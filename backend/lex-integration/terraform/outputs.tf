# Outputs for Lex Integration

output "lex_api_url" {
  description = "URL of the Lex API Gateway"
  value       = "${aws_api_gateway_stage.lex_stage.invoke_url}/lex"
}

output "lex_handler_lambda_arn" {
  description = "ARN of the Lex handler Lambda function"
  value       = aws_lambda_function.lex_handler.arn
}

output "lex_fulfillment_handler_arn" {
  description = "ARN of the Lex fulfillment handler Lambda function"
  value       = aws_lambda_function.lex_fulfillment_handler.arn
}

output "lex_lambda_role_arn" {
  description = "ARN of the Lex Lambda IAM role"
  value       = aws_iam_role.lambda_role.arn
} 