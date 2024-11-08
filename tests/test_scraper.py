"""Testing"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from source import StockScraper

if __name__ == "__main__":
    scraper = StockScraper()
    # scraper.choose_countries(output_dir=r"C:\Users\angel\Playground", verbose=True)
    scraper.scrape(
        "",
        loops=1,
        verbose=True,
    )
