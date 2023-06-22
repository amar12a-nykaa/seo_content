from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_restful import Resource, reqparse
import requests
import random
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)
model = "gpt-35-turbo"
east_us_api_base_url = f"https://nykaa-openai-eastus.openai.azure.com"
api_key = "5f8ff2383c6e4ad7a9091e6a9c6c83a1"
chat_completion_api = f"{east_us_api_base_url}/openai/deployments/{model}/chat/completions?api-version=2023-05-15&api-key={api_key}"
headers = {
    'api-key': api_key,
    'Content-Type': 'application/json'
}

primary_keywords = []
keyword_count = 5
system_message = "You are a beauty content generator for nykaa.com"
user_message = "Generate content for Maybelline New York beauty brand"
ai_message = f"""Maybelline New York
Maybe she’s born with it, maybe she’s Maybelline! A brand which launched women from sidewalk to catwalk, Maybelline is a brand that enhances the beauty that oozes from a lady of class, to even a college going lass. Luxurious textures that spell gorgeous and are within affordability, Maybelline is what makes you effortlessly beautiful, every day.

Maybelline New York Products Online at Nykaa
Get your skin and makeup mates, as Maybelline New York is aboard on Nykaa. Online shopping is just at your fingertips, as you peruse the much loved brand, and pick and choose your favourite products. The colours of the season or textures that are revolutionary, Maybelline and Nykaa have joined hands to give you the best of both worlds. From the latest launches like Maybelline New York Colossal Kajal Super Black, to the beloved bestsellers like, Maybelline The Colossal Liner – Black, Maybelline New York White Super Fresh Compact, Maybelline Color Show Lipstick, Maybelline Color Sensational Velvet Matte Lipstick, Maybelline New York The Nudes Eyeshadow Palette, Maybelline The Colossal Kajal 12 Hour Smudge Free - Black, Maybelline Baby Lips Color Balm and many more. From the foundation that aces your base makeup, to the rich kajal and eyeliners that define your eyes, to the lip colours of varied hues, and nail paints to suit every mood, Maybelline has a lot to offer, online at Nykaa.

So ladies, play up your features, with the widest range of makeup and beauty products online, all at the comfort of your home, with Nykaa’s huge range of cosmetics online. Shop online with at Nykaa, with our super easy checkout process, safe payment gateways, and trusted delivery partners that make sure, that you get the best of original and authentic products, in the quickest time possible, and in the best condition. Our offers give you the most authentic makeup products online at best prices. To ease your shopping experience even more, we offer you Cash on Delivery option, to pay for the product when it reaches your doorstep. Enjoy seamless online shopping experience at Nykaa, the best cosmetic store in India, and your one stop online destination for beauty."""

def get_response_from_chat_completion_api(url, headers, data):
  temperature = random.uniform(1.0, 2.0)  
  url = url+ f"&temperature={temperature}"
  response = requests.post(url, headers=headers, json=data)
  return response.json()

def get_assistance_data(system_message=system_message, user_message=user_message, ai_message=ai_message):
  return {
    "messages": [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content":user_message
        },
        {
            "role": "assistant",
            "content": ai_message
        }
    ]
}

def get_keyword_message(keyword_message):
  return {
    "messages": [
        {
            "role": "user",
            "content": keyword_message
        }
    ]
  }

def process_primary_keywords(primary_keywords_response):
    primary_keywords_list = primary_keywords_response['choices'][0]['message']['content']
    primary_keywords_list = primary_keywords_list.split('\n')
    processed_primary_keywords = [keyword[3:] for keyword in primary_keywords_list ]
    primary_keywords_str = ' ,'.join(processed_primary_keywords)
    return primary_keywords_str

def generate_content(input_message):
	assistance_data = get_keyword_message(input_message)
    # Perform cURL call to Azure Chat Completion API
	completion_response = get_response_from_chat_completion_api(chat_completion_api, headers, assistance_data)
	return completion_response	

