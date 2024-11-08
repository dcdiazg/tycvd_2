"""Testing"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TEST_URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-active/"

TD_IDX_STOCK_NAME = 0
TD_IDX_STOCK_PRICE = 2
TD_IDX_STOCK_VOLUME = 4
TD_IDX_MARKET_CAP = 6
TD_IDX_SECTOR = -2

CSV_OUTPUT = Path(__file__).parent / "results.csv"
CSV_HEADER = ["Symbol", "Name", "Price", "Currency", "Volume", "Market Cap", "Sector"]


def test():
    res = requests.get(TEST_URL)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find_all("table")[0]
        print(">>>", table.get("class"))
        rows = table.find_all("tr")
        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            # Símbolo y nombre de la acción
            symbol = cells[TD_IDX_STOCK_NAME].find("a").text
            name = cells[TD_IDX_STOCK_NAME].find("sup").text
            # Precio y moneda de la acción
            price_raw, currency = cells[TD_IDX_STOCK_PRICE].text.split()
            price = float(price_raw.replace(",", ""))
            # Volumen de la acción
            volume = float(
                cells[TD_IDX_STOCK_VOLUME].text.removesuffix("M").removesuffix("K")
            )
            # Capitalización de mercado
            market_cap_raw, *_ = cells[TD_IDX_MARKET_CAP].text.split()
            market_cap = float(market_cap_raw)
            # Sector/es
            sector = cells[TD_IDX_SECTOR].text
            # Almacenar datos
            data.append((symbol, name, price, currency, volume, market_cap, sector))
    # Guardar datos en un CSV
    with open(CSV_OUTPUT, "w") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        writer.writerows(data)


if __name__ == "__main__":
    test()
    print("DONE")
