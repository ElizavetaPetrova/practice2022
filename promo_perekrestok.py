from datetime import datetime
from decimal import Decimal
from re import sub
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base

PRODUCT_URL = "https://www.perekrestok.ru/cat/d?"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
}

page = requests.get(url=PRODUCT_URL, headers=headers)
soup = BeautifulSoup(page.content, "lxml")
paging = soup.find(class_="rc-pagination pagination").find_all("a")
start_page = paging[1].text
last_page = 1
# last_page = paging[len(paging)-2].text - номер последней страницы каталога с акциями
pages = list(range(1, int(last_page) + 1))

for page in pages:
    url = 'https://www.perekrestok.ru/cat/d?page=%s' % (page)
    page = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")

    titles = soup.find_all(class_="product-card__title")
    prices = soup.find_all(class_="price-new")

product_titles = list(map(lambda x: x.text, titles))
product_prices = list(map(lambda x: float(x.text.replace('\xa0₽', '').replace(',', '.')), prices))
product_price_int = list(map(int, product_prices))

# SQLALCHEMY
Base = declarative_base()


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    datetime = Column(DateTime)
    price = Column(String(64))
    price_int = Column(Numeric(10, 2))

    def __repr__(self):
        return f"{self.name} | {self.price}"


engine = create_engine("sqlite:///database_promo.sqlite")
Base.metadata.create_all(engine)
session = Session(bind=engine)

for i in range(len(product_titles)):
    session.add(
        Price(name=product_titles[i],
              price=product_prices[i],
              datetime=datetime.now(),
              price_int=product_price_int[i]
              )
    )
session.commit()
