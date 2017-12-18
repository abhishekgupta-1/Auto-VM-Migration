from __future__ import print_function
import sys
import libvirt
from threading import Timer
import time

def getCPUStats(cpu_stats):
	cpu_time_sum = 0
	for (i, cpu) in enumerate(cpu_stats):
		print('CPU '+str(i)+' Time: '+str(cpu['cpu_time'] / 1000000000.))
		prev_cpu_time_sum += cpu['cpu_time']
	return cpu_time_sum

def getMemoryStats(stats):
	memory_stats = 0
	print('memory used:')
	for name in stats:
		print('  '+str(stats[name])+' ('+name+')')
		memory_stats += stats[name]	
	return memory_stat
s
if len(sys.argv) == 1:
	conn = libvirt.open('qemu:///system')
else:
	conn = libvirt.open('qemu+ssh://'+ str(sys.argv[1])+'/system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)
domainIDs = conn.listDomainsID()
print("Active domain IDs:")
if len(domainIDs) == 0:
	print('  None')
	exit(0)
else:
	for domainID in domainIDs:
		print('  '+str(domainID))
		dom = conn.lookupByID(domainID)
		if dom == None:
		    print('Failed to find the domain ', file=sys.stderr)
		    exit(1)

		interval = 0.05
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
		
		for (i, cpu) in enumerate(cpu_stats):
		   print('CPU '+str(i)+' Time: '+str(cpu['cpu_time'] / 1000000000.))
		   new_cpu_time_sum += cpu['cpu_time'] 
		print('memory used:')
		for name in stats:
		    print('  '+str(stats[name])+' ('+name+')')
		    new_memory_stats = stats[name]
		
		cpu_util = (new_cpu_time_sum - prev_cpu_time_sum)/interval *1000000000.

		mem_util = (new_memory_stats - prev_memory_stats)/interval 
		print(mem_util)
		print(cpu_util)

conn.close()
exit(0)
