#!/bin/bash
# Results bash script
# author: abubakar sani ali

# No jamming transfer result
for run in {1..10}
do
    iperf3 -c 10.20.15.2 -u -b 100M -i 10 -t 5 -J --logfile log_$run.json
done
echo All Done!


