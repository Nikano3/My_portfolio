import asyncio
from playwright.async_api import async_playwright
import logging


'''class Browser:
    


    async def stop(self):
        if self.browser:
            await self.browser.close()

    async def pages(self, url):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(executable_path=self.chrome_path, headless=True)
            print("Браузер запущен")
            if self.browser:
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                await self.page.goto(url)
                '''
class Kufar():
    async def for_kufar(self):
        main = await self.page.query_selector_all('section')

        async def parse(ad):
            date = await ad.query_selector('.styles_date__ssUVP')
            if date:
                date_text = await date.inner_text()
                if date_text.lower().split(',')[0] == 'сегодня' or date_text.lower().split(',')[0] == 'вчера':
                    title = await ad.query_selector('.styles_parameters__7zKlL')
                    price = await ad.query_selector('.styles_price__gpHWH')
                    addr = await ad.query_selector('.styles_address__l6Qe_')
                    ssilka = await ad.query_selector('.styles_wrapper__Q06m9')
                    href = await ssilka.get_attribute('href')
                    if title and price:
                        title_text = await title.inner_text()
                        price_text = await price.inner_text()
                        addr_text = await addr.inner_text()
                        result = f"Дата: {date_text}\nСсылка:{href}\nАдрес: {", ".join(addr_text.split(", ")[:3])}\nОписание: {title_text}\nЦена: {price_text.split('.')[0]}\n-----------------------------------------------------------------"
                        return result
            return None

        htmls = await asyncio.gather(*(ad.inner_html() for ad in main))
        results = await asyncio.gather(*(parse(ad) for ad in main))
        results_one = [result for result in results if result is not None]

        if results_one:
            return results_one


class Realt():
    pass


class Gohome():
    pass


class Running(Kufar, Realt, Gohome):
    def __init__(self):
        self.chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
    async def pages(self, url):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(executable_path=self.chrome_path, headless=True)
            print("Браузер запущен")
            if self.browser:
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                await self.page.goto(url)
                self.results = await asyncio.gather(self.for_kufar())
    async def running(self):

        self.urls = [
            'https://re.kufar.by/l/polock/snyat/kvartiru-dolgosrochno?blc=v.or%3A1&cur=USD&rms=v.or%3A2%2C3&size=30',
            'https://re.kufar.by/l/novopolock/snyat/kvartiru-dolgosrochno?blc=v.or%3A1&cur=USD&rms=v.or%3A2%2C3&size=30'
        ]
        self.sites = ['kufar', 'realt', 'gohome']
        for url in self.urls:
            await self.pages(url)
            '''for site in self.sites:
                if site.lower().strip() in url:
                    if 'kufar' in site:
                        results = await asyncio.gather(self.for_kufar())
                    if 'realt' in site:
                        results = await asyncio.gather(*(self.for_realt()))
                    if 'gohome' in site:
                        results = await asyncio.gather(*(self.for_gohome()))'''
            end = [result for sublist in self.results for result in sublist]
            if end:
                return end



async def main():
    running = Running()
    results = await running.running()
    if results:
        print(results)

# Запуск программы
asyncio.run(main())