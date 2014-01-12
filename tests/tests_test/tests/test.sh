#!/bin/bash

while read line
do
    echo "Got line $line"
    case "$line" in
        *\"fail\":\ true* ) exit 1 ;;
        *\"timeout\":\ true* ) sleep 10 ;;
        * ) exit 0 ;;
    esac
done
