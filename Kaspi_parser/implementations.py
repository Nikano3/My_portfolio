

from abstracts import *


class OpenCategory(OpenCategoryAbstract):
    async def run(self, page, url, sem ):
        async with sem:
            await page.goto(url)
            await page.wait_for_selector('.current-location__dialog-list-link', timeout=30000)


class SetCity(SetCityAbstract):
    async def run(self, page, city):
        try:
            await page.click(f'text="{city}"')
            logger.debug(' SetCity: city selected')
        except Exception as e:
            logger.error(f'SetCity: error:{e}')

class ExtractLinks(ExtractLinksAbstract):

    async def run(self, page, sem):
        buttons = []

        while True:
            shops = 0
            try:
                async with sem:
                    while True:
                        await asyncio.sleep(0.3)
                        if not await page.query_selector('.item__price-heading'):

                            try:
                                await page.reload()
                            except PlaywrightTimeoutError:
                                await page.reload

                        else:
                            break
                logger.debug('ExtractLinks: shops found')
            except Exception as e:
                logger.error(f'ExtractLinks: erorr in found shops: {e}')
            try:
                if await page.query_selector('.rating-count'):
                    elements = await page.query_selector_all('td.sellers-table__cell')
                    for element in elements:
                        link = await element.query_selector('a')
                        if link:
                            name = await link.text_content()
                            href = await link.get_attribute('href')
                            shops += 1
                            if href:  # чтобы не было None
                                buttons.append({'url': href, 'name': name})

                next_btn = await page.query_selector('text="Следующая"')

                if not next_btn:
                    break
                if '_disabled' in await next_btn.get_attribute("class"):
                    break
                async with sem:
                    await page.wait_for_selector('text="Следующая"', timeout = 30000)
                    await asyncio.sleep(random.uniform(0.5, 1))
                    await page.click('text="Следующая"')
                logger.debug('buttons parsed')
            except Exception as e:
                logger.error(f'ExtractLinks error in the parsing buttons: {e}')

        return buttons


class GetUniqueLinks(GetUniqueLinks):

    async def run(self, buttons):
        unique_links = []
        seen_names = set()
        try:
            for btn in buttons:
                if btn['name'] not in seen_names:
                    try:
                        seen_names.add(btn['name'])
                        unique_links.append(btn)
                    except Exception as e:
                        logger.error(f' error Unique: {e}')
            logger.info(f'debug {len(unique_links)} shops')
        except Exception as e:
            logger.error(f'GetAtributeLinks error:{e}')
        return unique_links

class ParsingComps(ParsingCompsAbstract):
    async def run(self, context, info: dict, sem):

        url = info['url']
        city = info['city']
        category = info['category']

        if url.startswith("/"):
            url = "https://kaspi.kz" + url
        page = await context.new_page()

        try:
            async with sem:
                await page.goto(url)
                if await page.wait_for_selector('.current-location__dialog-list-link', timeout=10000):
                    await SetCity().run(page,city)

            await page.wait_for_selector('.merchant-profile__title', timeout=20000)

            company = await page.text_content(".merchant-profile__title")
            try:
                phone = await page.text_content(".merchant-profile__contact-text", timeout = 10000)
            except:
                phone = 'N/A'
            logger.debug('ParsingComps: successful')
        except Exception as e:
            logger.error(f'ParsingComps error:{e}')
        finally:
            try:
                if page:
                    await page.close()

            except Exception as e:
                logger.error(f'ParsingComps erorr in the page close: {e}')

        company_clean = company.split(' в')[0]
        category_clean = await ParsingCategory().run(category)
        result = {
            'company': company_clean,
            'city': city,
            'phone': phone,
            'url' : url ,
            'category': category_clean
        }
        logger.info(f'company {company_clean} are ready')
        return result

