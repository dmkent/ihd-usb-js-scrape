#!/bin/bash

BLKNAMEEXPR="Origin\s\+Energy_Monitor"
MOUNTPATH=$1

if [ "0" -ne $( id -ru ) ] ; then
  echo "Script must be run as root"
  exit 1
fi 

if [ ! -d "${MOUNTPATH}" ] ; then
  echo "Mount path [${MOUNTPATH}] does not exist"
  exit 1
fi

# find disk devices using the name
devices=$( lsblk -S | grep "${BLKNAMEEXPR}" | cut -d" " -f 1 )

if [ -z "${devices}" ] ; then
  echo "Unable to find disk(s)"
  exit 2
fi
maindevice=$( echo ${devices} | cut -d" " -f 1 )

# Unmount and eject the disks
for device in ${devices} ;
do
  umount /dev/${device}1 > /dev/null 2>&1
  eject /dev/${device}
done

# Determine the parent USB device ID
usbdevice=$( ls -l /sys/block/${maindevice} | sed -e "s/.*\/\([0-9\:\.-]\+\)\/host.*/\1/" )
if [ ! -L /sys/bus/usb/devices/${usbdevice} ] ; then
  echo "Unable to determine USB device ID"
  exit 3
fi

# Unbind it to power it down/disconnect it
echo ${usbdevice} > /sys/bus/usb/drivers/usb-storage/unbind
sleep 2

# Bind it again to power it up again
echo ${usbdevice} > /sys/bus/usb/drivers/usb-storage/bind

# Mount the primary disk again
sleep 5
devices=$( lsblk -S | grep "${BLKNAMEEXPR}" | cut -d" " -f 1 )
if [ -z "${devices}" ] ; then
  echo "Unable to find disk(s)"
  exit 2
fi
maindevice=$( echo ${devices} | cut -d" " -f 1 )
mount -t vfat /dev/${maindevice}1 ${MOUNTPATH} -o ro,uid=1000,gid=1000,utf8,dmask=027,fmask=137
