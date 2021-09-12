#!/bin/bash
# Results bash script
# author: abubakar sani ali

# No jamming transfer result
# iperf3 -c 10.20.15.2 -u -b 100M -t 240 -J --logfile log.json

for waveform in {3..3}
do
    for power in {10..10}
    do
        for run in {10..10}
	do
	    str="_"
            iperf3 -c 10.20.15.2 -u -b 100M -i 10 -t 30 -J --logfile log_$waveform$str$power$str$run.json
	done
    done
done

echo All Done!
