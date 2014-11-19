#!/bin/sh
if_file="/etc/network/interfaces"
res_file="/etc/resolv.conf"

if [ $# -gt "0" ]; then
	device=$1
else
	device="usb0"
fi

error="0"
devstat=$(ip link show $device 2>/dev/null)
if [ $? -ne 0 ]; then error="1"; fi
#if [ ! -f $if_file ]; then error="1"; fi
if [ ! -f $res_file ]; then error="1"; fi

dynamic=$(grep "^iface $device" $if_file | awk '{print $4}')
dyn_flag="-1"
if [ $dynamic == "dhcp" ]; then
	dyn_flag="1"
elif [ $dynamic == "static" ]; then
	dyn_flag="0"
fi

if [ $error -eq "0" ]; then
	ip_addr=$(ifconfig $device | grep "inet addr" | awk '{print $2}' | cut -d':' -f2 )
	subnet_mask=$(ifconfig $device | grep "Mask" | awk '{print $4}'| cut -d':' -f2 ) 
	gateway=$(ip route show | grep "default" | awk '{print $3}')
	dns=$(grep "nameserver" $res_file | head -n 1 | awk '{print $2}') 
	echo "$device $dyn_flag $ip_addr $subnet_mask $gateway $dns"
else
	echo "ERROR"
fi

