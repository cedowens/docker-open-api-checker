# Python3 Script to Check for Remote Unauth Docker API Access

python3 script that sweeps a subnet for docker on ports 2375 and 2376 and then checks for unauthenticated API access.

this script is largely based on the research done by Chris Gates (@carnal0wnage):

http://carnal0wnage.attackresearch.com/2019/02/abusing-docker-api-socket.html

Dependency:

requires requests library (pip3 install requests)

Usage:

python3 -W ignore docker-open-api-checker.py -r [network_range] -t [number_of_threads] 

Note: I use the -W ignore to ignore any warnings associated with attempting to connect to ssl sites, as this site checks for both 2375 (http) and 2376 (ssl).

This script does not launch any attacks...it simply looks for misconfigured docker hosts allowing remote unauth API access.

Additional things you can do once you find a docker host configured this way can be found here:

http://carnal0wnage.attackresearch.com/2019/02/abusing-docker-api-socket.html
