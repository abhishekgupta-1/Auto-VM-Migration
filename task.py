#Assumptions
#Password less login has been already setup with the hosts

from __future__ import print_function
import sys
import libvirt
import time
import thread
from xml.etree import ElementTree
import threading

#uri - qemu+ssh://uname@ipaddr/system

user_name = "user_name"
ip_address = "ip_addr"
name = "name"
protocol = "qemu+ssh://"
hotspot_detect_interval = 3
utilization_interval = 5
domain_interval = 1
host_list = [{user_name : "FDUSER", ip_address : "172.18.16.69", name : "node2"}
,{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"}
#,{user_name : "abhu", ip_address : "127.0.0.1", name : "rocknode"}
]
host_stats = {}
# host_list = [{user_name : "FDUSER", ip_address : "172.18.16.13", name : "node3"},]

window_size = 10
k_thres = 1
k_val = {}
window_dict = {}
conn_dict = {}

cpu_threshold = 2


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



hotspot_domain = 0


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
	util = (new_sum-prev_sum)/((domain_interval+additional_time)*10000000.)
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

def getNetworkUtil(new_network_stats, prev_network_stats, additional_time):
	new_net = new_network_stats[1]+new_network_stats[5]
	old_net = prev_network_stats[1]+prev_network_stats[5]
	# print('memory used:')
	#for name in stats:
		# print('  '+str(stats[name])+' ('+name+')')
	#	memory_stats += stats[name]
	return (new_net - old_net)/(domain_interval+additional_time)


def hotspot_detector(host_name):
	conn = conn_dict[host_name]
	window = window_dict.get(host_name)
	if window == None:
		window_dict[host_name] = []
		window = []
	k_va = k_val.get(host_name)
	if k_va == None:
		k_val[host_name] = 0
	t1 = time.time()
	prev_stats = conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)
	t2 = time.time()
	time.sleep(utilization_interval)
	t3 = time.time()
	new_stats = conn.getCPUStats(libvirt.VIR_NODE_CPU_STATS_ALL_CPUS)
	t4 = time.time()
	util = getCPUUtil(new_stats, prev_stats, t2-t1+t4-t3)

	print(host_name, util, "\n--------------------\n")
	if len(window) == window_size:
		if window[0] > cpu_threshold:
			k_val[host_name] -= 1
		window = window[1:]
	window.append(util)
	window_dict[host_name] = window
	if util > cpu_threshold:
		k_val[host_name] += 1
	hotspot = False
	if k_val[host_name] > k_thres:
		hotspot = True
		print("\n================  Hotspot detected at %s  ======================\n"%(host_name))
		#thread.start_new_thread(find_domain, (host_name,))
		#Create a new thread to find VMs domains, which domain
	score = 0
	alpha = 0.8
	lengt = len(window)
	for i in range(lengt):
		score += alpha * window[lengt-1-i]
	host_stats[host_name] = {"score":score, "window":window,"hotspot":hotspot} 


def filterDomain(domainInfos, filterType):#Max - Max VSR, Min otherwise
	aggregates = {}
	host_min = -1
	aggr_min = 100000000
	host_max = -1
	aggr_max = -1
	for dom in domainInfos:
		vals = domainInfos[dom]
		aggr_val = 1
		for x in vals: #VSR Calculation
			aggr_val *= vals[x]
		aggr_val /= 10000000
		if aggr_val < aggr_min:
			aggr_min = aggr_val
			host_min = dom
		if aggr_val > aggr_max:
			aggr_max = aggr_val
			host_max = dom
	if filterType == True:
		return host_max
	return host_min
			







def find_domain(host_name):
	conn = conn_dict[host_name]
	domainIDs = conn.listDomainsID()
	if len(domainIDs) == 0:
		print('None')
		return {}
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
				tree = ElementTree.fromstring(dom.XMLDesc())
				iface = tree.find('devices/interface/target').get('dev')
				prev_cpu_time_sum = 0
				new_cpu_time_sum = 0
				prev_memory_stats = 0
				new_memory_stats = 0
				
				prev_cpu_stats = dom.getCPUStats(True)
				prev_mem_stats  = dom.memoryStats()
				prev_network_stats = dom.interfaceStats(iface)				

				time.sleep(domain_interval)
				
				new_cpu_stats = dom.getCPUStats(True)
				new_mem_stats = dom.memoryStats()
				new_network_stats = dom.interfaceStats(iface)

				cpu_util = getdomCPUUtil(new_cpu_stats[0], prev_cpu_stats[0], 0.2)
				mem_util = getMemoryUtil(new_mem_stats, prev_mem_stats, 0.2)
				network_util = getNetworkUtil(new_network_stats, prev_network_stats, 0.2 )

				if val.get(domainID) == None:
					val[domainID] = {'mem': [], 'cpu' : [], "network": []}

				val[domainID]['mem'].append(mem_util)
				val[domainID]['cpu'].append(cpu_util)
				val[domainID]['network'].append(network_util)

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
		return averages





while True:
	ls = []
	for host_name in conn_dict:
		try:
			# 	hotspot_detector(host_name)
			th = threading.Thread(target=hotspot_detector, args=(host_name,))
			ls.append(th)
			th.start()
		except:
			print("Unable to run hotspot detector thread %s"%(host_name))
			raise
	for th in ls:
		th.join()
	print(host_stats)
	for host in host_stats:
		host_stat = host_stats[host]
		if host_stat['hotspot']:
			domain_info_hotspot = find_domain(host)
			dom_tobe = filterDomain(domain_info_hotspot, True)
			if dom_tobe == -1:
				continue
			min_sc = 10000000
			host_nam = -1
			for host1 in host_stats:
				if host_stats[host1]['hotspot'] == False and host_stats[host1].get('marked') == None:
					if host_stats[host1]['score'] < min_sc:
						min_sc = host_stats[host1]['score']
						host_nam = host1
			if host_nam == -1:
				print("Unable to find minload node for overload %s"%(host))
				continue
			host_stats[host_nam]['marked'] = True
			domain_info_repl = find_domain(host_nam)
			dom_with = filterDomain(domain_info_repl, False)
			#Do migrate
			conn_hotspot = conn_dict[host]
			conn_minload = conn_dict[host_nam]
			print("Migration of %d at %s with %d at %s"%(dom_tobe,host,dom_with,host_nam))
			dom_tobe = conn_hotspot.lookupByID(dom_tobe)
			if dom_with != -1:
				dom_with = conn_minload.lookupByID(dom_with)
			dom_tobe.migrate(conn_minload, 0, None, None, 0)
			if dom_with != -1:
				dom_with.migrate(conn_hotspot, 0, None, None, 0)
		# else:
	time.sleep(hotspot_detect_interval)





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

