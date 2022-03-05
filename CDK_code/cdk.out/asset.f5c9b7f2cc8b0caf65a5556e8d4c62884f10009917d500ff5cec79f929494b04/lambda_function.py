import boto3
import os


client_s3 = boto3.client('s3')
translate_client = boto3.client('translate')

region_name = os.environ.get('ENV_REGION_NAME')
OutputBucketName = os.environ.get('OutputBucketName')
sourceLanguage = os.environ['SOURCE_LANG_CODE']
targetLanguage= os.environ['TARGET_LANG_CODE']

def to_translate(text):
    traducido = translate_client.translate_text( Text=text, SourceLanguageCode=sourceLanguage, TargetLanguageCode=targetLanguage)['TranslatedText']
    print("Text translate")
    return traducido

def put_file(filename, bucket, key):
    with open(filename, "rb") as data:
        client_s3.upload_fileobj(data,bucket, key+filename)
        print("put_file in s3://{}{}{}".format(bucket,key,filename))
    return True

def lambda_handler(event, context):
    print (event)

    for record in event['Records']:
        print("Event: ",event['Records'])
        record = event['Records'][0]
    
        s3bucket = record['s3']['bucket']['name']
        s3object = record['s3']['object']['key']
        filename = s3object.split("/")[-1]
        key = s3object.split("/")[0]+"/"
        srt_file_out = targetLanguage + "_" + filename

        with open(filename) as f:
            str = f.readlines()

        traslate_out=[]
        for lines in str:
            lines_traducido=to_translate(lines)
            traslate_out.append(lines_traducido)
     
        with open(srt_file_out, 'w') as temp_file:
            for item in traslate_out:
                temp_file.write(item)

        put_file(srt_file_out, OutputBucketName, key)
    
    return True
