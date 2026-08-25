# sam cli doesn`t start properly pls use aws-cli only for infratrsuture ready deployment

aws configure

aws sts get-caller-identity 

$REGION = "ap-south-1"

$BUCKET = "beam-calculator-pranjal-2026-unique"

# Create the bucket 
aws s3api create-bucket `
    --bucket $BUCKET `
    --REGION $region `
    --create-bucket-configuration LocationConstraint=$REGION 

# Enable server-side encryption 
aws s3api put-bucket-encryption `
    --bucket $BUCKET `
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Block public access 
aws s3api put-public-access-block `
    --bucket $BUCKET `
    --public-access-block-configuration `
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Create the lambda role 
aws iam create-role `
    --role-name beam-calculator-lambda-role `
    --assume-role-policy-document file://deployment/lambda-trust-policy.json

# Attach CloudWatch logging permissions 
aws iam attach-role-policy `
    --role-name beam-calculator-lambda-role `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attaching the S3 bucket to IAM policy
aws iam put-role-policy `
    --role-name beam-calculator-lambda-role `
    --policy-name BeamCalculatorS3WritePolicy `
    --policy-document file://deployment/s3-write-policy.json

# Get your AWS account ID: 

$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# Your role ARN will be 

$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# Create the build directory for lambda deployment 

New-Item -ItemType Directory -Force deployment\lambda-package

# Copy only the backend code 

Copy-Item core deployment\lambda-package\core -Recurse -Force

Copy-Item api deployment\lambda-package\api -Recurse -Force

# Package the Lambda: From the project root 

Compress-Archive `
    -Path deployment\lambda-package\* `
    -DestinationPath deployment\beam-calculator-lambda.zip `
    -Force

# Create the lambda function 

aws lambda create-function `
    --function-name beam-calculator-api `
    --runtime python3.12 `
    --role $ROLE_ARN `
    --handler api.lambda_handler.lambda_handler `
    --zip-file fileb://deployment/beam-calculator-lambda.zip `
    --timeout 15 `
    --memory-size 256 `
    --environment "Variables={CALCULATION_BUCKET=$BUCKET}" `
    --region $REGION

# Invoking the lambda function for testing the json function 

aws lambda invoke `
    --function-name beam-calculator-api `
    --payload fileb://deployment/test-event.json `
    --cli-binary-format raw-in-base64-out `
    --region $REGION `
    deployment\lambda-response.json

# View the response 

Get-Content deployment\lambda-response.json

# Check the calculation was saved 

aws s3 ls "s3://$BUCKET/calculations/" --recursive

# Create API gateway HTTP API 

$API_ID = aws apigatewayv2 create-api `
    --name beam-calculator-http-api `
    --protocol-type HTTP `
    --cors-configuration AllowOrigins='*',AllowMethods='POST,OPTIONS',AllowHeaders='Content-Type' `
    --region $REGION `
    --query ApiId `
    --output text

# Get the lambda ARN:

$LAMBDA_ARN = aws lambda get-function `
    --function-name beam-calculator-api `
    --region $REGION `
    --query Configuration.FunctionArn `
    --output text

# Create the lambda integration 

$INTEGRATION_ID = aws apigatewayv2 create-integration `
    --api-id $API_ID `
    --integration-type AWS_PROXY `
    --integration-uri $LAMBDA_ARN `
    --payload-format-version 2.0 `
    --region $REGION `
    --query IntegrationId `
    --output text


# Create the /calculate role 

$ROUTE_ID = aws apigatewayv2 create-route `
    --api-id $API_ID `
    --route-key "POST /calculate" `
    --target "integrations/$INTEGRATION_ID" `
    --region $REGION `
    --query RouteId `
    --output text

# Allow API Gateway to invoke lambda 

aws lambda add-permission `
    --function-name beam-calculator-api `
    --statement-id allow-api-gateway-invoke `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/calculate" `
    --region $REGION

# Create the API stage 

aws apigatewayv2 create-stage `
    --api-id $API_ID `
    --stage-name '$default' `
    --auto-deploy `
    --region $REGION

# Get the API endpoint 

