# AGENTS.md

## What this is
CDK (Python) app that generates subtitles for MP4 videos: an upload to the input S3 bucket triggers Amazon Transcribe, a second Lambda converts the SRT and translates it with Amazon Translate into the target language bucket.

## Structure
- `CDK_code/app.py` – CDK entrypoint (`CdkCodeStack`).
- `CDK_code/cdk_code/cdk_code_stack.py` – 3 S3 buckets, 2 Lambda functions, S3 event notifications, IAM policies. Language codes (`SOURCE_LANG_CODE`, `TARGET_LANG_CODE`) are constants at the top of the file.
- `CDK_code/lambda_invokes_transcribe/lambda_function.py` – starts the Transcribe job (SRT output).
- `CDK_code/lambda_process_transcribe/lambda_function.py` – reads the SRT, translates each cue, writes the translated SRT.
- `CDK_code/cdk.out/` – committed synth output from 2023 (build artifact; safe to regenerate/remove).

## Commands
```bash
cd CDK_code
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cdk synth          # needs the CDK CLI: npm install -g aws-cdk
cdk deploy         # creates real AWS resources (S3, Lambda, IAM)
```

## Dependencies
- `aws-cdk-lib==2.277.0`, `constructs>=10,<11`, CDK CLI 2.x.
- Lambda runtime: **Python 3.13** (`aws_lambda.Runtime.PYTHON_3_13`). Handlers only use `boto3` from the runtime, no layers.
- AWS credentials with permissions for S3, Lambda, IAM, Transcribe, Translate.

## Conventions / gotchas
- The stack is environment-agnostic (no `env=` in `app.py`); region for the Transcribe client comes from `ENV_REGION_NAME`.
- Transcribe limits: MP4 up to 2 GB.
- Do not hardcode new model/service identifiers without checking the official docs.

## Recent changes
- 2026-11: Lambda runtime `python3.8` (deprecated 2024-10-14) -> `python3.13`; `aws-cdk-lib` 2.15.0 -> 2.277.0. Verified with `cdk synth` (all functions render `python3.13`) and by importing both handlers under Python 3.13. Not deployed.
