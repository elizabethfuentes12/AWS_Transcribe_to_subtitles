import boto3
import os
import uuid
import json


#https://towardsdatascience.com/speech-to-text-using-aws-transcribe-s3-and-lambda-a6e88fb3a48e
def lambda_handler(event, context):
    print (event)

    region_name = os.environ.get('ENV_REGION_NAME')
    OUTPUT_BUCKET_PREFIX = os.environ.get('OUTPUT_BUCKET_PREFIX')
    INPUT_BUCKET_PREFIX = os.environ.get('INPUT_BUCKET_PREFIX')


    for record in event['Records']:
        print("Event: ",event['Records'])

        #Leemos el archivo en S3


        record = event['Records'][0]
    
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']
        key = s3object.split("/")[-1]
        
        if OUTPUT_BUCKET_PREFIX in key:

            print('Archivo listo {}'.format(s3Path))
    
            s3Path = "s3://" + s3bucket + "/" + s3object
            jobName = s3object + '-' + str(uuid.uuid4())

            print('Empieza la lectura de {}'.format(s3Path)) 

            
    


    return {
        True
    }
    