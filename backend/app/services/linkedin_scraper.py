import asyncio
import random
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("linkedin_scraper")


class ScraperError(Exception):
    pass


class PoliteLinkedInScraper:
    def __init__(self, concurrency: int = None, proxies: Optional[List[str]] = None):
        self.concurrency = concurrency or settings.SCRAPER_CONCURRENCY
        self.semaphore = asyncio.Semaphore(self.concurrency)
        self.proxies = proxies or settings.PROXY_LIST
        self.client = httpx.AsyncClient(timeout=30)

    async def _fetch(self, url: str, proxy: Optional[str] = None) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            if proxy:
                # httpx requires proxies to be set at client initialization.
                # Since we want to rotate proxies, we use a temporary client for this request.
                async with httpx.AsyncClient(proxies=proxy, timeout=30) as client:
                    resp = await client.get(url, headers=headers)
                    resp.raise_for_status()
                    return resp.text
            else:
                resp = await self.client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.text
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error while fetching", url=url, status=e.response.status_code)
            raise ScraperError(str(e))
        except httpx.RequestError as e:
            logger.exception("Network error while fetching %s", url)
            raise

    async def search_jobs(self, query_urls: List[str], max_results: int = 10) -> List[dict]:
        """Search multiple LinkedIn job listing pages (or other job pages) and extract simple job metadata.

        IMPORTANT: This implementation does not log into LinkedIn and is intended for public job pages only.
        Use polite scraping configuration (delays, proxies) and respect robots.txt.
        """
        tasks = [self._scrape_job_page(url) for url in query_urls]
        results = []
        for coro in asyncio.as_completed(tasks):
            try:
                r = await coro
                if r:
                    results.extend(r)
            except Exception:
                logger.exception("Error scraping a page")
            if len(results) >= max_results:
                break
        return results[:max_results]

    async def _scrape_job_page(self, url: str) -> List[dict]:
        async with self.semaphore:
            # polite randomized delay derived from RATE_LIMIT_PER_MINUTE
            per_min = settings.RATE_LIMIT_PER_MINUTE or 60
            delay = random.uniform(0.5, max(1.0, 60.0 / float(per_min)))
            await asyncio.sleep(delay)
            proxy = random.choice(self.proxies) if self.proxies else None
            html = await self._fetch(url, proxy)
            return self._parse_job_listings(html, url)

    def _parse_job_listings(self, html: str, base_url: str) -> List[dict]:
        soup = BeautifulSoup(html, "lxml")
        jobs = []
        
        # Modern LinkedIn public job search selectors
        # They often use .base-card or .base-search-card
        cards = soup.select(".base-card, .base-search-card, .result-card, .job-card-list__entity, .jobs-search-results__list-item")
        
        for card in cards:
            # Title
            title_el = card.select_one(".base-search-card__title, .job-result-card__title, .job-card-list__title, h3")
            
            # Company
            company_el = card.select_one(".base-search-card__subtitle, .job-result-card__subtitle, .job-card-container__company-name, .hidden-nested-link")
            
            # Location
            location_el = card.select_one(".job-search-card__location, .job-result-card__location, .job-card-container__metadata-item")
            
            # Link
            link_el = card.select_one("a.base-card__full-link, a.result-card__full-link, a")
            
            if title_el:
                jobs.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "Unknown Company",
                    "location": location_el.get_text(strip=True) if location_el else "Remote",
                    "url": link_el["href"] if link_el and link_el.has_attr("href") else base_url,
                })
        
        if not jobs:
            logger.warning("No jobs parsed from HTML, selectors might be outdated or page structure changed.")
            
        return jobs

    async def close(self):
        await self.client.aclose()
