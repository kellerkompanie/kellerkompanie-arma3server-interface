#!/bin/bash

/home/arma3server/arma3server start

if [[ $# -gt 0 ]]; then
  if [[ $1 == "true" ]]; then
    /home/arma3server/arma3hc1 start
    /home/arma3server/arma3hc2 start
    /home/arma3server/arma3hc3 start
  fi
fi