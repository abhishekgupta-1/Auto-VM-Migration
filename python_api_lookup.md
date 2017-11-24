#### [API Link](https://libvirt.org/docs/libvirt-appdev-guide-python/en-US/pdf/Version-1.1-Libvirt_Application_Development_Guide_Using_Python-en-US.pdf)

1. conn = libvirt.open
2. domainsIds = conn.listDomainIds
3. 



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

### Virtual Networks
1. After installation of libvirt, every host will get a single virtual network instance called 'default', which provides DHCP services to guests and allows NAT'd IP connectivity to the host's interfaces. This service is of most use to hosts with intermittent network connectivity. For example, laptops using wireless networking.
2