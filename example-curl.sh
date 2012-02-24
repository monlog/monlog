#!/bin/bash
# This is a handy script to use for testing Monlog's API
# Remember to change the API_KEY variable to something present in your database
# Also don't forget that the user connected with that API key needs permissions to add log messages
API_KEY=92ab1ebe33fb6522c590b0e235282020820bca9f
API_URL="http://localhost:8000/api/log/?api_key=$API_KEY"
DATA="$1"

curl --dump-header - -H "Content-Type: application/json" -X POST --data "$DATA" $API_URL
