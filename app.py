from flask import Flask, Blueprint, jsonify, render_template
from sqlalchemy import Column, Integer, String, JSON, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import requests
from bs4 import BeautifulSoup
import os


# 1. Конфигурация
class Config:
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@db/scraping_db"


# 2. Инициализация базы данных
DATABASE_URL = "postgresql://user:password@db/scraping_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def init_db():
    """Создаем все таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)


# 3. Модели
class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)


# 4. Scraper (для парсинга данных)
def scrape_quotes():
    """Скрейпинг цитат с сайта"""
    url = "http://quotes.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    quotes = []
    for quote_block in soup.select('.quote'):
        text = quote_block.select_one('.text').get_text(strip=True)
        author = quote_block.select_one('.author').get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in quote_block.select('.tag')]
        quotes.append({"text": text, "author": author, "tags": tags})

    return quotes


# 5. Роуты
api = Blueprint('api', __name__)

@api.route('/')
def index():
    """Маршрут для отображения цитат на главной странице"""
    session = Session()
    quotes = session.query(Quote).all()
    result = [{"text": q.text, "author": q.author, "tags": q.tags} for q in quotes]
    session.close()
    return render_template('index.html', quotes=result)

@api.route('/scrape', methods=['GET'])
def scrape():
    """Маршрут для парсинга цитат и сохранения их в базу данных"""
    session = Session()
    scraped_data = scrape_quotes()

    for data in scraped_data:
        if not session.query(Quote).filter_by(text=data["text"]).first():
            quote = Quote(**data)
            session.add(quote)

    session.commit()
    session.close()
    return jsonify({"message": "Data scraped and saved!"})


# 6. Основная логика приложения Flask
def create_app():
    """Функция для создания Flask приложения"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация базы данных
    init_db()

    # Регистрация маршрутов
    app.register_blueprint(api)

    return app


# 7. Запуск приложения
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
