#!/bin/bash

echo "establishing TCP connection on $1:$2"

for i in $(seq 1 30); do
  echo "... attempt $i ..."
  nc -z "$1" "$2" && echo Success && exit 0
  sleep 1
done

echo Failed waiting for Postgres && exit 1
