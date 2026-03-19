import httpx
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from auditeo_ai.models import FactualMetrics, HeadingCounts, LinkCounts
from auditeo_ai.utils import generate_url


class AuditeoScraperToolInput(BaseModel):
    """
    Input of the scraper tool
    """

    website_url: str = Field(description="The URL of the website to scrape")


class AuditeoScraperToolOutput(BaseModel):
    """
    Output of the scraper tool
    """

    factual_metrics: FactualMetrics = Field(description="Factual metrics of the page")
    page_content: str = Field(description="Raw HTML content of the page")
    page_content_clean: str = Field(description="Clean text content of the page")


class AuditeoScraperTool(BaseTool):
    name: str = "auditeo_web_scraper"
    description: str = "Scrapes a URL and returns structured factual metrics."
    args_schema: type[BaseModel] = AuditeoScraperToolInput

    def _run(self, website_url: str) -> str:
        """
        Executes the scrape and returns the Pydantic model as a JSON string.
        """
        try:
            website_url = generate_url(website_url)

            headers = {"User-Agent": "Auditeo/1.0 (Auditeo Internal Tool)"}
            response = httpx.get(
                website_url, headers=headers, follow_redirects=True, timeout=15
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text = soup.get_text(separator=" ")
            words = [w for w in text.split() if len(w) > 1]

            images = soup.find_all("img")
            img_count = len(images)
            missing_alt = len(
                [
                    img
                    for img in images
                    if not img.get("alt") or img.get("alt").strip() == ""
                ]
            )
            alt_pct = (missing_alt / img_count * 100) if img_count > 0 else 0.0

            from urllib.parse import urlparse

            domain = urlparse(website_url).netloc
            all_links = soup.find_all("a", href=True)
            internal = 0
            external = 0
            for a in all_links:
                href = a["href"]
                if href.startswith("/") or domain in href:
                    internal += 1
                elif href.startswith("http"):
                    external += 1

            ctas = soup.find_all(
                ["button", "a"],
                class_=lambda x: (
                    x
                    and any(
                        word in x.lower()
                        for word in ["btn", "button", "cta", "signup", "contact"]
                    )
                ),
            )

            m_desc = soup.find("meta", {"name": "description"})

            clean_text = soup.get_text(separator=" ", strip=True)
            pretty_html = soup.prettify()

            metrics = FactualMetrics(
                total_word_count=len(words),
                heading_counts=HeadingCounts(
                    h1=len(soup.find_all("h1")),
                    h2=len(soup.find_all("h2")),
                    h3=len(soup.find_all("h3")),
                ),
                cta_count=len(ctas),
                link_counts=LinkCounts(internal=internal, external=external),
                image_count=img_count,
                images_missing_alt_text_pct=alt_pct,
                meta_title=soup.title.string.strip() if soup.title else None,
                meta_description=m_desc["content"].strip() if m_desc else None,
            )

            output = AuditeoScraperToolOutput(
                factual_metrics=metrics,
                page_content=pretty_html,
                page_content_clean=clean_text,
            )

            return output.model_dump_json(indent=2)

        except Exception as e:
            return f"Error scraping {website_url}: {str(e)}"
