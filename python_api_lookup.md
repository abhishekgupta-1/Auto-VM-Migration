#### [API Link](https://libvirt.org/docs/libvirt-appdev-guide-python/en-US/pdf/Version-1.1-Libvirt_Application_Development_Guide_Using_Python-en-US.pdf)

1. conn = libvirt.open
2. domainsIds = conn.listDomainsID || conn.listDefinedDomains() //Returns list
3. domainIdObjs = conn.listAllDomains(VIR_CONNECT_LIST_DOMAINS_ACTIVE)
4. lookupByID, lookupByName and lookupByUUID
5. struct = dom.getTime(), timestamp = time.ctime(float(struct['seconds']))
6. rd_req, rd_bytes, wr_req, wr_bytes, err = \
dom.blockStats('/path/to/linux-0.2.img')
print('Read requests issued: '+str(rd_req))
print('Bytes read:
'+str(rd_bytes))
print('Write requests issued: '+str(wr_req))
print('Bytes written:
'+str(wr_bytes))
print('Number of errors:
'+str(err))
7. cpu_stats = dom.getCPUStats(False)
for (i, cpu) in enumerate(cpu_stats):
print('CPU '+str(i)+' Time: '+str(cpu['cpu_time'] / 1000000000.))
8. stats = dom.getCPUStats(True)
print('cpu_time:
'+str(stats[0]['cpu_time']))
print('system_time: '+str(stats[0]['system_time']))
print('user_time:
'+str(stats[0]['user_time']))
9. stats = dom.memoryStats()
print('memory used:')
for name in stats:
print(' '+str(stats[name])+' ('+name+')')
10. To get the network statistics, you'll need the name of the host interface that the domain is connected to (usually vnetX). To find it, retrieve the domain XML description (libvirt modifies it at the runtime). Then, look for devices/interface/target[@dev] element(s):
11. tree = ElementTree.fromstring(dom.XMLDesc())
iface = tree.find('devices/interface/target').get('dev')
stats = dom.interfaceStats(iface)
print('read bytes:
'+str(stats[0]))
print('read packets: '+str(stats[1]))
print('read errors:
'+str(stats[2]))
print('read drops:
'+str(stats[3]))
print('write bytes:
'+str(stats[4]))
print('write packets: '+str(stats[5]))
print('write errors: '+str(stats[6]))
print('write drops:
'+str(stats[7]))
12. 


## Notes

### Hypervisor connection
1. A connection is the primary or top level object in the libvirt API and Python libvirt module. An instance of this object is required before attempting to use almost any of the classes or methods. A connection is associated with a particular hypervisor, which may be running locally on the same machine as the libvirt client application, or on a remote machine over the network. In all cases, the connection is represented by an instance of the virConnect class and identified by a URI. The URI scheme and path defines the hypervisor to connect to, while the host part of the URI determines where it is located.
2. An application is permitted to open multiple connections at the same time, even when using more than one type of hypervisor on a single machine. For example, a host may provide both KVM full machine virtualization and LXC container virtualization. A connection object may be used concurrently across multiple threads. Once a connection has been established, it is possible to obtain handles to other managed objects or create new managed objects, as discussed in Section 2.1.2, “Guest domains”.



### Guest Domain
1. A guest domain can refer to either a **running virtual machine or a configuration** that can be used to launch a virtual machine. The connection object provides methods to **enumerate the guest domains, create new guest domains and manage existing domains**. A guest domain is represented with an instance of the virDomain class and has a number of unique identifiers.
2. ####Unique Identifiers
2.1 __ID__: positive integer, **unique** amongst running guest domains on a single host. An inactive domain does not have an ID
2.2 __name__: short string, **unique amongst all guest domains on a single host**, both running and inactive. 
3. A guest domain may be transient or persistent. A transient guest domain can only be managed while it is running on the host. Once it is powered off, all trace of it will disappear. A persistent guest domain has its configuration maintained in a data store on the host by the hypervisor, in an implementation defined format. Thus when a persistent guest is powered off, it is still possible to manage its inactive configuration. A transient guest can be turned into a persistent guest while it is running by defining a configuration for it.
4. Typically domain IDs will not be re-used until the entire ID space wraps around. The domain ID space is at least 16 bits in size, but often extends to 32 bits

### Virtual Networks
1. After installation of libvirt, every host will get a single virtual network instance called 'default', which provides DHCP services to guests and allows NAT'd IP connectivity to the host's interfaces. This service is of most use to hosts with intermittent network connectivity. For example, laptops using wireless networking.
2