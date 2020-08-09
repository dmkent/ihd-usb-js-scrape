Tool to parse data from Origin IHD device

The device connects to the smart meter and displays usage and cost
information. When connected to a PC via USB it provides a simple web
interface to view the last few month's data.

The web interface presents its data as a bunch of JS files containing
array data. This tool parses the JS and sends the most recent data
using MQTT.

Package also installs a shell script (`ihd_power_cycle_usb.sh`) that will
disconnect and reconnect the USB device to force the data in the JS files
to refresh.

That shell script needs the following APT packages installed (on a Raspberry Pi):

* libatlas-base-dev (actually needed by `pandas`)
* eject
