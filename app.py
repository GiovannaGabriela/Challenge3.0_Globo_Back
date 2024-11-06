import json
from flask import Flask, request
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from bd import add_news, get_news

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


users = {
    "admin": {"password": "admin_pass", "role": "admin"},
    "visitante": {"password": "visitante_pass", "role": "visitante"},
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username]["password"] == password:
        return username
    return None


def role_required(role):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            username = auth.current_user()
            user_role = users.get(username, {}).get("role")
            if user_role != role:
                return {"message": "Acesso negado!"}, 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class News(Resource):

    def post(self):

        from datetime import datetime

        data = request.get_json()

        if not data:
            return {"message": "Nenhum dado foi enviado."}, 400

        title = data.get('title', "").strip()
        location = data.get('location', "").strip()
        category = data.get('category', "").strip()
        image = data.get('image')
        description = data.get('description', "").strip()

        if not title or not location or not category:
            return {"message": "Preencha todos os campos obrigatórios: título, localização e categoria."}, 400

        new = {
            "title": title,
            "location": location,
            "category": category,
            "image": image,
            "description": description
        }
        today = datetime.today()

        new["date"] = today.strftime("%d/%m/%Y")
        new["time"] = today.strftime("%H:%M")

        try:
            add_news.add_news(new)
            return {"message": "Noticia adicionada com sucesso."}, 200
        except Exception as e:
            return {"message": f"Erro ao adicionar notícia: {str(e)}"}, 500

    def get(self):

        title = request.args.get("title")
        location = request.args.get("location")
        category = request.args.get("category")
        date = request.args.get("date")

        try:

            news = get_news.get_news()

            if title:
                news = [new for new in news if new["title"].lower() == title.lower()]
            if location:
                news = [new for new in news if new["location"].lower() == location.lower()]
            if category:
                news = [new for new in news if new["category"].lower() == category.lower()]
            if date:
                news = [new for new in news if new["date"].lower() == date.lower()]

            return [{
                "title": new["title"],
                "location": new["location"],
                "category": new["category"],
                "image": new["image"],
                "description": new["description"],
                "date": new["date"],
                "time": new["time"]
            } for new in news], 200


        except Exception as e:
            return {"message": f"Erro ao obter as noticias: {str(e)}"}, 500


class AdminNews(Resource):
    @auth.login_required
    @role_required('admin')
    def get(self):
        return {"message": "Acesso autorizado para admin."}


api.add_resource(News, '/news')
api.add_resource(AdminNews, '/news/admin')


if __name__ == "__main__":
    app.run(debug=True)