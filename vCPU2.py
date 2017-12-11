from __future__ import print_function
import sys
import libvirt
from threading import Timer
import time
def getCPUTimeSum(cpu_stats):
	cpu_time_sum = 0
	for (i, cpu) in enumerate(cpu_stats):
		# print('CPU '+str(i)+' Time: '+str(cpu['cpu_time'] / 1000000000.))
		cpu_time_sum += cpu['cpu_time'] + cpu['system_time']
	return cpu_time_sum

def getMemoryStats(stats):
	print(stats)
	memory_stats = stats['rss']
	# print('memory used:')
	#for name in stats:
		# print('  '+str(stats[name])+' ('+name+')')
	#	memory_stats += stats[name]	
	
	return memory_stats

if len(sys.argv) == 1:
	conn = libvirt.open('qemu:///system')
else:
	conn = libvirt.open('qemu+ssh://'+ str(sys.argv[1])+'/system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)
domainIDs = conn.listDomainsID()

if len(domainIDs) == 0:
	print('  None')
	exit(0)
else:
	cpu_stat_dict = {}
	mem_stat_dict = {}
	k_val = 7
	n_val = 20
	cpu_thres = 150
	mem_thres = 150
	k_cpu_val_dict = {}
	k_mem_val_dict = {}
	while True:
		val = {}
		for domainID in domainIDs:
			print('Active domain:  '+str(domainID))
			dom = conn.lookupByID(domainID)
			if dom == None:
			    print('Failed to find the domain ', file=sys.stderr)
			    exit(1)
			interval = 0.01
			prev_cpu_time_sum = 0
			new_cpu_time_sum = 0
			prev_memory_stats = 0
			new_memory_stats = 0

			cpu_stats = dom.getCPUStats(True)
			stats  = dom.memoryStats()
			
			prev_cpu_time_sum = getCPUTimeSum(cpu_stats)
			prev_memory_stats = getMemoryStats(stats)
			
			print("Interval of", interval, "seconds")
			time.sleep(interval)
			
			cpu_stats = dom.getCPUStats(True)
			
			stats = dom.memoryStats()
			new_cpu_time_sum = getCPUTimeSum(cpu_stats)
			new_memory_stats = getMemoryStats(stats)
			
			
			cpu_util = (new_cpu_time_sum - prev_cpu_time_sum)/(interval*10000000)
			mem_util = (new_memory_stats + prev_memory_stats)/(2) 
			lis = cpu_stat_dict.get(domainID)
			memlis = mem_stat_dict.get(domainID)
			if lis == None:
				lis = []
				memlis = []
				k_cpu_val_dict[domainID] = 0
				k_mem_val_dict[domainID] = 0
			if len(lis) == n_val:
				if lis[0] > cpu_thres:
					k_cpu_val_dict[domainID] -= 1
				if memlis[0] > mem_thres:
					k_mem_val_dict[domainID] -= 1
				lis = lis[1:]
				memlis = memlis[1:]
			lis.append(cpu_util)
			memlis.append(mem_util)
			if cpu_util > cpu_thres:
				k_cpu_val_dict[domainID] += 1
			if mem_util > mem_thres:
				k_mem_val_dict[domainID] += 1
			cpu_stat_dict[domainID] = lis
			mem_stat_dict[domainID] = memlis
			val[domainID] = {"CPU":cpu_util, "MEM":mem_util}
			if k_cpu_val_dict[domainID] > k_val or k_mem_val_dict[domainID] > k_val: #Migrate this
				print("Domain id %d should be migrated!"%(domainID))
		print(val)
		time.sleep(3)


# print("Active domain IDs:")
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



conn.close()
exit(0)
