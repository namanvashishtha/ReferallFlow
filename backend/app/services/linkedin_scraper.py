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
            "User-Agent": "Mozilla/5.0 (compatible; ReferralForgeBot/1.0; +https://example.com/bot)"
        }
        proxies = None
        if proxy:
            proxies = {
                "http://": proxy,
                "https://": proxy,
            }
        try:
            resp = await self.client.get(url, headers=headers, proxies=proxies)
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
        # Simple heuristics for LinkedIn-like job cards
        for card in soup.select(".result-card, .job-card-list__entity, .jobs-search-results__list-item"):
            title = card.select_one(".job-result-card__title, .job-card-list__title")
            company = card.select_one(".job-result-card__subtitle, .job-card-container__company-name")
            location = card.select_one(".job-result-card__location, .job-card-container__metadata-item")
            link = card.select_one("a")
            jobs.append({
                "title": title.get_text(strip=True) if title else None,
                "company": company.get_text(strip=True) if company else None,
                "location": location.get_text(strip=True) if location else None,
                "url": link["href"] if link and link.has_attr("href") else base_url,
            })
        return jobs

    async def close(self):
        await self.client.aclose()
