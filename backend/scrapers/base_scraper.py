"""Base scraper interface — all scrapers implement this."""
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, domain: str, keywords: list[str], location: str = ""):
        self.domain = domain
        self.keywords = keywords
        self.location = location

    @abstractmethod
    async def scrape(self) -> list[dict]:
        """Return list of job dicts: title, description, location, url, posted_date"""
        pass

    def _normalize(self, raw: dict) -> dict:
        return {
            "title": raw.get("title", "").strip(),
            "description": raw.get("description", "").strip(),
            "location": raw.get("location", "").strip(),
            "url": raw.get("url", "").strip(),
            "posted_date": raw.get("posted_date"),
        }
