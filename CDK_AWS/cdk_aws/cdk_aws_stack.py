from aws_cdk import (
    core,
    aws_iam,
    aws_s3 as s3,
    aws_s3_notifications,
    aws_sns as sns,
    aws_lambda,
    aws_sns_subscriptions as subscriptions,
    aws_lambda_event_sources
    )


class CdkAwsStack(cdk.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        REGION_NAME = 'us-east-1'
        email="elizabethfuentes12@gmail.com"

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++Creamos el data bucket +++++++++++++++++++++++++++++++
        #El cual sera el encargado de almacenar los videos a escanear.+++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        BUCKET_NAME        = "video-bucket"
        INPUT_BUCKET_PREFIX  = "input_transcribe"
        OUTPUT_BUCKET_PREFIX = "output_transcribe"

        bucket1 = s3.Bucket(self, BUCKET_NAME ,  versioned=False, removal_policy=core.RemovalPolicy.DESTROY)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++     Creamos el work bucket +++++++++++++++++++++++++++
        #++El cual sera el encargado de almacenar la traduccion.++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++ Crear el topic SNS +++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_sns/Topic.html
        #https://pypi.org/project/aws-cdk.aws-sns-subscriptions/

        my_topic_email = sns.Topic(self, "my_topic_email",
                        display_name="Customer subscription topic")
        my_topic_email.add_subscription(subscriptions.EmailSubscription(email))
        SNS_ARN_email = my_topic_email.topic_arn


        my_topic_transcribe = sns.Topic(self, "my_topic_transcribe",
                        display_name="transcribe subscription topic")
        SNS_ARN_transcribe=my_topic_transcribe.topic_arn

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #+++++++++++++++++++++++++++++++++++ Role Rekognition para poder publicar en SNS ++++++++++++++++++++++++
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        transcribeServiceRole = aws_iam.Role( self, "TranscribeServiceRole", assumed_by=aws_iam.ServicePrincipal('transcribe.amazonaws.com'))
        transcribeServiceRole.add_to_policy(
            aws_iam.PolicyStatement(
                actions=["sns:Publish"], 
                resources=[my_topic_transcribe.topic_arn])
                )

        SNS_ROLE_ARN_TRANS = transcribeServiceRole.role_arn

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++The Lambda function invokes Amazon Rekognition for content moderation on videos ++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_invokes_transcribe= aws_lambda.Function(self, "lambda_invokes_transcribe",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = core.Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda que invoca Amazon transcribe",
                                    code = aws_lambda.Code.asset("./lambda_invokes_transcribe"),
                                    environment = {
                                        'ENV_REGION_NAME': REGION_NAME,
                                        'ENV_SNS_ARN': SNS_ARN_email,
                                        'ENV_SNS_TRANSCRIBE': SNS_ARN_transcribe,
                                        "ENV_SNS_ROLE_ARN_TRANS":SNS_ROLE_ARN_TRANS,
                                        "OUTPUT_BUCKET_PREFIX":OUTPUT_BUCKET_PREFIX,
                                        "INPUT_BUCKET_PREFIX":INPUT_BUCKET_PREFIX}
                                    )

        lambda_invokes_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["transcribe:*"], 
                resources=['*'])
              )
        
        lambda_invokes_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["sns:*"], 
                resources=['*']))

        lambda_invokes_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions =['iam:PassRole'],
                resources =[transcribeServiceRole.role_arn]  
            )
        )

        #Permiso para leer y escribir en S3 y se agrega el evento que la activara 
        bucket1.grant_read_write(lambda_invokes_transcribe) 
        notification = aws_s3_notifications.LambdaDestination(lambda_invokes_transcribe)
        bucket1.add_event_notification(s3.EventType.OBJECT_CREATED, notification) 

        #Permiso para enviar email con SNS
        my_topic_email.grant_publish(lambda_invokes_transcribe)


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #++++++++++The Lambda function invokes Amazon transcribe for content moderation on videos ++++++++++++++++
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        lambda_process_transcribe= aws_lambda.Function(self, "lambda_process_transcribe",
                                    handler = "lambda_function.lambda_handler",
                                    timeout = core.Duration.seconds(300),
                                    runtime = aws_lambda.Runtime.PYTHON_3_8,
                                    memory_size = 256, description = "Lambda que procesa Amazon transcribe ",
                                    code = aws_lambda.Code.asset("./lambda_process_transcribe"),
                                    environment = {
                                        'ENV_REGION_NAME': REGION_NAME,
                                        'ENV_SNS_ARN': SNS_ARN_email,
                                        'OUT_BUCKET': out_bucket}
                                    )
        

        lambda_process_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["out_bucket:*"], 
                resources=['*']))

        lambda_process_transcribe.add_to_role_policy(
            aws_iam.PolicyStatement(
                actions=["sns:*"], 
                resources=['*']))
        
        #Permiso para escribir en la tabla
        
        my_topic_transcribe.add_subscription(subscriptions.LambdaSubscription(lambda_process_transcribe))


