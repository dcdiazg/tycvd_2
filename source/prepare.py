# 05/11/2024
"""Módulo para preparación de datos descargables"""

from pathlib import Path

import toml
from more_itertools import chunked
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

CONFIG_FILE = Path(__file__).parent.parent / "config.toml"


def setup() -> WebDriver:
    """Define el WebDriver a utilizar en función de la configuración asignada"""
    config = toml.load(CONFIG_FILE)
    # Local o mediante 'webdriver-manager'
    local = bool(config["webdriver"].get("local", False))
    # Generando el WebDriver
    choice = config["webdriver"]["driver"]
    if not local:
        if choice == "chrome":
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
            )
        elif choice == "chromium":
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.os_manager import ChromeType

            options = Options()
            options.add_argument("--headless=new")
            driver = webdriver.Chrome(
                service=Service(
                    ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
                ),
                options=options,
            )
        elif choice == "edge":
            from selenium.webdriver.edge.service import Service
            from webdriver_manager.microsoft import EdgeChromiumDriverManager

            driver = webdriver.Edge(
                service=Service(EdgeChromiumDriverManager().install())
            )
        elif choice == "firefox":
            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import GeckoDriverManager

            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    # Devolviendo el WebDriver
    return driver


def prepare():
    """Preparar datos descargables"""
    driver = setup()
    driver.get("https://www.tradingview.com/markets/stocks-usa/market-movers-active/")
    driver.implicitly_wait(10)
    # Clicamos el botón de "US stocks", que nos lleva a un menú para seleccionar países
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    target = [button for button in all_buttons if button.text == "US stocks"][0]
    target.click()
    # Ubicamos el menú y recogemos el continent, país, y URL a su mercado
    driver.implicitly_wait(5)
    dialog = driver.find_element(By.XPATH, "//div[starts-with(@class, 'dialog-')]")
    content = dialog.find_element(By.XPATH, "./div/div[3]")
    for continent_div, countries_div in chunked(
        content.find_elements(By.XPATH, "./div")[1:], 2
    ):
        continent = continent_div.text.title()
        for country_item in countries_div.find_elements(By.TAG_NAME, "a"):
            country, url = country_item.text.split("\n")[0], country_item.get_attribute(
                "href"
            )
            token = url.split("/")[-3]
            print(f">>> {continent} | {country} | {token}")
