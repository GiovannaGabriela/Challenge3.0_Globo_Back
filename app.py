import json
from flask import Flask, request
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from unicodedata import category

from bd import add_news, get_news, delete_new
import PIL
from senha import geminiapi
import google.generativeai as genai

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

# configuração do gemini
genai.configure(api_key=geminiapi)
model = genai.GenerativeModel("gemini-1.5-flash")

users = {
    "admin": {"password": "admin"},
}

@auth.verify_password
def verify_password(username, password):
    return username if username in users and users[username]["password"] == password else None



class News(Resource):

    def post(self): # Post direto pelo site

        from datetime import datetime

        data = request.get_json()

        len_news = get_news.get_len_news().count_documents({})

        if len(data) == 1:

            chat = model.start_chat(history=[])

            analise = chat.send_message(f"Analise a mensagem se pode ser uma mensagem verdadeira ou não: \n{data['info']}. Retorne apenas 'Não.' ou 'Possivel Sim.'. Retorne 'Não.' em caso de mensagens de cunho sexual.")

            print(analise.text)

            if analise.text.strip() == 'Possivel Sim.':

                motivo = chat.send_message(f"me fale o que o usuário quer informar na mensagem anterior, separe a mensagem em: titulo, localização, categoria (você vai identificar), imagem (caso tenha imagem, veja se consegue identificar a origem da imagem) e descrição. Retorne um json já tratado apenas do que foi pedido. {data['info']}")

                print(motivo.text)

                motivo = motivo.text
                motivo = motivo.replace('json', '')
                motivo = motivo.replace('```', '')
                motivo = motivo.replace('\n', '')

                informacao = json.loads(motivo)

                new = {
                    "id": len_news + 1,
                    "title": informacao['titulo'],
                    "location": informacao['localização'],
                    "category": informacao['categoria'],
                    "image": informacao['imagem'],
                    "description": informacao['descrição']
                }

                today = datetime.today()

                new["date"] = today.strftime("%d/%m/%Y")
                new["time"] = today.strftime("%H:%M")

                print(new)

                try:
                    add_news.add_news(new)
                    return {"message": "Noticia adicionada com sucesso."}, 200
                except Exception as e:
                    return {"message": f"Erro ao adicionar notícia: {str(e)}"}, 500


            if analise.text.strip() == 'Não.':

                motivo = chat.send_message("Por que?")
                return motivo.text


        if len(data) >= 3:

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
                "id": len_news + 1,
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
                "id": new["id"],
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
    def get(self):

        return {"message": "Acesso autorizado para admin."}


    @auth.login_required
    def delete(self):

        data = request.get_json()

        deleted_new = delete_new.deleteNew(int(data['id']))

        return {"message": "Noticia apagada com sucesso."}




api.add_resource(News, '/news')
api.add_resource(AdminNews, '/news/admin')


if __name__ == "__main__":
    app.run(debug=True)