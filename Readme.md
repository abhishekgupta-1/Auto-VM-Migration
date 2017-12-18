Done in team effort:-
1. Vidhi Jain (2014A7TS0113P)
2. Abhishek Gupta (2014A7PS0026P)

========================================================

Previous attempts in old_Report.pdf


Implementation using libvirt:-


List of hosts in host_list variable

The task implemented:-
1. Hotspot among the physical machines
2. Detecting machine with lowest VSR
3. Profiling the virtual machines
4. Migration of the highest VSR VM on hotspot with lowest VSR VM on lowest node

cpu_utilization = delta(cpu_time+system_time)/(time_interval)


Pseudo code:
Repeat:
	Get utilization of each host node
	add the utilization to the window
	check hotspot criteria
	for hotspots:
		get highest VSR VM
		get node with lowest load
		get lower VSR VM in the lowest load VM
		do migration
