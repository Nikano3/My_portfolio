import asyncio
from playwright.async_api import async_playwright
import logging


class Kufar():
    async def for_kufar(self, page):
        self.page = page
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
                        result = {"Дата": date_text,
                                  'Ссылка': href,
                                  'Адрес': ", ".join(addr_text.split(", ")[:3]),
                                  'Описание': title_text,
                                  'Цена': price_text.split('.')[0]}
                        print(3)
                        return result
            return None

        htmls = await asyncio.gather(*(ad.inner_html() for ad in main))
        results = await asyncio.gather(*(parse(ad) for ad in main))
        results_one = [result for result in results if result is not None]

        if results_one:
            print(f"Найдено {len(results_one)} объявлений")  # Логируем количество найденных объявлений
            return results_one
        else:
            print("Объявления не найдены")  # Логируем, если объявления не были найдены
            return None


class Realt():
    pass


class Gohome():
    pass


class Running(Kufar, Realt, Gohome):
    async def running(self):
        self.results = []
        self.urls = [
            'https://re.kufar.by/l/polock/snyat/kvartiru-dolgosrochno?blc=v.or%3A1&cur=USD&rms=v.or%3A2%2C3&size=30',
            'https://re.kufar.by/l/novopolock/snyat/kvartiru-dolgosrochno?blc=v.or%3A1&cur=USD&rms=v.or%3A2%2C3&size=30'
        ]
        self.sites = ['kufar', 'realt', 'gohome']
        for url in self.urls:
            page1 = await self.pages(url)
            for site in self.sites:
                if site.lower().strip() in url:
                    if 'kufar' in site:
                        print('переход в функцию куфар')
                        self.results.append(await self.for_kufar(page1))
                    if 'realt' in site:
                        self.results.append(await self.for_realt(page1))
                    if 'gohome' in site:
                        self.results.append(await self.for_gohome(page1))
                    self.urls.remove(url)
        if self.results:
            return self.results


class Browser(Running):
    def __init__(self):
        self.chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'

    async def start(self, p):
        self.browser = await p.chromium.launch(executable_path=self.chrome_path, headless=True)
        ret = await self.running()
        await self.stop()
        return ret

    async def stop(self):
        if self.browser:
            await self.browser.close()

    async def pages(self, url):
        if self.browser:
            self.page = await self.browser.new_page()
            await self.page.goto(url)
            return self.page

    async def main(self):
        print(1)
        async with async_playwright() as p:
            endl = await self.start(p)
            print(endl)
            return endl
