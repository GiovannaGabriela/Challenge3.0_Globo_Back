from datetime import datetime
from . import connection


def add_news(new):

    news = connection.news

    try:
        news.insert_one(new)
        return "Noticia adicionada."
    except:
        return "Erro ao adicionar noticia."