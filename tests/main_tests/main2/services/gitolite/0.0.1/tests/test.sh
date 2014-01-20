#!/bin/sh

# read stdin so we don't break pipes
while read line
do
    echo $line
done

exit 0
