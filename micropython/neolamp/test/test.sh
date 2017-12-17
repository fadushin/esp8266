#!/usr/bin/env bash

IP_ADDR="192.168.1.200"

curl -X POST "http://${IP_ADDR}/api/neolamp/neolamp?color_name=mellow_yellow"
curl -X POST "http://${IP_ADDR}/api/neolamp/mode?mode=neolamp"
