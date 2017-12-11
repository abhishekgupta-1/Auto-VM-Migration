#Assumptions
#Password less login has been already setup with the hosts

from __future__ import print_function
import sys
import libvirt
import time
import thread
#uri - qemu+ssh://uname@ipaddr/system

user_name = "user_name"
ip_address = "ip_addr"
name = "name"
protocol = "qemu+ssh://"
hotspot_detect_interval = 3
utilization_interval = 5
domain_interval = 0.01
host_list = [{user_name : "FDUSER", ip_address : "172.18.16.69", name : "node2"}
,{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"}
,{user_name : "abhu", ip_address : "127.0.0.1", name : "rocknode"}
]

# host_list = [{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"},]

window_size = 10
k_thres = 1

conn_dict = {}

cpu_threshold = 70


#========================Setup Connection=============================

for host in host_list:
	uri = protocol+host[user_name]+"@"+host[ip_address]+"/system"
	conn = libvirt.open(uri)
	if conn == None:
		print("Failed to open for %s "%(host))
	else:
		conn_dict[host[name]] = conn

for name in conn_dict:
	print(name, "=>", conn_dict[name])


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
#TODO: Run a separate thread for getting getStats for each host
# while True:
# 	for host_name in conn_dict:
# 		# printHostStats(host_name)
# 		# print("================")
# 		#Check for hotspots

		
# 		# domains = conn_dict[host_name].listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
# 		# print(domains)
# 		# for dom in domains:
# 		# 	stats = dom.getCPUStats(True)
# 		# 	print("dom-name:"+dom.name())
# 		# 	print("dom-id:"+str(dom.ID()))
# 		# 	print('cpu-time:'+str(stats[0]['cpu_time']))
# 		# 	print('system-time:'+str(stats[0]['system_time']))
# 		# 	print('user_time:'+str(stats[0]['user_time']))
# 		# 	print("=================")
# 		# print("=================================================================")
		
# 	time.sleep(hotspot_detect_interval)




def hotspot_detector(host_name):
	conn = conn_dict[host_name]
	window = []
	k_val = 0
	while True:
		t1 = time.time()
		prev_stats = conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)
		t2 = time.time()
		time.sleep(utilization_interval)
		t3 = time.time()
		new_stats = conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)
		t4 = time.time()
		util = getCPUUtil(new_stats, prev_stats, t2-t1+t4-t3)

		print(host_name, util)
		
		if len(window) == window_size:
			if window[0] > cpu_threshold:
				k_val -= 1
			window = window[1:]
		window.append(util)
		if util > cpu_threshold:
			k_val += 1
		if k_val > k_thres:
			print("Hotspot detected at %s"%(host_name))
			thread.start_new_thread(find_domain, (host_name,))
			#Create a new thread to find VMs domains, which domain
		time.sleep(hotspot_detect_interval)


for host_name in conn_dict:
	try:
		# hotspot_detector(host_name)
		thread.start_new_thread(hotspot_detector, (host_name,))
		
	except:
		print("Unable to run hotspot detector thread %s"%(host_name))
		raise

def getCPUUtil(new_stats, prev_stats, additional_time):
	lis = ['user', 'kernel']
	prev_sum = 0
	new_sum = 0
	for ite in lis:
		prev_sum += prev_stats[ite]
		new_sum += new_stats[ite]
	util = (new_sum-prev_sum)/((utilization_interval+additional_time)*10000000.)
	return util

def getdomCPUUtil(new_stats, prev_stats, additional_time):
	lis = ['cpu_time', 'system_time']
	prev_sum = 0
	new_sum = 0
	for ite in lis:
		prev_sum += prev_stats[ite]
		new_sum += new_stats[ite]
	util = (new_sum-prev_sum)/((domain_interval)*10000000.)
	return util
	

def getMemoryUtil(new_mem_stats, prev_mem_stats, additional_time):
	new_mem = new_mem_stats['rss']
	old_mem = prev_mem_stats['rss']
	# print('memory used:')
	#for name in stats:
		# print('  '+str(stats[name])+' ('+name+')')
	#	memory_stats += stats[name]
	memory_util = (new_mem + old_mem) / 2.0	
	return memory_util



