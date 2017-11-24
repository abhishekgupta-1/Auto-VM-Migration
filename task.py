#Assumptions
#Password less login has been already setup with the hosts

from __future__ import print_function
import sys
import libvirt

#uri - qemu+ssh://uname@ipaddr/system

user_name = "user_name"
ip_address = "ip_addr"
name = "name"
protocol = "qemu+ssh"

host_list = [{user_name : "FDUSER", ip_address : "172.18.16.69", name : "node2"}
,{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"}]

conn_dict = {}

for host in host_list:
	uri = protocol+"://"+host[user_name]+"@"+host[ip_address]+"/system"
	conn_dict[host[name]] = libvirt.open(uri)
	if conn_dict[host[name]] == None:
		print("Failed to open for %s "%(host))
		conn_dict.pop(host[name], None) #Removing the key

for name in conn_dict:
	print(conn_dict[name])


for name in conn_dict:
	conn_dict[name].close()

