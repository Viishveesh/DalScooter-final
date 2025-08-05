# Lex Integration Terraform Configuration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM Role for Lambda Functions
resource "aws_iam_role" "lambda_role" {
  name = "DALScooterLexLambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda Functions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "DALScooterLexLambdaPolicy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function for Lex Handler
resource "aws_lambda_function" "lex_handler" {
  filename         = "../lambda/lex_handler.py"
  function_name    = "DALScooterLexHandler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lex_handler.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      BOOKINGS_TABLE_NAME = var.bookings_table_name
      USERS_TABLE_NAME   = var.users_table_name
    }
  }
}

# API Gateway for Lex Integration
resource "aws_api_gateway_rest_api" "lex_api" {
  name = "DALScooterLexAPI"
  description = "API Gateway for Lex integration"
}

# API Gateway Resource
resource "aws_api_gateway_resource" "lex_resource" {
  rest_api_id = aws_api_gateway_rest_api.lex_api.id
  parent_id   = aws_api_gateway_rest_api.lex_api.root_resource_id
  path_part   = "lex"
}

# API Gateway Method
resource "aws_api_gateway_method" "lex_method" {
  rest_api_id   = aws_api_gateway_rest_api.lex_api.id
  resource_id   = aws_api_gateway_resource.lex_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration
resource "aws_api_gateway_integration" "lex_integration" {
  rest_api_id = aws_api_gateway_rest_api.lex_api.id
  resource_id = aws_api_gateway_resource.lex_resource.id
  http_method = aws_api_gateway_method.lex_method.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.lex_handler.invoke_arn
}

# Lambda Permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lex_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lex_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "lex_deployment" {
  rest_api_id = aws_api_gateway_rest_api.lex_api.id
  depends_on = [
    aws_api_gateway_integration.lex_integration
  ]
}

# API Gateway Stage
resource "aws_api_gateway_stage" "lex_stage" {
  deployment_id = aws_api_gateway_deployment.lex_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.lex_api.id
  stage_name    = "prod"
} 