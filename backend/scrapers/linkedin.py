"""LinkedIn job scraper using Playwright + BeautifulSoup."""
from backend.scrapers.base_scraper import BaseScraper


class LinkedInScraper(BaseScraper):
    BASE_URL = "https://www.linkedin.com/jobs/search"

    async def scrape(self) -> list[dict]:
        results = []
        for keyword in self.keywords:
            jobs = await self._scrape_keyword(keyword)
            results.extend(jobs)
        return results

    async def _scrape_keyword(self, keyword: str) -> list[dict]:
        try:
            from playwright.async_api import async_playwright
            from bs4 import BeautifulSoup

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                url = f"{self.BASE_URL}?keywords={keyword}&location={self.location}"
                await page.goto(url, timeout=30000)
                await page.wait_for_selector(".job-search-card", timeout=10000)
                html = await page.content()
                await browser.close()

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".job-search-card")
            jobs = []
            for card in cards[:20]:  # limit per keyword
                title_el = card.select_one(".base-search-card__title")
                company_el = card.select_one(".base-search-card__subtitle")
                location_el = card.select_one(".job-search-card__location")
                link_el = card.select_one("a.base-card__full-link")
                jobs.append(self._normalize({
                    "title": title_el.text if title_el else "",
                    "description": company_el.text if company_el else "",
                    "location": location_el.text if location_el else "",
                    "url": link_el["href"] if link_el else "",
                }))
            return jobs
        except Exception as e:
            print(f"LinkedIn scraper error: {e}")
            return []
