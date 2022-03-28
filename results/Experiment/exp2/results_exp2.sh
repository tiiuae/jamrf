#!/bin/bash
# Results bash script
# author: abubakar sani ali

# No jamming transfer result
# iperf3 -c 10.20.15.2 -u -b 100M -t 240 -J --logfile log.json


for waveform in {3..3}
do
    for ch_dist in {4..4}
    do
    	for run in {1..10}
    	do
    	    str="_"
    	    file=$waveform$str$ch_dist$str$run.json
    	    iperf3 -c 10.20.15.2 -u -b 100M -i 10 -t 180 -J --logfile log_$file
    	done
    done
done

echo All Done
