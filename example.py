import imssh

def target(device):
    try:
        s = imssh.connect(username=device.username, password=device.password, host=device.host, port=device.port)
        s.execute("sudo ls -l", 1)

    except Exception as e:
        print(imssh.format_exc())
        pass

target(imssh.Host("smartcow@192.168.0.175 smartcow"))
# with imssh.open("hosts") as hosts:
#     imssh.map(target=target, args=hosts.get('nx'))