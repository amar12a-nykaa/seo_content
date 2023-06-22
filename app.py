from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_restful import Resource, reqparse
import pymongo

app = Flask(__name__)
api = Api(app)


class SeoContent(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('query', type=str, required=True, default='nykaa')

	def post(self):
		data = SeoContent.parser.parse_args()
		print(data)
		content = {"Name": "Amar", "comp": "hack"}
		return {"status": "Success", "content": content}

api.add_resource(SeoContent, "/seo/data")


if __name__ == "__main__":
	app.run(debug=True, port=2023)
