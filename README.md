# Bed Lights

This is a simple script to run a string of LED lights on
my bed. The lights are ran by a Griffin Technology Powermate
programmable button that I had lying around. This code runs
on a raspberry pi.  


## To Run:

To get a list of usb devices:

    usbls -v

For powermate in bottom right usb slot:

    /dev/bus/usb/001/007

Need to use sudo to run:

    sudo python3 bed_lights.py -c 

    
