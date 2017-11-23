from  __future__ import print_function
import sys
import libvirt


if len(sys.argv) == 1:
	conn = libvirt.open('qemu:///system')
else:
	conn = libvirt.open('qemu+ssh://'+ str(sys.argv[1])+'/system')
if conn == None:
	print('Failed to open connection to qemu:///system', file=sys.stderr)
	exit(1)


statsList = conn.getCPUStats(1)
print(len(statsList))
for stats in statsList:
	print("kernel: " + str(stats['kernel']))
	print("idle:   " + str(stats['idle']))
	print("user:   " + str(stats['user']))
	print("iowait: " + str(stats['iowait']))

conn.close()
exit(0)

