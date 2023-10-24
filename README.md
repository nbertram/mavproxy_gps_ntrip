This is a MAVProxy module that dynamically picks an NTRIP peer based on
a rough GPS location provided over MAVLink.

It's not at all generic, but I've made it public in case anyone needs
something similar as a starting point.

It assumes all the rest of the ntrip config is passed in a startup script.
