#!/bin/bash
# This is a handy script to use for testing Monlog's API
# Remember to change the API_KEY variable to something present in your database
# Also don't forget that the user connected with that API key needs permissions to add log messages
API_KEY=923401cccf603724f0c6a5e1b72ea1f65750cb2b
API_URL="http://localhost:8000/api/log/?api_key=$API_KEY"
DATA='{ "severity": 0, "datetime": "2012-02-05T10:10:10", "long_desc": "This is my long description", "short_desc": "Shortdesc" }'

curl --dump-header - -H "Content-Type: application/json" -X POST --data "$DATA" $API_URL
