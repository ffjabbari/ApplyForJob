"""Indeed job scraper."""
from backend.scrapers.base_scraper import BaseScraper


class IndeedScraper(BaseScraper):
    BASE_URL = "https://www.indeed.com/jobs"

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
                url = f"{self.BASE_URL}?q={keyword}&l={self.location}"
                await page.goto(url, timeout=30000)
                await page.wait_for_selector(".job_seen_beacon", timeout=10000)
                html = await page.content()
                await browser.close()

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".job_seen_beacon")
            jobs = []
            for card in cards[:20]:
                title_el = card.select_one("h2.jobTitle span")
                company_el = card.select_one("[data-testid='company-name']")
                location_el = card.select_one("[data-testid='text-location']")
                link_el = card.select_one("h2.jobTitle a")
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.indeed.com" + href
                jobs.append(self._normalize({
                    "title": title_el.text if title_el else "",
                    "description": company_el.text if company_el else "",
                    "location": location_el.text if location_el else "",
                    "url": href,
                }))
            return jobs
        except Exception as e:
            print(f"Indeed scraper error: {e}")
            return []
