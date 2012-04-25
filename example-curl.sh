#!/bin/bash
# This is a handy script to use for testing Monlog's API
# Remember to change the API_KEY variable to something present in your database
# Also don't forget that the user connected with that API key needs permissions to add log messages
API_KEY=7a64b819fed3edb9c7c06680d9b99ab44db4dd79
API_URL="http://localhost:8000/api/log/?api_key=$API_KEY"
DATA="$1"

curl --dump-header - -H "Content-Type: application/json" -X POST --data "$DATA" $API_URL
