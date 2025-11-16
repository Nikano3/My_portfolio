from implementations import *

settings = Settings()


class Parsing(ParsingAbstract):
    def __init__(self, cities, rate_limit, get_sheet, open_category, set_city, parsing_items, save_last_page, extract_links):
        self.rate_limit = rate_limit
        self.cities = cities
        self.get_sheet = get_sheet
        self.open_category = open_category
        self.set_city = set_city
        self.parsing_items = parsing_items
        self.save_last_page = save_last_page
        self.extract_links = extract_links

    async def run(self, browser, category, city_index, items: int):
        urls = []
        companies = 0
        current_index = 0
        context = await browser.new_context()
        page = await context.new_page()
        city = self.cities[city_index]
        sheet = await self.get_sheet.run(category)
        await self.open_category.run(page, category, self.rate_limit)
        await self.set_city.run(page, city)
        cards = await self.parsing_items.run(page, self.rate_limit, sheet)
        product = cards['items']
        sheet = cards['sheet'] + 1
        logger.info(f'{len(product)}, {category}')
        while companies < items:
            if current_index == len(product):
                cards = await self.parsing_items.run(page, self.rate_limit, sheet)
                product = cards['items']
                sheet = cards['sheet']
                current_index = 0
            try:
                async with self.rate_limit:
                    url = 'https://kaspi.kz' + product[current_index]
                    await page.goto(url, timeout=60000)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
            except Exception as e:
                logger.error(f'error in Parsing: {e}')
            links = await self.extract_links.run(page, self.rate_limit)
            for link in links:
                urls.append({'url': link['url'], 'city': city, 'category': category, 'name': link['name'] })

            companies += len(links)
            current_index += 1

        if current_index != 0:

            sheet_temp = (current_index // 12) * 12
            sheet = (sheet_temp // 12) + 1

            if sheet == 1:
                sheet = 0

        await self.save_last_page.run(sheet, category)
        await page.close()
        await context.close()

        if len(urls) > items:
            urls = urls[:items]
        return urls


class StartParsingCompanies(StartParsingCompaniesAbstract):
    def __init__(self, parser, workers):
        self.parser = parser
        self.workers = workers

    async def run(self, urls, context, sem):
        queue = asyncio.Queue()
        workers = Workers()

        for url in urls:
            coro = self.parser.run(context, url, sem)
            await queue.put(coro)

        worker_tasks = [asyncio.create_task(workers.worker(queue, self.workers)) for _ in range(self.workers)]

        for _ in range(self.workers):
            await queue.put(None)

        results = await asyncio.gather(*worker_tasks)
        return results


class Main(MainAbstract):
    def __init__(self):
        self.rate_limit_urls = asyncio.Semaphore(settings.rate_limit_urls)
        self.rate_limit_comps = asyncio.Semaphore(settings.rate_limit_urls)
        self.workers = settings.workers
        self.categories = settings.categories
        self.cities = settings.cities

        self.get_sheet = GetLastSheet()
        self.open_category = OpenCategory()
        self.set_city = SetCity()
        self.parsing_items = ParsingUrlsItems()
        self.save_last_page = SaveLastSheet()
        self.extract_links = ExtractLinks()
        self.question = Question()
        self.parser = Parsing(self.cities, self.rate_limit_urls, self.get_sheet, self.open_category, self.set_city,
                              self.parsing_items, self.save_last_page, self.extract_links)
        self.parsing_comps = StartParsingCompanies(ParsingComps(), self.workers)
        self.save_comps = SaveCompanies()
        self.get_unique_links = GetUniqueLinks()

    async def main(self, items: int):
        queue = asyncio.Queue()
        workers = Workers()

        async with async_playwright() as p:

            try:
                choice = True
                sheet = await self.get_sheet.run()

                if sheet != 0:
                    choice = await self.question.run()

                browser = await p.chromium.launch(headless=True)

                for category in self.categories:
                    for city_index, _ in enumerate(self.cities):

                        if choice:
                            await self.save_last_page.run(0, category)
                        coro = self.parser.run(browser, category, city_index, round(items / 8))
                        await queue.put(coro)

                worker_tasks = [asyncio.create_task(workers.worker(queue, self.workers)) for _ in range(self.workers)]

                for _ in range(self.workers):
                    await queue.put(None)

                all_results_lists = await asyncio.gather(*worker_tasks)
                end_urls= list(item for sublist in all_results_lists for item in sublist)
                end_urls = await self.get_unique_links.run(end_urls)

                logger.info(f' awdawdaw {len(end_urls)}')
                comps = await self.parsing_comps.run(end_urls, browser, self.rate_limit_comps)
                all_comps = [company for sublist in comps for company in sublist]
                await self.save_comps.run(all_comps)

            except Exception as e:
                logger.error(f'Main error: {e}')

            finally:
                await browser.close()


if __name__ == "__main__":
    main_app = Main()
    start_time = time.time()
    asyncio.run(main_app.main(settings.products))
    end_time = time.time()
    total = end_time - start_time
    logger.info(f"\n⏱ Время выполнения: {int(total // 60)} минут {int(total % 60)} секунд")