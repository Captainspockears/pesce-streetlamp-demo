import csv
import os
from flask import Flask, redirect, url_for, render_template, request, send_file, session
from passlib.context import CryptContext

class streetlamp:

	def __init__(self, num=0, streetlampid=0, nodemcuid=0, status=False, latitude=0.0, longitude=0.0):
		self.num = num
		self.streetlampid = streetlampid
		self.nodemcuid = nodemcuid
		self.latitude = latitude
		self.status = status
		self.longitude = longitude

	def putlist(self, itemlist):
		self.num = itemlist[0]
		self.streetlampid = itemlist[1]
		self.nodemcuid = itemlist[2]
		self.status = itemlist[3]
		self.latitude = itemlist[4]
		self.longitude = itemlist[5]

	def getList(self):
		return [self.num, self.streetlampid, self.nodemcuid, self.status, self.latitude, self.longitude]

	def printItem(self):
		print("{},{},{},{},{},{}".format(self.num, self.streetlampid, self.nodemcuid, self.status, self.latitude, self.longitude))

	def getcsvtext(self):
		return str("{},{},{},{},{},{}".format(self.num, self.streetlampid, self.nodemcuid, self.status, self.latitude, self.longitude))

def getData():
	streetlamps = []
	with open('database.csv', 'r') as f:
		reader = csv.reader(f)
		next(reader)
		for row in reader:
			streetlamptemp = streetlamp()
			streetlamptemp.putlist(row)
			streetlamps.append(streetlamptemp)
	return streetlamps

def appendData(num=0, streetlampid=0, nodemcuid=0, status=False, latitude=0.0, longitude=0.0):
	newstreetlamp = streetlamp(num, code, name, catagory, allocatedto, desc, loc, date, ID)
	newstreetlamptext = newstreetlamp.getcsvtext()
	with open('database.csv','a') as fd:
		fd.write(newstreetlamptext)

def putData(streetlamps):
	with open('database.csv','w') as fd:
		fd.write('num,streetlampid,nodemcuid,status,latitude,longitude\n')
		for streetlamp in streetlamps:
			streetlamptext = streetlamp.getcsvtext()
			fd.write(streetlamptext)

def toggleOn(num):
	newstreetlamps = getData()
	newstreetlamps[num-1].status = True
	putData(newstreetlamps)

def toggleOff(num):
	newstreetlamps = getData()
	newstreetlamps[num-1].status = False
	putData(newstreetlamps)


pwd_context = CryptContext(
	schemes=["pbkdf2_sha256"],
	default="pbkdf2_sha256",
	pbkdf2_sha256__default_rounds=30000
)

def encrypt_password(password):
	return pwd_context.hash(password)


def check_encrypted_password(password, hashed):
	return pwd_context.verify(password, hashed)

#CODE STARTS HERE
app = Flask(__name__, template_folder='static', static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'key'#os.urandom(24)

@app.route("/")
def home():

	if 'user' in session:
		if request.method == "POST":
			if request.form['submit_button'] == 'Control Lights':
				return redirect(url_for('control'))
			if request.form['submit_button'] == 'Settings':
				return redirect(url_for('settings'))

		return render_template("index.html")

	return redirect(url_for("auth"))

@app.route("/index", methods=["POST", "GET"])
def index():

	if 'user' in session:
		if request.method == "POST":
			if request.form['submit_button'] == 'Control Lights':
				return redirect(url_for('control'))
			if request.form['submit_button'] == 'Settings':
				return redirect(url_for('settings'))

		return render_template("index.html")

	return redirect(url_for("auth"))

@app.route("/control", methods=["POST", "GET"])
def control():

	if 'user' in session:
		if request.method == "POST":
			if request.form['submit_button'] == 'ON':
				return redirect(url_for('on'))
			if request.form['submit_button'] == 'OFF':
				return redirect(url_for('off'))
			if request.form['submit_button'] == 'back':
				return redirect(url_for('index'))

		return render_template("control.html")

	return redirect(url_for("auth"))

@app.route("/on")
def on():
	toggleOn(1)
	return redirect(url_for('control'))

@app.route("/off")
def off():
	toggleOff(1)
	return redirect(url_for('control'))

@app.route("/passwordchange", methods=["POST", "GET"])
def passwordchange():

	if 'user' in session:
	#if AUTHFLAG:
		hashpswrd = ""
		f = open("password.txt", "r")
		hashpswrd = f.readlines()[0]
		f.close()
		if request.method == "POST":
			try:
				curr=request.form["curr"]
				upt=request.form["upt"]
				if curr=="" or upt=="":
					return render_template("passwordchange.html", warn="Incomplete fields.")
				if curr==upt:
					return render_template("passwordchange.html", warn="Passwords cannot be the same.")
				if check_encrypted_password(curr,hashpswrd):
					print("Saving new password: {}".format(upt))
					f1 = open("password.txt", "w")
					hashpswrd = encrypt_password(upt)
					print(hashpswrd)
					f1.write(hashpswrd)
					f1.close()
					return redirect(url_for("auth"))
				return render_template("passwordchange.html", warn="Incorrect password.")
			except Exception as e:
				print(e)
				return render_template("passwordchange.html", warn="Incomplete fields.")
		else:
			return render_template("passwordchange.html")

@app.route("/settings")
def settings():

	if 'user' in session:
		return render_template("settings.html")

	return redirect(url_for("auth"))

@app.route("/auth", methods=["POST", "GET"])
def auth():

	f = open("password.txt", "r")
	hashpswrd = f.readlines()[0]
	f.close()
	if request.method == "POST":
		try:
			password=request.form["password"]
			if password=="":
				return render_template("auth.html", warn="Incomplete fields.")
			if check_encrypted_password(password,hashpswrd):
				print("password correct")
				session['user'] = 'Hello'
				try:
					return redirect(url_for('index'))
				except:
					return redirect(url_for("user", idname=currentpage))
			return render_template("auth.html", warn="Incorrect credential. Please try again.")
		except Exception as e:
			print("Fail: {}".format(e))
			return render_template("auth.html", warn="Incomplete fields.")
	else:
		return render_template("auth.html")



@app.route("/<idname>")
def user(idname):

	streetlamps = getData()
	status = str(streetlamps[0].status)

	if idname == 'lamp001':
		return status

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, use_reloader=True)
