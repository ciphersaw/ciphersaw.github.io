# Python 3.6
import requests
import base64 

# Solution 1: Use Session Object
url = 'http://120.24.86.145:8002/web6/'
s = requests.Session()
headers = s.get(url).headers
key = base64.b64decode(base64.b64decode(headers['flag']).decode().split(":")[1])
post = {"margin": key} 
print(s.post(url, data = post).text)

# Solution 2: Only use requests with constructing cookies 
# url = 'http://120.24.86.145:8002/web6/'
# headers = requests.get(url).headers
# key = base64.b64decode(base64.b64decode(headers['flag']).decode().split(":")[1])
# post = {"margin": key} 
# PHPSESSID = headers["Set-Cookie"].split(";")[0].split("=")[1]
# cookie = {"PHPSESSID": PHPSESSID}
# print(requests.post(url, data = post, cookies = cookie).text)