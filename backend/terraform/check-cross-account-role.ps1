# Check Cross-Account Role for DALScooter
Write-Host "Checking cross-account role..."

# Set AWS region
$env:AWS_DEFAULT_REGION = "us-east-1"

# Check if the role exists
$roleName = "DALScooterCrossAccountRole"
$roleArn = "arn:aws:iam::ACCOUNT_ID:role/$roleName"

try {
    $role = aws iam get-role --role-name $roleName
    Write-Host "Cross-account role exists: $roleArn"
    Write-Host "Role ARN: $($role.Role.Arn)"
} catch {
    Write-Host "Cross-account role does not exist. Creating..."
    
    # Create the role
    aws iam create-role `
        --role-name $roleName `
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }'
    
    Write-Host "Cross-account role created successfully!"
}

Write-Host "Cross-account role check completed!" 