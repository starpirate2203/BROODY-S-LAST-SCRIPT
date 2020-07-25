# -*- coding: utf-8 -*-
import bs

# Returns your local and static IP Adress in bs.Lstr object, uses in bsUI (address check tab)

local = static = None
local_lstr = static_lstr = None

no_connection_text = bs.Lstr(resource='gatherWindow.noConnectionText')

def get_local_ip_address():
    global local
    import socket
    s = socket.socket(2, 2)
    s.settimeout(1.0)
    try: s.connect(("8.8.8.8", 80))
    except Exception: return no_connection_text
    else:
        local = ip = s.getsockname()[0]
        s.close()
        return bs.Lstr(value=ip)
    
def get_static_ip_address():
    global static
    import socket
    ip = ''
    request = bytes(
        "GET / HTTP/1.1\r\n"+
        "Host: api.ipify.org\r\n"+
        "Connection: Close\r\n\r\n")
    s = socket.socket(2, 1)
    s.settimeout(1.0)
    try: s.connect(("api.ipify.org", 80))
    except Exception: return no_connection_text
    else: 
        s.sendall(request)
        while True:
            try: chunk = s.recv(8)
            except Exception: chunk = None
            if not chunk: break
            if chunk is not None: ip+=chunk
        if len(ip) > 0: ip = ip.split('\n')[-1]
        else: return no_connection_text
        s.close()
    static = ip
    return bs.Lstr(value=ip)

local_lstr = get_local_ip_address()
if local is not None: print("Local IP-Address: "+local)
static_lstr = get_static_ip_address()
if static is not None: print("Static IP-Address: "+static)