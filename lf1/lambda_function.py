import json
import boto3
import requests
from datetime import *
import urllib.parse

from requests_aws4auth import AWS4Auth

credentials = boto3.Session().get_credentials()
ES_HOST = 'ES HOST'
REGION = 'REGION'


s3 = boto3.client('s3')
rekognition = boto3.client("rekognition", region_name = "REGION")

def lambda_handler(event, context):
    print("Integrating code to CodeBuild!")

    headers = { "Content-Type": "application/json" }    

    # TODO implement
    custom_labels = None
    for record in event['Records']:
    # record = event['Records'][0]['s3']
        bucket = record['s3']['bucket']['name']
        photo = record['s3']['object']['key']
        try:
            custom_labels = s3.head_object(Bucket=bucket, Key=photo)["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-customlabels"]
            print("Custom labels", custom_labels)
        except Exception as e:
            print(e)
        res = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            MaxLabels=10)
            
        # print(res)
        # print("The response is: ", res)
        obj = {}
        obj['objectKey'] = photo
        obj["bucket"] = bucket
        obj["createdTimestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        obj["labels"] = []
        
        for label in res['Labels']:
            obj["labels"].append(label['Name'].lower())
        for elm in custom_labels.split(","):
            obj["labels"].append(elm.strip().lower())
        
        print(obj)
        # url = get_url('photos')    
        req = requests.post(ES_HOST, json=obj, auth=("USER","PASS"))
        print(req.text)
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            'Content-Type': 'application/json'
        },
        'body': json.dumps("Image labels have been successfully detected!")
    }
