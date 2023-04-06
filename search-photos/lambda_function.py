import json
import boto3
import os
import sys
import uuid
import time
from botocore.vendored import requests

ES_HOST = 'https://search-photos-r7vcovxedl22yzbs5f3gv3snba.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'

def get_url(es_index, es_type, keyword):
    url = ES_HOST + '/' + es_index + '/' + es_type + '/_search?q=' + keyword.lower()
    return url

def lambda_handler(event, context):
	print("hi")
	print("hi2")

	print("EVENT --- {}".format(json.dumps(event)))
	
	headers = { "Content-Type": "application/json" }
	lex = boto3.client('lex-runtime')
    
	query = event["queryStringParameters"]["q"]
	
	print("query: ", query)
	lex_response = lex.post_text(
		botName='PhotoAlbum',
		botAlias='photoalbum',
		userId='kelly',
		inputText=query
	)
	
	print("LEX RESPONSE --- {}".format(json.dumps(lex_response)))

	slots = lex_response['slots']
	print("slots: ", slots)

	img_list = []
	for i, tag in slots.items():
		if tag:
			if tag[-1] == '.':
				tag = tag[:len(tag)-1]
			url = get_url('photos', 'Photo', tag)
			print("ES URL --- {}".format(url))

			es_response = requests.get(url, auth=("photos-user", "Kushaal@26")).json()
			print("ES RESPONSE --- {}".format(json.dumps(es_response)))

			es_src = es_response['hits']['hits']
			print("ES HITS --- {}".format(json.dumps(es_src)))

			for photo in es_src:
				print(photo)
				labels = [word.lower() for word in photo['_source']['labels']]
				if tag in labels:
					print(tag)
					objectKey = photo['_source']['objectKey']
					img_url = 'https://s3.amazonaws.com/photos-bucket-1/' + objectKey
					img_list.append(img_url)
	
	img_list = list(set(img_list))
	print(img_list)

	if img_list:
		return {
			'statusCode': 200,
			'headers': {
				"Access-Control-Allow-Origin": "*",
				'Content-Type': 'application/json'
			},
			'body': json.dumps(img_list)
		}
	else:
		return {
			'statusCode': 200,
			'headers': {
				"Access-Control-Allow-Origin": "*",
				'Content-Type': 'application/json'
			},
			'body': json.dumps("No such photos.")
		}