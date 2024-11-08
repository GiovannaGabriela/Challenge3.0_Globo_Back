from . import connection


def get_news():

    news = connection.news
    return news.find({}, {"_id": 0})


def get_len_news():

    return connection.news