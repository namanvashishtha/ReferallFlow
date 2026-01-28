from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from typing import Dict
from app.core.logging import get_logger

logger = get_logger("application_service")

# Use a simple file-system loader so templates can live in app/templates
env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_application_template(template_name: str, context: Dict) -> str:
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)
