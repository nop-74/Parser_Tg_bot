from sqlalchemy import Column
from sqlalchemy.orm import Mapped

from bot.db_config.config import Base, DecimalField


class ResultParser(Base):
    tg_id: Mapped[int]
    title: Mapped[str]
    url: Mapped[str]
    xpath: Mapped[str]
    price = Column(DecimalField(50))
