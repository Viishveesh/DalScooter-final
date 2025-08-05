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

# IAM Role for Lex Bot
resource "aws_iam_role" "lex_bot_role" {
  name = "DALScooterLexBotRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lex.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lex Bot
resource "aws_iam_role_policy" "lex_bot_policy" {
  name = "DALScooterLexBotPolicy"
  role = aws_iam_role.lex_bot_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lex:RecognizeText",
          "lex:RecognizeUtterance",
          "lex:StartConversation"
        ]
        Resource = "*"
      }
    ]
  })
}

# Lambda Function for Lex Handler
resource "aws_lambda_function" "lex_handler" {
  filename         = "../lambda/lex_handler.zip"
  function_name    = "DALScooterLexHandler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lex_handler.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      LEX_BOT_ID        = aws_lexv2_bot.dalscooter_bot.id
      LEX_BOT_ALIAS_ID  = aws_lexv2_bot_alias.dalscooter_alias.id
      BOOKINGS_TABLE_NAME = var.bookings_table_name
      USERS_TABLE_NAME   = var.users_table_name
    }
  }
}

# Lambda Function for Lex Fulfillment
resource "aws_lambda_function" "lex_fulfillment" {
  filename         = "../personal-account-lambda/lex_fulfillment_handler.zip"
  function_name    = "DALScooterLexFulfillment"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lex_fulfillment_handler.lambda_handler"
  runtime         = "python3.9"
  timeout         = 30

  environment {
    variables = {
      BOOKINGS_TABLE_NAME = var.bookings_table_name
      USERS_TABLE_NAME   = var.users_table_name
    }
  }
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
          "lexv2-runtime:RecognizeText",
          "lexv2-runtime:RecognizeUtterance",
          "lexv2-runtime:StartConversation",
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

# Lex Bot
resource "aws_lexv2_bot" "dalscooter_bot" {
  name = "DALScooterBot"
  description = "AI assistant for DALScooter rental service"
  role_arn = aws_iam_role.lex_bot_role.arn
  data_privacy = "PRIVACY_POLICY"
  idle_session_ttl_in_seconds = 300
}

# Lex Bot Alias
resource "aws_lexv2_bot_alias" "dalscooter_alias" {
  bot_id = aws_lexv2_bot.dalscooter_bot.id
  bot_alias_name = "DALScooterAlias"
  description = "Production alias for DALScooter bot"
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