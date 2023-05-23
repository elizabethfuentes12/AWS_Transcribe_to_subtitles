from aws_cdk import (
    Duration, RemovalPolicy,
    Stack,
    aws_iam,
    aws_s3 as s3,
    aws_s3_notifications,
    aws_sns as sns,
    aws_lambda,
    aws_sns_subscriptions as subscriptions,
    aws_lambda_event_sources
)
from constructs import Construct

class CdkCodeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        REGION_NAME = 'us-east-1'
        email="YOUR-EMAIL"
        SOURCE_LANG_CODE = 'es-ES'
        TARGET_LANG_CODE = 'en-US'

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++Creamos el data bucket +++++++++++++++++++++++++++++++
        #El cual sera el encargado de almacenar los videos a escanear.+++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        BUCKET_NAME       = "video-bucket"
        INPUT_BUCKET  = "input_transcribe"
        OUTPUT_BUCKET = "output_transcribe"

        bucket1 = s3.Bucket(self, BUCKET_NAME ,  versioned=False, removal_policy=RemovalPolicy.DESTROY)
        bucket2 = s3.Bucket(self, INPUT_BUCKET ,  versioned=False, removal_policy=RemovalPolicy.DESTROY)
        bucket3 = s3.Bucket(self, OUTPUT_BUCKET ,  versioned=False, removal_policy=RemovalPolicy.DESTROY)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++     Creamos el work bucket +++++++++++++++++++++++++++
        #++El cual sera el encargado de almacenar la traduccion.++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++The Lambda function invokes Amazon Rekognition for content moderation on videos ++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_invokes_transcribe= aws_lambda.Function(self, "lambda_invokes_transcribe",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda que invoca Amazon transcribe",
                                    code = aws_lambda.Code.from_asset("./lambda_invokes_transcribe"),
                                    environment = {
                                        'ENV_REGION_NAME'  : REGION_NAME,
                                        "OutputBucketName" : bucket2.bucket_name,
                                        "SOURCE_LANG_CODE" : SOURCE_LANG_CODE}
                                        
                                    )

        lambda_invokes_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["transcribe:*"], 
                resources=['*'])
              )
        

        # Permiso para leer y escribir en S3 y se agrega el evento que la activara 
        bucket1.grant_read_write(lambda_invokes_transcribe) 
        bucket2.grant_read_write(lambda_invokes_transcribe) 
        notification = aws_s3_notifications.LambdaDestination(lambda_invokes_transcribe)
        bucket1.add_event_notification(s3.EventType.OBJECT_CREATED, notification) 
    
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++The Lambda function invokes Amazon translate +++++++++++++++++++++++++++++++ ++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_process_transcribe= aws_lambda.Function(self, "lambda_process_transcribe",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda que procesa el SRT entregado por amazon transcribe y traduce su contenido",
                                    code = aws_lambda.Code.from_asset("./lambda_process_transcribe"),
                                    environment = {
                                        'ENV_REGION_NAME': REGION_NAME,
                                        "OutputBucketName" : bucket3.bucket_name,
                                        "SOURCE_LANG_CODE" : SOURCE_LANG_CODE[0:2],
                                        "TARGET_LANG_CODE" : TARGET_LANG_CODE[0:2]
                                        }
                                    )
                
        lambda_process_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["translate:*"], 
                resources=['*'])
              )

        bucket2.grant_read_write(lambda_process_transcribe) 
        notification2 = aws_s3_notifications.LambdaDestination(lambda_process_transcribe)
        bucket2.add_event_notification(s3.EventType.OBJECT_CREATED, notification2) 
        bucket3.grant_read_write(lambda_process_transcribe) 


