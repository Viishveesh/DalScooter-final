# Outputs for Lex Integration

output "lex_bot_id" {
  description = "ID of the Lex bot"
  value       = aws_lexv2_bot.dalscooter_bot.id
}

output "lex_bot_alias_id" {
  description = "ID of the Lex bot alias"
  value       = aws_lexv2_bot_alias.dalscooter_alias.id
}

output "lex_api_url" {
  description = "URL of the Lex API Gateway"
  value       = "${aws_api_gateway_stage.lex_stage.invoke_url}/lex"
}

output "lex_handler_lambda_arn" {
  description = "ARN of the Lex handler Lambda function"
  value       = aws_lambda_function.lex_handler.arn
}

output "lex_fulfillment_lambda_arn" {
  description = "ARN of the Lex fulfillment Lambda function"
  value       = aws_lambda_function.lex_fulfillment.arn
}

output "lex_bot_role_arn" {
  description = "ARN of the Lex bot IAM role"
  value       = aws_iam_role.lex_bot_role.arn
}

output "lex_lambda_role_arn" {
  description = "ARN of the Lex Lambda IAM role"
  value       = aws_iam_role.lambda_role.arn
} 