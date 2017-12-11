from __future__ import print_function
import sys
import libvirt

domName = sys.argv[1]
print(domName)

conn = libvirt.open('qemu:///system')
if conn == None:
    print('Failed to open connection to qemu:///system', file=sys.stderr)
    exit(1)

dest_conn = libvirt.open('qemu+ssh://'+sys.argv[2]+'/system')
if conn == None:
    print('Failed to open connection to qemu+ssh://desthost/system', file=sys.stderr)
    exit(1)

dom = conn.lookupByName(domName)
if dom == None:
    print('Failed to find the domain '+domName, file=sys.stderr)
    exit(1)

new_dom = dom.migrate(dest_conn, 0, None, None, 0)
if new_dom == None:
    print('Could not migrate to the new domain', file=sys.stderr)
    exit(1)

print('Domain was migrated successfully.', file=sys.stderr)

dest_conn.close()
conn.close()
exit(0)
