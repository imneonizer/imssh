import imssh

def target(device):
    try:
        # connect to remove device via ssh
        s = imssh.connect(username=device.username, password=device.password, host=device.host, port=device.port)

        # execute command and print output
        output = s.execute("hostname", pprint=1)

    except Exception as e:
        print(imssh.format_exc())

# execute on single device
target(imssh.Host("<username>@<ip-address> <password>"))

# execute on multiple devices
# with imssh.open("hosts") as hosts:
#     imssh.map(target=target, args=hosts.all)

# example host file:
# [group1]
# <username>@<ip-address> <password>
# <username>@<ip-address>:<port>!<ssh-keys-path> <password>