def find_domain(host_name):
	conn = conn_dict[host_name]
	domainIDs = conn.listDomainsID()
	if len(domainIDs) == 0:
		print('None')
		exit(0)
	else:
		dom_cache = {}
		num_of_times = 5
		val = {}
		for _ in range(num_of_times):
			for domainID in domainIDs:
				dom = dom_cache.get(domainID)
				if dom == None:
					dom = conn.lookupByID(domainID)
					dom_cache[domainID] = dom
				if dom == None:
				    print('Failed to find the domain ', file=sys.stderr)
				    exit(1)

				
				prev_cpu_time_sum = 0
				new_cpu_time_sum = 0
				prev_memory_stats = 0
				new_memory_stats = 0

				prev_cpu_stats = dom.getCPUStats(True)
				prev_mem_stats  = dom.memoryStats()
				
				time.sleep(domain_interval)
				
				new_cpu_stats = dom.getCPUStats(True)
				new_mem_stats = dom.memoryStats()
				
				cpu_util = getdomCPUUtil(new_cpu_stats[0], prev_cpu_stats[0], 0.2)
				mem_util = getMemoryUtil(new_mem_stats, prev_mem_stats, 0.2)


				if val.get(domainID) == None:
					val[domainID] = {'mem': [], 'cpu' : []}

				val[domainID]['mem'].append(mem_util)
				val[domainID]['cpu'].append(cpu_util)

		averages = {}
		for domainID in val:
			res = {}
			stats = val[domainID]
			for typ in stats:
				lis = stats[typ]
				y = 0
				for x in lis:
					y += x
				res[typ] = y/float(num_of_times)
			averages[domainID] = res
		print(averages)









#=========================Close the program============================
while True:
	time.sleep(5)
	pass

for name in conn_dict:
	conn_dict[name].close()
	

# if len(domainIDs) == 0:
# 	print('  None')
# 	exit(0)
# else:
# 	cpu_stat_dict = {}
# 	mem_stat_dict = {}
# 	k_val = 7
# 	n_val = 20
# 	cpu_thres = 150
# 	mem_thres = 150
# 	k_cpu_val_dict = {}
# 	k_mem_val_dict = {}
# 	while True:
# 		val = {}
# 		for domainID in domainIDs:
# 			print('Active domain:  '+str(domainID))
# 			dom = conn.lookupByID(domainID)
# 			if dom == None:
# 			    print('Failed to find the domain ', file=sys.stderr)
# 			    exit(1)
# 			interval = 0.01
# 			prev_cpu_time_sum = 0
# 			new_cpu_time_sum = 0
# 			prev_memory_stats = 0
# 			new_memory_stats = 0

# 			cpu_stats = dom.getCPUStats(True)
# 			stats  = dom.memoryStats()
			
# 			prev_cpu_time_sum = getCPUTimeSum(cpu_stats)
# 			prev_memory_stats = getMemoryStats(stats)
			
# 			print("Interval of", interval, "seconds")
# 			time.sleep(interval)
			
# 			cpu_stats = dom.getCPUStats(True)
			
# 			stats = dom.memoryStats()
# 			new_cpu_time_sum = getCPUTimeSum(cpu_stats)
# 			new_memory_stats = getMemoryStats(stats)
			
			
# 			cpu_util = (new_cpu_time_sum - prev_cpu_time_sum)/(interval*10000000)
# 			mem_util = (new_memory_stats + prev_memory_stats)/(2) 
# 			lis = cpu_stat_dict.get(domainID)
# 			memlis = mem_stat_dict.get(domainID)
# 			if lis == None:
# 				lis = []
# 				memlis = []
# 				k_cpu_val_dict[domainID] = 0
# 				k_mem_val_dict[domainID] = 0
# 			if len(lis) == n_val:
# 				if lis[0] > cpu_thres:
# 					k_cpu_val_dict[domainID] -= 1
# 				if memlis[0] > mem_thres:
# 					k_mem_val_dict[domainID] -= 1
# 				lis = lis[1:]
# 				memlis = memlis[1:]
# 			lis.append(cpu_util)
# 			memlis.append(mem_util)
# 			if cpu_util > cpu_thres:
# 				k_cpu_val_dict[domainID] += 1
# 			if mem_util > mem_thres:
# 				k_mem_val_dict[domainID] += 1
# 			cpu_stat_dict[domainID] = lis
# 			mem_stat_dict[domainID] = memlis
# 			val[domainID] = {"CPU":cpu_util, "MEM":mem_util}
# 			if k_cpu_val_dict[domainID] > k_val or k_mem_val_dict[domainID] > k_val: #Migrate this
# 				print("Domain id %d should be migrated!"%(domainID))
# 		print(val)
# 		time.sleep(3)

