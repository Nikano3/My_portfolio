from abc import ABC, abstractmethod
from log import get_logger
from typing import List, Dict
import random
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import pandas as pd
import os
import asyncio
import re
from implementations import *
from playwright.async_api import async_playwright
import asyncio
import time
from tqdm import tqdm

from config import Settings
import json
from pathlib import Path

from log import get_logger
logger = get_logger(level="INFO", log_file="logs/my_logs.log")

class ParsingCompsAbstract(ABC) :
    @abstractmethod
    async def run(self, context, info, sem) -> List[Dict]:
        pass

class ParsingAbstract(ABC):
    @abstractmethod
    async def run(self, browser, category, city_index, items: int) -> List:
        pass

class MainAbstract(ABC):
    @abstractmethod
    async def main(self, items: int) -> None:
        pass

class OpenCategoryAbstract(ABC) :
    @abstractmethod
    async def run(self, page, url, sem ) -> None:
        pass

class SetCityAbstract(ABC):
    @abstractmethod
    async def run(self, page, city) -> None:
        pass

class ExtractLinksAbstract(ABC):
    @abstractmethod
    async def run(self, page, sem) -> List:
        pass

class GetUniqueLinks(ABC) :

    @abstractmethod
    async def run(self, links) -> List:
        pass




class StartParsingCompaniesAbstract(ABC):
    @abstractmethod
    async def run(self, urls, context, sem) -> List[Dict]:
        pass


class SaveCompaniesAbstract(ABC):
    @abstractmethod
    async def run(self, info) -> None:
        pass

class WorkersAbstract(ABC):
    @abstractmethod
    async def worker(self, queue, rate) -> List:
        pass

class ParsingCategoryAbstract(ABC):
    @abstractmethod
    async def run(self, url: str):
        pass

class ParsingUrlsItemsAbstract(ABC):
    @abstractmethod
    async def run(self, page, sem, sheet) -> Dict:
        pass

class GetLastSheetAbstract(ABC):
    @abstractmethod
    async def run(self,category) -> int:
        pass

class QuestionAbstract(ABC):
    @abstractmethod
    async def run(self) -> bool:
        pass

class SaveLastSheetAbstract(ABC):
    @abstractmethod
    async def run(self, sheet, category) -> None:
        pass