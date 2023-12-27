#!/bin/bash

usernames="zzhao1 kliang wgao xdong lyang0 jhu2 sjiao pyan jkang lwang4 lliu2 xhou flian zliu2 cxu zwang11 zwang7 yshao1"

for folk in $usernames; do
    echo pdp-reports.py -u $folk
    ./pdp-reports.py -u $folk
done


