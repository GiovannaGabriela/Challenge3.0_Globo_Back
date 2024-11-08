from . import connection


def deleteNew(id):

    news = connection.news
    result = news.delete_one({"id": id})
