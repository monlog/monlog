#!/bin/bash
for (( c=1; c<=100; c++))
do
    python random-data.py >> example-data.sh
done
