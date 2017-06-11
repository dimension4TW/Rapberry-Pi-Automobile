import tornado.ioloop
import tornado.web
import time
import shlex, subprocess
import os
import signal
import queue
import base64


class MainHandler(tornado.web.RequestHandler):
	def set_default_headers(self):
		#print("setting headers!")
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "x-requested-with")
		self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
		
	def post(self):
		global mode
		global pro
		global q #queue to store struction
		control = self.get_argument('control', '')
		img_exist = self.get_argument('img_exist', '')
		if img_exist == '1': 
			img = self.get_argument('img', '')
			current_time = time.strftime("%m-%d-%Y--%H-%M", time.localtime())
			print(current_time)
			f = open('./picture/'+current_time+".jpg", 'wb')
			print(img)
			bimg = base64.b64decode(img)
			f.write(bimg)
			#print(img)
			f.close()
			print("get image")
		print(control)
		if control == 'w' and mode == 'mode2':
			q.put('w')
		elif control == 'a'and mode == 'mode2':
			q.put('a')
		elif control == 's'and mode == 'mode2':
			q.put('s')
		elif control == 'd'and mode == 'mode2':
			q.put('d')
		elif control == 'k' and mode == 'mode2':
			q.put('k')
		elif control == 'q':
			if(mode=="mode1"):
				mode = "mode2"
			else:
				mode = "mode1"
		self.write("ok")

	def get(self):
		global mode
		global q
		if(mode == "mode1"):
			dir = "x"
		else:
			if(q.empty()):
				dir = "x"
			else:
				dir = q.get()
		re = {"mode":mode, "dir":dir}
		self.write(re)

def make_app():
	return tornado.web.Application([
		(r"/", MainHandler),
	])

if __name__ == "__main__":

    app = make_app()
    app.listen(8888)
    print ('server running: 0.0.0.0:8888')
    global mode
    global q
    q = queue.Queue()
    mode = "mode1"
    tornado.ioloop.IOLoop.current().start()
