from pymongo import MongoClient

uri = 'mongodb+srv://root:root1227@projetos.gbfgogr.mongodb.net/?retryWrites=true&w=majority&appName=Projetos'

client = MongoClient(uri)

db = client.challenge30
news = db['news']