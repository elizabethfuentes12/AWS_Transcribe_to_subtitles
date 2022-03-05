import boto3
import os
import uuid
import json


#https://towardsdatascience.com/speech-to-text-using-aws-transcribe-s3-and-lambda-a6e88fb3a48e
def lambda_handler(event, context):
    print (event)

    region_name = os.environ.get('ENV_REGION_NAME')
    SOURCE_LANG_CODE = os.environ.get('SOURCE_LANG_CODE')
    OutputBucketName = os.environ.get('OutputBucketName')
    transcribe = boto3.client('transcribe')



    for record in event['Records']:
        print("Event: ",event['Records'])
        record = event['Records'][0]
    
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']
        
        s3Path    = "s3://" + s3bucket + "/" + s3object
        jobName   = s3object + '-' + str(uuid.uuid4())
        OutputKey = s3object.replace(".mp4","")+"/"+SOURCE_LANG_CODE+"_"+s3object

        print('Empieza la lectura de {}'.format(s3Path)) 
        #Leemos el archivo en S3        
    
        s3Path = "s3://" + s3bucket + "/" + s3object
        jobName = s3object + '-' + str(uuid.uuid4())

        print('Empieza la lectura de {}'.format(s3Path)) 

        #Transcribe APIs
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/transcribe.html#TranscribeService.Client.start_transcription_job
        
        response = transcribe.start_transcription_job(
            TranscriptionJobName=jobName,
            LanguageCode= SOURCE_LANG_CODE,
            MediaFormat='mp4',
            Media={
            'MediaFileUri': s3Path
            },
            OutputBucketName = OutputBucketName,
            OutputKey=OutputKey.replace(".mp4",""), 
            Subtitles={
            'Formats': [
                'srt'
            ]}
            )

        TranscriptionJobName = response['TranscriptionJob']['TranscriptionJobName']
    
        print("Procesando....")
        print("TranscriptionJobName : {}".format(TranscriptionJobName))

    
    return True
    
    