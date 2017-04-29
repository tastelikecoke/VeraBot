#!/bin/sh

echo "Running Vera Bot"
python3 server.py server.log 2> server.err &
