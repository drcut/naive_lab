#!/bin/sh
less sift_lines.txt | awk '{if(NF>7)print $0}'
