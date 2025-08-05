# Get Cognito Information and Update Frontend Environment Variables

Write-Host "Getting Cognito User Pool Client ID..."

# Get the User Pool ID from Terraform state
$userPoolId = terraform output -raw auth_user_pool_id 2>$null
if (-not $userPoolId) {
    Write-Host "User Pool ID not found in Terraform outputs. Please run 'terraform apply' first."
    exit 1
}

Write-Host "User Pool ID: $userPoolId"

# Get the User Pool Client ID from Terraform state
$userPoolClientId = terraform output -raw auth_user_pool_client_id 2>$null
if (-not $userPoolClientId) {
    Write-Host "User Pool Client ID not found in Terraform outputs. Please run 'terraform apply' first."
    exit 1
}

Write-Host "User Pool Client ID: $userPoolClientId"

# Get API endpoints
$authApiEndpoint = terraform output -raw auth_api_gateway_endpoint
$bikeApiEndpoint = terraform output -raw bike_crud_api_endpoint
$bookingApiEndpoint = terraform output -raw booking_api_endpoint
$feedbackApiEndpoint = terraform output -raw feedback_api_endpoint
$complaintApiEndpoint = terraform output -raw complaint_api_endpoint

Write-Host "API Endpoints:"
Write-Host "Auth API: $authApiEndpoint"
Write-Host "Bike API: $bikeApiEndpoint"
Write-Host "Booking API: $bookingApiEndpoint"
Write-Host "Feedback API: $feedbackApiEndpoint"
Write-Host "Complaint API: $complaintApiEndpoint"

# Create frontend environment file
$envContent = @"
# DALScooter Frontend Environment Variables

# Cognito Configuration
VITE_COGNITO_USER_POOL_ID=$userPoolId
VITE_COGNITO_USER_POOL_CLIENT_ID=$userPoolClientId
VITE_COGNITO_REGION=us-east-1

# API Gateway Endpoints
VITE_AUTH_API_URL=$authApiEndpoint
VITE_BIKE_API_URL=$bikeApiEndpoint
VITE_BOOKING_API_URL=$bookingApiEndpoint
VITE_FEEDBACK_API_URL=$feedbackApiEndpoint
VITE_COMPLAINT_API_URL=$complaintApiEndpoint

# Lex API (will be updated after Lex deployment)
VITE_LEX_API_URL=https://your-lex-api-gateway-url.amazonaws.com/prod/lex
"@

# Write to frontend .env file
$envContent | Out-File -FilePath "../../frontend/.env" -Encoding UTF8

Write-Host "Frontend environment file updated successfully!"
Write-Host "Please restart your frontend development server." 