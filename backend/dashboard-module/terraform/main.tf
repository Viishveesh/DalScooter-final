data "aws_caller_identity" "current" {}

provider "aws" {
  region = "us-east-1"
}

# ZIP Lambda Functions

data "archive_file" "get_user_count_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/get_user_count.py"
  output_path = "${path.module}/../lambdas/get_user_count.zip"
}

data "archive_file" "log_user_login_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambdas/log_user_login.py"
  output_path = "${path.module}/../lambdas/log_user_login.zip"
}

# Lambda Functions

resource "aws_lambda_function" "get_user_count" {
  function_name = "get_user_count"
  role          = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"
  runtime       = "python3.12"
  handler       = "get_user_count.lambda_handler"
  filename      = data.archive_file.get_user_count_zip.output_path

  environment {
    variables = {
      COGNITO_USER_POOL_ID = var.cognito_user_pool_id
    }
  }
}

resource "aws_lambda_function" "log_user_login" {
  function_name = "log_user_login"
  role          = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"
  runtime       = "python3.12"
  handler       = "log_user_login.lambda_handler"
  filename      = data.archive_file.log_user_login_zip.output_path

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = "UserLogins"
    }
  }
}

# API Gateway

resource "aws_apigatewayv2_api" "user_api" {
  name          = "UserCountAPI"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "OPTIONS", "GET", "PUT", "DELETE"]
    allow_headers = ["*"]
    expose_headers = ["*"]
    max_age        = 3600
  }
}

# Integrations

resource "aws_apigatewayv2_integration" "user_count_integration" {
  api_id                 = aws_apigatewayv2_api.user_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.get_user_count.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "log_user_login_integration" {
  api_id                 = aws_apigatewayv2_api.user_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.log_user_login.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}


# Routes

resource "aws_apigatewayv2_route" "user_count_route" {
  api_id    = aws_apigatewayv2_api.user_api.id
  route_key = "GET /user-count"
  target    = "integrations/${aws_apigatewayv2_integration.user_count_integration.id}"
}

resource "aws_apigatewayv2_route" "log_user_login_route" {
  api_id    = aws_apigatewayv2_api.user_api.id
  route_key = "POST /log-login"
  target    = "integrations/${aws_apigatewayv2_integration.log_user_login_integration.id}"
}

# Lambda Permissions

resource "aws_lambda_permission" "allow_apigw_get_user_count" {
  statement_id  = "AllowAPIGatewayInvokeUserCount"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_user_count.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.user_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "allow_apigw_log_user_login" {
  statement_id  = "AllowAPIGatewayInvokeLogLogin"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_user_login.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.user_api.execution_arn}/*/*"
}

# Stage

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.user_api.id
  name        = "$default"
  auto_deploy = true
}
