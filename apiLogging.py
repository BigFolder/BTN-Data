import requests
import logging
import time
import http.client
import socket
import requests.packages.urllib3.util.connection as urllib3_cn

http.client.HTTPConnection.debuglevel = 1

# Init. Logging to see debug output
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

'''
# timeout=unspecified
# Time taken: 42.26596641540527 Seconds
# timeout=5
# Time taken: 10.717306852340698 Seconds
# timeout=1
# Time taken: 2.184016704559326 Seconds
# Update to urllib3  IPV6 -> IPV4
# Time taken: 0.2540280818939209 Seconds
'''

# Uses Socket and Requests urllib3_cn to FORCE IPV4 family


def allowed_gai_family():
	"""
	 https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
	"""
	family = socket.AF_INET
	return family


urllib3_cn.allowed_gai_family = allowed_gai_family

start = time.time()
requests.get("https://api.rotf.io/account/info/by-name/Kebbels")
end = time.time()
print("Time taken:", end-start, "Seconds")
