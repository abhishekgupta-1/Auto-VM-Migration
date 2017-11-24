=====================Architecture=======================


1. 10 VMs will be running on each of the 5 physical machines.
2. A controller node will be running.
3. The controller node will fetch usage statistics from each physical node and plot the usage, VM wise and physical machine wise.
4. Determine hotspot occurence.
5. Do live migration.


=========================Tasks===========================

Initial
1. Run two virtual machines on a physical machine.
2. Write a script for the controller node to get the usage statistics.



Fancy
1. Plot the statistics received from the domains



========================Precautions======================
1. Use lowest common denominator for CPU configuration. See **cpu-baseline** command of virsh
2. All the guests, even on different hosts, should have a unique name



========================QUESTIONS========================

1. Push or pull mechanism?
2. How to connect guests to the network? How does bridge work? 
Use **