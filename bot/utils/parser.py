import re
import pandas as pd
import aiohttp
from decimal import Decimal
from loguru import logger
from bs4 import BeautifulSoup
from lxml import html
from typing import BinaryIO

from bot.schemas.result import InfoParser
from bot.dao.result_parser import ResultParserDAO
from bot.db_config.config import async_session_maker


def read_excel_file(file: BinaryIO) -> pd.DataFrame:
    df = pd.read_excel(file, engine="openpyxl")
    required_columns = ['title', 'url', 'xpath']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Неправильный формат файла!")
    return df


class Parser:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
        "DNT": "1"
    }


    def __init__(self, tg_id: int):
        self.tg_id = tg_id

    async def __get_page(self, url: str) -> BeautifulSoup:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                page = BeautifulSoup(await response.text(), "html.parser")
                return page


    @staticmethod
    def __formated_price(elem: str) -> str:
        price_pattern = r"""
            (?:-?\$?\s*)?
            (            
                \d{1,3}
                (?:[\s.,]?\d{3})*
                (?:[.,]\d+)?
            )
            (?:\s*€?| руб.?)?
        """
        matches = re.findall(price_pattern, elem, re.VERBOSE)
        if not matches:
            raise ValueError("Цена не найдена в тексте")
        price_str = matches[-1].replace(' ', '').replace(',', '.')
        if '.' in price_str and ',' not in price_str:
            price_str = price_str.replace('.', '')
        elif ',' in price_str and '.' in price_str:
            price_str = price_str.replace('.', '').replace(',', '.')
        return price_str


    def __parse_page(self, page: BeautifulSoup, elem: str) -> Decimal:
        try:
            dom = html.fromstring(str(page))
            finding_elem = dom.xpath(elem)[0]
            price = self.__formated_price(finding_elem.text)
            return Decimal(price)
        except ValueError as e:
            logger.error(e)
            raise


    async def parse_df(self, df: pd.DataFrame, save_db: bool = False) -> list[InfoParser]:
        results = []
        for row in df.itertuples():
            page = await self.__get_page(row.url)
            price = self.__parse_page(page, row.xpath)
            info = InfoParser(
                tg_id=self.tg_id,
                title=row.title,
                url=row.url,
                xpath=row.xpath,
                price=price,
            )
            results.append(info)
        if save_db:
            async with async_session_maker() as session:
                dao_obj = ResultParserDAO(session)
                await dao_obj.add_many(results)
                await session.commit()
        return results
