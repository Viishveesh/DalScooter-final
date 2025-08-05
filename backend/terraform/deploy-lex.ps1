# Deploy Lex Integration for DALScooter
Write-Host "Deploying Lex Integration..."

# Set AWS region
$env:AWS_DEFAULT_REGION = "us-east-1"

# Navigate to lex-integration directory
Set-Location "backend/lex-integration"

# Deploy Terraform infrastructure
Write-Host "Deploying Lex infrastructure..."
terraform init
terraform plan
terraform apply -auto-approve

# Create Lex bot
Write-Host "Creating Lex bot..."
Set-Location "lex-bot"
./create-lex-bot.sh

Write-Host "Lex integration deployment completed!"
Set-Location "../../../" 