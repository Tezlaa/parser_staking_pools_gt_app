import schedule

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


PERSENT_NOTIFICATION = 98


def firefox_options() -> webdriver.FirefoxOptions:
    options = webdriver.FirefoxOptions()
    return options


def loadpage(url: str, delay: int) -> webdriver.Firefox:
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options())
    driver.get(url)
    WebDriverWait(driver, delay).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'img[data-testid="staking-icon-img"]')
        )
    )
    return driver


def parser_persents(page_source: str) -> list[int]:
    soup = BeautifulSoup(page_source, 'html.parser')
    elements_with_persent = soup.find_all('div', {'class': 'w-full bg-level-two p-5 rounded space-y-4'})
    elements = []
    for element in elements_with_persent:
        persent = element.find('div', class_='text-primary').text
        if '%' in persent:
            elements.append(int(persent.replace('%', '')))
    return elements


def is_send_message(persents: list[int]) -> bool:
    return any(persent >= PERSENT_NOTIFICATION for persent in persents)


def send_telegram_message(message: str) -> None:


if __name__ == '__main__':
    url = 'https://staking.gt-protocol.io/'
    driver = loadpage(url, 10)
    persents = parser_persents(driver.page_source)
    if is_send_message(persents):
        send_telegram_message(message=f'Persent: {persents}')
    driver.quit()
