# AWS Configuration Template for DALScooter
# Replace the placeholder values with your actual AWS credentials and configuration

# AWS Credentials
$env:AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY"
$env:AWS_DEFAULT_REGION = "us-east-1"

# AWS CLI Configuration
aws configure set aws_access_key_id $env:AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $env:AWS_SECRET_ACCESS_KEY
aws configure set default.region $env:AWS_DEFAULT_REGION

Write-Host "AWS configuration completed successfully!"
Write-Host "Please replace the placeholder values with your actual AWS credentials."
Write-Host "For security reasons, never commit this file with real credentials to version control." 