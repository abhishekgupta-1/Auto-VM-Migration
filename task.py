#Assumptions
#Password less login has been already setup with the hosts

from __future__ import print_function
import sys
import libvirt

#uri - qemu+ssh://uname@ipaddr/system

user_name = "user_name"
ip_address = "ip_addr"
name = "name"
protocol = "qemu+ssh://"

#========================Setup Connection=============================

# host_list = [{user_name : "FDUSER", ip_address : "172.18.16.69", name : "node2"}
# ,{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"}]
host_list = [{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"},]

conn_dict = {}
active_hosts = []

for host in host_list:
	uri = protocol+host[user_name]+"@"+host[ip_address]+"/system"
	conn = libvirt.open(uri)
	if conn == None:
		print("Failed to open for %s "%(host))
	else:
		conn_dict[host[name]] = conn
		active_hosts.append(host[name])

for name in active_hosts:
	print(conn_dict[name])


#=================================Utility===============================

def printHostStats(host_name):
	conn = conn_dict.get(host_name)
	if conn == None:
		print("unable to get stats for %s"%(node_name))
		return
	domainIds = conn.listDomainsID()
	print("Domains : %s"%(domainIds))
	memoryStats = conn.getMemoryStats(libvirt.VIR_NODE_MEMORY_STATS_ALL_CELLS)
	cpuStats = conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)
	print("For %s : memoryStats = %s, cpuStats=%s"%(host_name,memoryStats,cpuStats))





#===========================Main=======================================
#Run a separate thread for getting getStats for each host

for host_name in active_hosts:
	printHostStats(host_name)
	print("===============")
	domains = conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
	for dom in domains:
		stats = dom.getCPUStats(True)
		print("dom-name:"+dom.name())
		print("dom-id:"+str(dom.ID()))
		print('cpu-time:'+str(stats[0]['cpu_time']))
		print('system-time:'+str(stats[0]['system_time']))
		print('user_time:'+str(stats[0]['user_time']))
		print("=================")


#=========================Close the program============================


for name in active_hosts:
	conn_dict[name].close()
