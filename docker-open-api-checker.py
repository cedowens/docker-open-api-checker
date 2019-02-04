import socket
import sys
import ipaddress
from ipaddress import IPv4Address, IPv4Network
import threading
from queue import Queue
import requests
from optparse import OptionParser

if ((len(sys.argv) < 5 or len(sys.argv) > 5) and '-h' not in sys.argv):
    print("Usage:")
    print("%s -r <range> -t <threads>" % sys.argv[0])
    sys.exit(1)

parser = OptionParser()
parser.add_option("-r", "--range", help="Network range to spray")
parser.add_option("-t", "--threads", help="Number of threads to use")
(options, args) = parser.parse_args()

print("\033[1;36m<============================================================================>")
print("                          _   _   _   _   _   _")
print("                         / \ / \ / \ / \ / \ / \\")
print("                        | D | o | c | k | e | r |")
print("                         \_/ \_/ \_/ \_/ \_/ \_/")
print('')
print("                          _   _   _   _    _   _   _")
print("                         / \ / \ / \ / \  / \ / \ / \\")
print("                        | O | p | e | n || A | P | I |")
print("                         \_/ \_/ \_/ \_/  \_/ \_/ \_/") 
print('')
print("                          _   _   _   _   _   _   _")
print("                         / \ / \ / \ / \ / \ / \ / \\") 
print("                        | C | h | e | c | k | e | r |")
print("                         \_/ \_/ \_/ \_/ \_/ \_/ \_/\033[0m")
print('')
print("Author: @cedowens")
print("Checks a subnet for docker hosts allowing remote unauth API access.")
print("Based on research done by Chris Gates (@carnal0wnage) at:")
print("http://carnal0wnage.attackresearch.com/2019/02/abusing-docker-api-socket.html")
print("\033[1;36m<============================================================================>\033[0m")


dockerhosts = []
iplist = []
dockercount = 0
iprange = options.range
numthreads = options.threads
portopenlist = []
portopenlist2 = []
print('')
print("Checking %s..." % options.range)
print('')

def Connector(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.8)
        result = sock.connect_ex((str(ip),2375))
        sock.close()
        if result == 0:
            print("\033[92mPort 2375 OPEN on %s\033[0m" % str(ip))
            portopenlist.append(str(ip))
        else:
            pass
        
    except Exception as e:
        print(e)


def Connector2(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.8)
        result = sock.connect_ex((str(ip),2376))
        sock.close()
        if result == 0:
            print("\033[92mPort 2376 OPEN on %s\033[0m" % str(ip))
            portopenlist2.append(str(ip))
        else:
            pass
        
    except Exception as e:
        print(e)

def threader():
    while True:
        worker = q.get()
        worker4 = q4.get()
        Connector(worker)
        Connector2(worker)
        q.task_done()
        q4.task_done()



def dockerchecker(host):
    url = 'http://' + host + ':2375/containers/json'

    try:
        response = requests.get(url, timeout=1)
        if (response.status_code == 200 and 'Names' in response.text and "Id" in response.text):
            print("+"*100)
            print("\033[91m--->Docker host found - can remotely list containers: %s\033[0m" % url)
            dockerhosts.append(url)
            dockercount = dockercount + 1
    except requests.exceptions.RequestException:
        pass



def dockerchecker2(host):
    url2 = 'https://' + host + ':2376/containers/json'
    
    try:
        response4 = requests.get(url2, verify=False, timeout=1)
        if (response4.status_code == 200 and 'Names' in response4.text and "Id" in response4.text):
            print("+"*100)
            print("\033[91m--->Docker host found - can remotely list containers: %s\033[0m" % url2)
            dockerhosts.append(url2)
            dockercount = dockercount + 1
            
    except requests.exceptions.RequestException:
        pass

def threader2():
    while True:
        worker2 = q2.get()
        dockerchecker(worker2)
        q2.task_done()

q = Queue()

q4 = Queue()

for ip in ipaddress.IPv4Network(iprange):
    iplist.append(str(ip))
    
for x in range(int(numthreads)):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()



for worker in iplist:
    q.put(worker)

for worker4 in iplist:
    q4.put(worker4)

q.join()
q4.join()

def threader3():
    while True:
        worker3 = q3.get()
        dockerchecker2(worker3)
        q3.task_done()

q2 = Queue()

for y in range(int(numthreads)):
    t2 = threading.Thread(target=threader2)
    t2.daemon = True
    t2.start()

for worker2 in portopenlist:
    item = str(ipaddress.IPv4Address(worker2))
    q2.put(item)

q2.join()

q3 = Queue()

for z in range(int(numthreads)):
    t3 = threading.Thread(target=threader3)
    t3.daemon = True
    t3.start()

for worker3 in portopenlist2:
    item = str(ipaddress.IPv4Address(worker3))
    q3.put(item)

q3.join()

if (len(portopenlist) == 0 or len(portopenlist2) == 0):
    print("+"*100)
    print("No docker hosts listening on ports 2375 or 2376 were found.")
elif (dockercount == 0 and (len(portopenlist) > 0 or len(portopenlist2) > 0)):
    print("+"*100)
    print("No docker hosts allowing unauthenticated remote listing of containers found.")
elif dockercount > 0:
    print("+"*100)
    print("It looks like you found docker hosts allowing unauthenticated listing of containers.")
    print("You can follow the steps from Chris Gates' post to expand your access:")
    print("Link to Chris Gates post: http://carnal0wnage.attackresearch.com/2019/02/abusing-docker-api-socket.html")
else:
    pass
        
print("+"*100)
print("DONE!")
print("+"*100)
