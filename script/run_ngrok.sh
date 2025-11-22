#!/bin/bash

port=25565 # default

if [ -n "$1" ]; then
    port="$1"
fi

ngrok http ${port}