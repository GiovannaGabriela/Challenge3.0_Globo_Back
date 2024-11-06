from . import connection


def get_news():

    news = connection.news

    return news.find({}, {"_id": 0})