$API_URL = aws apigatewayv2 get-api `
    --api-id $API_ID `
    --region $REGION `
    --query ApiEndpoint `
    --output text

# Your final API endpoint 

$CALCULATE_URL = "$API_URL/calculate"

Write-Host $CALCULATE_URL

# final testing of the complete API 

$body = @{
    span = 6.0
    uniform_load = 10.0
    section_modulus = 597.0
    second_moment_of_area = 8503.0
    youngs_modulus = 200.0
    yield_strength = 275.0
    deflection_limit_ratio = 360.0
    input_units = "si"
} | ConvertTo-Json

# Then try to invoke lambda 

Invoke-RestMethod `
    -Uri $CALCULATE_URL `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Connecting to the streamlit 

# set the deployed API url to: 

$env:BEAM_API_URL = $CALCULATE_URL

# Running the streamlit application 

streamlit run ui/streamlit_app.py 

# incase of errors pls address these issues properly 

# 1. Powershell quoting issue 

# Then run:

aws s3api put-bucket-encryption `
    --bucket $BUCKET `
    --server-side-encryption-configuration file://deployment/bucket-encryption.json

# Verify 

aws s3api get-bucket-encryption `
    --bucket $BUCKET

aws s3api put-bucket-encryption `
    --bucket $BUCKET `
    --server-side-encryption-configuration $encryptionConfig

# 2. When thr $ROLE_ARN is unclear pls run these cli related commands 

# Step-1: Check oyu AWS Account ID 

$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

Write-Host $ACCOUNT_ID

# Step-2: Recreate the role ARN 

$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/beam-calculator-lambda-role"

Write-Host $ROLE_ARN

# Step-3: Check the IAM role actually exists 

aws iam get-role `
    --role-name beam-calculator-lambda-role

# Step-4: Please verify the other variables 

Write-Host "ROLE_ARN: $ROLE_ARN"
Write-Host "BUCKET: $BUCKET"
Write-Host "REGION: $REGION"

# Step-5: Then run the function for lambda creation again 

aws lambda create-function `
    --function-name beam-calculator-api `
    --runtime python3.12 `
    --role "$ROLE_ARN" `
    --handler api.lambda_handler.lambda_handler `
    --zip-file fileb://deployment/beam-calculator-lambda.zip `
    --timeout 15 `
    --memory-size 256 `
    --environment "Variables={CALCULATION_BUCKET=$BUCKET}" `
    --region "$REGION"

# Important pls note these session-specific variables for PowerShell again

# $ROLE_ARN
# $ACCOUNT_ID
# $BUCKET
# $REGION

# ./ .sh file for will have this script 

$REGION = "ap-south-1"

$BUCKET = "YOUR-ACTUAL-BUCKET-NAME"

$ACCOUNT_ID = aws sts get-caller-identity `
    --query Account `
    --output text

$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/beam-calculator-lambda-role"

# Verifying these session - specific variables from power shell only 

Write-Host "AWS Account: $ACCOUNT_ID"
Write-Host "Region: $REGION"
Write-Host "Bucket: $BUCKET"
Write-Host "Role ARN: $ROLE_ARN"

# 3. Error in invoking the lambda function 

aws lambda invoke `
    --function-name beam-calculator-api `
    --payload file://deployment/test-event.json `
    --region "$REGION" `
    deployment\lambda-response.json

# Check that the response file was created properly 

Test-Path deployment\lambda-response.json

# Then it returns 

# True 

# Run the final command with values of variables

aws lambda invoke `
    --function-name beam-calculator-api `
    --payload file://deployment/test-event.json `
    --region ap-south-1 `
    deployment\lambda-response.json

# Pls invoke the metadata for the visibility of the output vairable after the lambda function is invoked 

aws lambda invoke `
    --function-name beam-calculator-api `
    --payload file://deployment/test-event.json `
    --region ap-south-1 `
    deployment\lambda-response.json

# for this task also check the CloudWatch Logs correctly 

aws lambda invoke `
    --function-name beam-calculator-api `
    --payload file://deployment/test-event.json `
    --region ap-south-1 `
    deployment\lambda-response.json