class SaveCompanies(SaveCompaniesAbstract):
    async def run(self, info):
        try:
            if isinstance(info, dict):
                info = [info]

            new_df = pd.DataFrame(info).rename(columns={
                'company': 'Компания',
                'city': 'Город',
                'phone': 'Телефон',
                'url': 'Сайт',
                'category': 'Категория'
            })

            file_path = 'database/companies.xlsx'

            # если файл уже есть — загружаем старые данные
            if os.path.exists(file_path):
                old_df = pd.read_excel(file_path)
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            try:
                combined_df = combined_df.drop_duplicates(subset=['Компания', 'Город'])

                combined_df.to_excel(file_path, index=False)

            except Exception as e:
                logger.error(f'ошибка в сейве компаний:{e}. в dict: {info}')

        except Exception as e:
            logger.error (f'ошибка в сейве компаний:{e}. в dict: {info}')
class Workers(WorkersAbstract):
    async def worker(self, queue, rate):
        results = []  # все результаты воркера
        while True:
            task = await queue.get()
            if task is None:
                queue.task_done()
                break

            try:
                result = await task

                if isinstance(result, list):
                    results.extend(result)
                elif isinstance(result, dict):
                    results.append(result)

            except Exception as e:
                logger.error(f"Worker error: {e}")
            finally:
                queue.task_done()


        return results  # весь список после завершения воркера
class ParsingCategory(ParsingCategoryAbstract):
    async def run(self, url: str):
        import urllib.parse

        CATEGORY_TRANSLATIONS = {
            'smartphones and gadgets': 'Смартфоны и гаджеты',
            'home equipment': 'Бытовая техника',
            'pharmacy': 'Аптека',
            'tv_audio': 'ТВ и аудио',
            'computers': 'Компьютеры',
            'furniture': 'Мебель',
            'beauty care': 'Уход и косметика',
            'child goods': 'Детские товары',
        }
        try:
            # часть после /c/
            part = url.split('/c/')[-1].strip('/')
            #  %20 -> пробел
            decoded = urllib.parse.unquote(part)
            # переводим, если есть в словаре
            return CATEGORY_TRANSLATIONS.get(decoded, decoded)
        except Exception:
            return 'Неизвестная категория'


class ParsingUrlsItems(ParsingUrlsItemsAbstract):
    async def run(self, page, sem, sheet):
        
        items = set()
        digit = 0
        if sheet != 0:
            await page.goto(page.url + f'?page={sheet}')
        while digit != 5:
            await asyncio.sleep(0.5)
            await page.wait_for_selector('.item-card__name-link', timeout=30000)

            links = await page.query_selector_all('.item-card__name-link')

            for link in links:
                href = await link.get_attribute("href")

                if href:
                    items.add(href)

            next_btn = await page.query_selector('text="Следующая →"')


            if not next_btn:
                break

            class_attr = await next_btn.get_attribute("class") or ""
            if '_disabled' in class_attr:
                break
            async with sem:

                await next_btn.click()

                await page.wait_for_load_state('domcontentloaded')
                await page.wait_for_selector('.item-card__name-link', timeout=10000)
                await asyncio.sleep(random.uniform(0.5, 0.9))

            digit += 1
            page_number = int(re.search(r'page=(\d+)', page.url).group(1)) if 'page=' in page.url else 1


        return {'items': list(items),
                'sheet': page_number }


class GetLastSheet(GetLastSheetAbstract):
    async def run(self, category = None):
        path = Path("database/last.json")
        if not path.exists():
            return None

        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return None
        if category:
            return data[category]['last']  # если весь JSON
        first_key = next(iter(data))  # 'smartphones'
        first_value = data[first_key]
        return first_value['last']
        # или data["last"], если там {"last": 10}


class Question(QuestionAbstract):
    async def run(self):
        choice = None
        while choice not in ('да', 'нет'):
            choice = input(f"Начать парсинг сначала (да/нет) ?  ").strip().lower()
        if choice == 'нет':
            return False
        elif choice == 'да':
            return True
        return None


class SaveLastSheet(SaveLastSheetAbstract):
    async def run(self, sheet: int, category):
        path = "database/last.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}

        data[category] = {"last": sheet}

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Ошибка при сохранении последней страницы: {e}")

