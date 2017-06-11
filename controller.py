import requests
import sys
import getch

while (True):
	#x = input(">>> Control: ")
	x = getch.getch()
	r = requests.post('http://140.113.89.234:8888', data={'control': x})
	print(r)

