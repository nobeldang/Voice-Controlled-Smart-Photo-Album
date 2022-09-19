import json
import json
import boto3
import requests
from datetime import *
import urllib.parse


ES_HOST = 'ES HOST'
REGION = 'REGION'
S3_URL = 'S3 URL'
def get_url(keyword):
    url = ES_HOST + keyword.lower()
    return url


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin":"*",
            "Access-Control-Allow-Credentials" : True,
        },
    }
    


def lambda_handler(event, context):
	headers = { "Content-Type": "application/json" }
	lex = boto3.client('lex-runtime')
	query = event["queryStringParameters"]["q"]
	lex_response = lex.post_text(
		botName='BOT NAME',
		botAlias='ALIAS',
		userId='USER ID',
		inputText=query
	)
	
	print("LEX RESPONSE --- {}".format(json.dumps(lex_response)))

	slots = lex_response['slots']

	img_list = []
	labels_list = []
	for i, tag in slots.items():
		if tag:
			url = get_url(tag)
			print("ES URL --- {}".format(url))

			es_response = requests.get(url, headers=headers, auth=("USER","PASS")).json()
			print("ES RESPONSE --- {}".format(json.dumps(es_response)))

			es_src = es_response['hits']['hits']
			print("ES HITS --- {}".format(json.dumps(es_src)))

			for photo in es_src:
				labels = [word.lower() for word in photo['_source']['labels']]
				objectKey = photo['_source']['objectKey']
				print("Labels print:", labels)
				labels_list.append(labels)
				img_list.append(objectKey)
	print("Images ", img_list)
	

	results = []
	for i, l in zip(img_list, labels_list):
		results.append({"url": S3_URL + i, "labels": l})
	print(results)
	response = {"results": results}
	return respond(None, response)