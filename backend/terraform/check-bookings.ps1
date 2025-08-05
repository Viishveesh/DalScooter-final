# Check Bookings Script for DALScooter
Write-Host "Checking bookings..."

# Set AWS region
$env:AWS_DEFAULT_REGION = "us-east-1"

# Get API Gateway URL from Terraform output
$apiUrl = terraform output -raw api_gateway_url

# Check all bookings
Write-Host "Fetching all bookings..."
$response = Invoke-RestMethod -Uri "$apiUrl/bookings" -Method GET

Write-Host "Bookings found: $($response.Count)"
foreach ($booking in $response) {
    Write-Host "Booking ID: $($booking.id), Status: $($booking.status), User: $($booking.user_id)"
}

Write-Host "Booking check completed!" 