def get_sub_heading_count(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    subheadings = soup.find_all('h2')
    count = len(subheadings)
    return count
class SeoContent(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('query', type=str, required=True, default='nykaa')
	parser.add_argument('heading_max_wc', type=int, required=False, default=200)
	parser.add_argument('sub_heading_max_wc', type=int, required=False, default=400)
	parser.add_argument('sub_heading_count', type=int, required=False, default=1)
	parser.add_argument('use_primary_keyword', type=bool, required=False, default=False)

	def post(self):
		data = SeoContent.parser.parse_args()
		query = data.get("query")
		heading_max_wc = data.get("heading_max_wc")
		sub_heading_max_wc = data.get("sub_heading_max_wc")
		sub_heading_count = data.get("sub_heading_count")
		use_primary_keyword = data.get("use_primary_keyword")
		heading_count = 1
		input_message = f"Generate html document with exactly {heading_count} heading having length of heading's content or heading's description length less than <= {heading_max_wc} words and {sub_heading_count} subheading having length of subheading's content or subheading's description length less than <= {sub_heading_max_wc} words for {query} and replace duplicate with synonyms or similar words. Use keywords or words that are most relevant to search volume at google.\If you do not identify any beauty brand in the {query} then show some suggestions of top beauty brands relevant to {query} and available at nykaa.com. \Remove any NOTE if present.**Generated Content should be in html format only."
		actual_subheading_count = 0
		primary_keyword_message = f"get top {keyword_count} keywords for {query} that are most relevant to search volume at google"
		while(actual_subheading_count!=sub_heading_count):
			response = generate_content(input_message)
			response = response['choices'][0]['message']['content']
			actual_subheading_count = get_sub_heading_count(response)
		
		if use_primary_keyword:
			primary_keywords_str = ""
			primary_assiatnce_messgae = get_keyword_message(primary_keyword_message)
			primary_keywords_response = get_response_from_chat_completion_api(chat_completion_api, headers, primary_assiatnce_messgae)
			if primary_keywords_response and primary_keywords_response.get('choices'):
				primary_keywords_str = process_primary_keywords(primary_keywords_response)
			if primary_keywords_str:
				primary_keyword_prompt = f"get crispy .html content with heading related to beauty ecommerce site which include {primary_keywords_str} words. Content should be less than 100 words"
				primary_keywords_content = get_response_from_chat_completion_api(chat_completion_api, headers, get_keyword_message(primary_keyword_prompt))
				if primary_keywords_content:
					final_message = f"merge content {response} and {primary_keywords_content} and generate a html format document"
					response = get_response_from_chat_completion_api(chat_completion_api, headers, get_keyword_message(final_message))
					response = response['choices'][0]['message']['content']
		input = ""
		for k,v in data.items():
			input+=" |"+str(k)+": "+str(v)+"| "
		print(type(data))
		response=response.replace("\n","<br />\n")
		return {"status": "Success"+input, "content": response}
class ProvideAssistance(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('system_message', type=str, required=False, default=system_message)
	parser.add_argument('user_message', type=str, required=False, default=user_message)
	parser.add_argument('ai_message', type=str, required=False, default=ai_message)

	def post(self):
		data = ProvideAssistance.parser.parse_args()
		system_message = data.get("system_message")
		user_message = data.get("user_message")
		ai_message = data.get("ai_message")
		# Perform cURL call to Azure Chat Completion API
		assistance_data = get_assistance_data(system_message, user_message, ai_message)
		completion_response = get_response_from_chat_completion_api(chat_completion_api, headers, assistance_data)
		if completion_response:
			content = {"status": "Success", "content": completion_response}
			return content 
		else:
			return {"status": "Failure", "Message": "Issue occured while making call"}

api.add_resource(ProvideAssistance, "/api/provide_assistance")
api.add_resource(SeoContent, "/seo/data")


if __name__ == "__main__":
	app.run(debug=True, port=2023)
