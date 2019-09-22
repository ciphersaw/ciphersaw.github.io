# Python 3.6
import requests
import base64 

url = 'http://ctf5.shiyanbar.com/web/10/10.php'
headers = requests.get(url).headers
key = base64.b64decode(headers['FLAG']).decode().split(':')[1]
post = {'key': key}
print(requests.post(url, data = post).text)