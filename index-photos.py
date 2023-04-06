import json
import boto3
import time
import requests

ES_HOST = 'https://search-photos-r7vcovxedl22yzbs5f3gv3snba.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'

def get_url(index, type):
    url = ES_HOST + '/' + index + '/' + type
    return url

def lambda_handler(event, context):
    print("hi")
    print("event: ", event)
    jsonBody = event['Records'][0]
    bucketName = jsonBody['s3']['bucket']['name']
    key = jsonBody['s3']['object']['key']
    reko = boto3.client('rekognition')
    s3 = boto3.client('s3')
    print("key" , key)
    try:
        data = {}
        responses3 = s3.head_object(Bucket = bucketName, Key =key )
        print("responses3: ", responses3)
        
        response = reko.detect_labels(
            Image={'S3Object': {'Bucket': bucketName, 'Name': key}})
        print("response: ", response)
        data['objectKey'] = key
        data['bucket'] = bucketName
        data['createdTimestamp'] = time.time()
        data['labels'] = []
        print(responses3)
        if not responses3['Metadata'] =={}:
            customlabel = responses3['Metadata']['customlabels']
            if customlabel != "":
                data['labels'] = [i.strip() for i in customlabel.split(",")]
        
        for label in response['Labels']:
            if label['Confidence'] > 95:
                data['labels'].append(label['Name'])
        print("***********",data['labels'])
        body = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        esUrl = get_url('photos', 'Photo')
        r = requests.post(url=esUrl,auth = ('photos-user', 'Kushaal@26'), data=body, headers=headers)
        print(body,"******",r)
    except Exception as e:
        print("Error " + str(e))

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }