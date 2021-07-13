# SDR-based Jamming using GNU Radio
## Introduction
Jamming makes use of intentional radio interferences to harm wireless communications by keeping communicating medium busy, causing a transmitter to back-off whenever it senses busy wireless medium, or corrupted signal received at receivers. Jamming mostly targets attacks at the physical layer but sometimes cross-layer attacks are possible too. In this work, we implemented three types of proactive jammers using GNU radio as follows:

1. Constant sweep Jammer
A constant jammer continually emits radio signals on the wireless medium. The signals can consist of a completely random sequence of bits; electromagnetic energy transmissions do not have to follow the rules of any MAC protocol. The goal of this type of jammer is twofold: (a) to pose interference on any transmitting node in order to corrupt its packets at the receiver (lower PDR) and (b) to make a legitimate transmitter (employing carrier sensing) sense the channel busy, thereby preventing it from gaining access to the channel (lower PSR).
In our implementation we implemented a sweep signal that sweeps 20MHz frequency centered at a center frequency F. This allows the blockage of all transmissions within 20MHz of the center frequency. The center frequency is shifted every few seconds to sweep over the whole freqeuncy spectrum of WiFi. In a 2.4GHz WiFi with 14 channels, the jammer hops from one channel to the next sequentially and continously. 

2. Random Channel Hopping Jammer
This is similar to the constant sweep jammer in its operation. However in this jammer, the channel to jam is randomly chosen. This random behaviour makes it harder to determine the behaviour of the jammer as compared to the constant sweep jammer.

3. Random Jammer
The previous two jammers are not energy efficient as they continously radiate radio signals. In this jammer, instead of continuously sending out a radio signal, a random jammer alternates between sleeping and jamming. Specifically, after jamming for tj units of time, it turns off its radio, and enters a “sleeping” mode. It will resume jamming after sleeping for ts time. tj and ts can be either random or fixed values. The core jammer for this could be either the constant sweep jammer or the random channel hopping jammer.

## Implementation
To implement the aforementioned jammers we followed the following methodology
###Requirements
1. 2 Hackrf SDRs, one for transmission and the other for reception
2. [spectrum analyzer GUI for hackrf_sweep](https://github.com/pavsa/hackrf-spectrum-analyzer)
3. Linux machine
###Scripts
1. proactive_jammers.sh is a bash script created for invoking the python program. In this script, at the start the user is prompted to select one of the 3 jammers. After the selection the script calls the constant_jammer.py file continously.
2. constant_jammer.py is a python file that is based on osmocom_siggen_nogui python file of the GNU radio apps. This creates a sweeping signal centered at a frequency that changes based on the passed argument by proactive_jammers.sh script.
###Setup
1. Connect an SMA cable between the two SMA connectors of the SDRs. This ensures we aren’t going to be jamming nearby networks, and get’s rid of background noise.
2. Connect the SDRs to a Linux machine.
3. Startup the spectrum analyzer.
4. Set the start frequency to 2400MHz and Stop frequency to 2500MHz.
5. Open the terminal and navigate to the working directory.
6. Run the proactive_jammers.sh script.
