#!/bin/bash

# Create Lex Bot for DALScooter
echo "Creating Lex Bot for DALScooter..."

# Create the bot
aws lexv2-models create-bot \
    --bot-name "DALScooterBot" \
    --description "AI assistant for DALScooter rental service" \
    --role-arn "arn:aws:iam::ACCOUNT_ID:role/LexBotRole" \
    --data-privacy "PRIVACY_POLICY" \
    --idle-session-ttl-in-seconds 300

echo "Bot created successfully!"

# Create intents
echo "Creating intents..."

# BookScooter Intent
aws lexv2-models create-intent \
    --bot-id "BOT_ID" \
    --bot-version "DRAFT" \
    --locale-id "en_US" \
    --intent-name "BookScooter" \
    --description "Intent for booking a scooter"

# CheckBooking Intent
aws lexv2-models create-intent \
    --bot-id "BOT_ID" \
    --bot-version "DRAFT" \
    --locale-id "en_US" \
    --intent-name "CheckBooking" \
    --description "Intent for checking booking status"

# CancelBooking Intent
aws lexv2-models create-intent \
    --bot-id "BOT_ID" \
    --bot-version "DRAFT" \
    --locale-id "en_US" \
    --intent-name "CancelBooking" \
    --description "Intent for canceling a booking"

echo "Intents created successfully!" 