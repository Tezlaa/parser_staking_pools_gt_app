import os
import time
import asyncio

import schedule

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from telegram import Bot

from dotenv import load_dotenv


load_dotenv()


PERCENT_NOTIFICATION = 98
SCHEDULE_INTERVAL_IN_MINUTES = 3
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


def firefox_options() -> webdriver.FirefoxOptions:
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
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


def parser_percents(page_source: str) -> list[int]:
    soup = BeautifulSoup(page_source, 'html.parser')
    elements_with_percent = soup.find_all('div', {'class': 'w-full bg-level-two p-5 rounded space-y-4'})
    elements = []
    for element in elements_with_percent:
        percent = element.find('div', class_='text-primary').text
        if '%' in percent:
            elements.append(int(percent.replace('%', '')))
    return elements


def is_send_message(percents: list[int]) -> bool:
    return any(percent >= PERCENT_NOTIFICATION for percent in percents)


def send_telegram_message(message: str) -> None:
    async def send(message: str) -> None:
        await Bot(TELEGRAM_TOKEN).sendMessage(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    asyncio.run(send(message))


def main() -> None:
    url = 'https://staking.gt-protocol.io/'
    driver = loadpage(url, 10)
    percents = parser_percents(driver.page_source)
    if is_send_message(percents):
        percent_text = [
            f"{'🟢' if percent >= PERCENT_NOTIFICATION else '🟠'} №{i} - {percent}%"
            for i, percent in enumerate(percents, start=1)
        ]
        message = (
            f'❗Has percent that more than {PERCENT_NOTIFICATION}% ❗\n\n'
            f'Percents: \n{"\n".join(percent_text)}'
        )
        send_telegram_message(message=message)
    driver.quit()


if __name__ == '__main__':
    try:
        schedule.every(SCHEDULE_INTERVAL_IN_MINUTES).minutes.do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except BaseException as e:
        send_telegram_message(message=f'⚠️ Error: {e}')
        raise e
