import boto3
import os
import uuid
import json


#https://towardsdatascience.com/speech-to-text-using-aws-transcribe-s3-and-lambda-a6e88fb3a48e
def lambda_handler(event, context):
    print (event)

    region_name = os.environ.get('ENV_REGION_NAME')
    transcribe = boto3.client('transcribe')
    OUTPUT_BUCKET_PREFIX = os.environ.get('OUTPUT_BUCKET_PREFIX')
    INPUT_BUCKET_PREFIX = os.environ.get('INPUT_BUCKET_PREFIX')


    for record in event['Records']:
        print("Event: ",event['Records'])

        #Leemos el archivo en S3


        record = event['Records'][0]
    
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']
        key = s3object.split("/")[-1]
        
        if INPUT_BUCKET_PREFIX in key:
    
            s3Path = "s3://" + s3bucket + "/" + s3object
            jobName = s3object + '-' + str(uuid.uuid4())

            print('Empieza la lectura de {}'.format(s3Path)) 

            #Transcribe APIs
            #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html#TranscribeService.Client.start_transcription_job
            
            response = transcribe.start_transcription_job(
            TranscriptionJobName=jobName,
            LanguageCode='es-ES',
            MediaFormat='mp4',
            Media={
                'MediaFileUri': s3Path
            },
            OutputBucketName = s3bucket, 
            OutputKey        = OUTPUT_BUCKET_PREFIX,
            Subtitles={
            'Formats': [
                'srt'
            ]}
            )

            TranscriptionJobName = response['TranscriptionJob']['TranscriptionJobName']
        
            print("Procesando....")
            print("TranscriptionJobName : {0}".format(TranscriptionJobName))


        else:
            TranscriptionJobName = " "
    


    return {
        'TranscriptionJobName': TranscriptionJobName
    }
    