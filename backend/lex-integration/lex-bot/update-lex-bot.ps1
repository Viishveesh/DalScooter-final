# Update Lex Bot for DALScooter
Write-Host "Updating Lex Bot for DALScooter..."

# Update bot configuration
$botId = "YOUR_BOT_ID"
$botVersion = "DRAFT"
$localeId = "en_US"

# Update bot settings
aws lexv2-models update-bot `
    --bot-id $botId `
    --bot-name "DALScooterBot" `
    --description "AI assistant for DALScooter rental service" `
    --role-arn "arn:aws:iam::ACCOUNT_ID:role/LexBotRole" `
    --data-privacy "PRIVACY_POLICY" `
    --idle-session-ttl-in-seconds 300

Write-Host "Bot updated successfully!"

# Update intents
Write-Host "Updating intents..."

# Update BookScooter Intent
aws lexv2-models update-intent `
    --bot-id $botId `
    --bot-version $botVersion `
    --locale-id $localeId `
    --intent-name "BookScooter" `
    --description "Intent for booking a scooter"

# Update CheckBooking Intent
aws lexv2-models update-intent `
    --bot-id $botId `
    --bot-version $botVersion `
    --locale-id $localeId `
    --intent-name "CheckBooking" `
    --description "Intent for checking booking status"

# Update CancelBooking Intent
aws lexv2-models update-intent `
    --bot-id $botId `
    --bot-version $botVersion `
    --locale-id $localeId `
    --intent-name "CancelBooking" `
    --description "Intent for canceling a booking"

Write-Host "Intents updated successfully!" 