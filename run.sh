#!/bin/bash

# how to start flask:

export FLASK_ENV=development
echo $FLASK_ENV		# expected output is development
export FLASK_APP='./app.py'
flask run -p 5500
