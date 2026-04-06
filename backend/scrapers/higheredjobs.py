"""HigherEdJobs scraper — specialized for university/academic positions."""
from backend.scrapers.base_scraper import BaseScraper


class HigherEdJobsScraper(BaseScraper):
    BASE_URL = "https://www.higheredjobs.com/search/advanced_action.cfm"

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
                url = f"{self.BASE_URL}?Keyword={keyword}&Remote=1&Remote=2&JobCat=19"
                await page.goto(url, timeout=30000)
                await page.wait_for_selector(".record-row", timeout=10000)
                html = await page.content()
                await browser.close()

            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select(".record-row")
            jobs = []
            for row in rows[:20]:
                title_el = row.select_one("a.job-title")
                inst_el = row.select_one(".col-employer")
                loc_el = row.select_one(".col-location")
                href = title_el["href"] if title_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.higheredjobs.com" + href
                jobs.append(self._normalize({
                    "title": title_el.text if title_el else "",
                    "description": inst_el.text if inst_el else "",
                    "location": loc_el.text if loc_el else "",
                    "url": href,
                }))
            return jobs
        except Exception as e:
            print(f"HigherEdJobs scraper error: {e}")
            return []
