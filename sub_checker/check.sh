#!/bin/bash

userid=$1
pin=$2
from=$3
to=$4

# first request: login, save cookies
curl --cookie-jar cookies -v "https://sub.aesoponline.com/Login/RedirectLogin?userId=$userid&pin=$pin&remember=false&pswd=&loginBaseUrl=www.aesoponline.com" > 1.html  2> /dev/null

# second request, use cookies
curl -v --cookie cookies https://sub.aesoponline.com/Substitute/Home > 2.html  2> /dev/null

# parse output
output=$(cat 2.html | grep '<a href="/Substitute/Schedule/AvailableJobs"><span>' | sed 's~<a href="/Substitute/Schedule/AvailableJobs"><span>~~' | sed 's~</span>~~' | awk '{print $1}')

echo output = "$output" "opening(s)"

if [ -n $output ]; then
    if [ $output -gt 0 ]; then
        echo "Got openings!"
        echo $(cat 2.html | grep "availJobs:" | sed 's/availJobs://' | sed 's/..$//' | python -mjson.tool) > body.json
	/usr/bin/python mail.py $output $userid $pin $from $to
    fi
fi
