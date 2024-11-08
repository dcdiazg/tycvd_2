"""Testing"""

from source import StockScraper

if __name__ == "__main__":
    scraper = StockScraper()
    scraper.scrape("", verbose=True)
