import csv
import os
from flask import Flask, redirect, url_for, render_template, request, send_file, session
from passlib.context import CryptContext

class streetlamp:

	def __init__(self, num=0, streetlampid=0, nodemcuid=0, ledstatus=0, ldrstatus=0, latitude=0.0, longitude=0.0):
		self.num = num
		self.streetlampid = streetlampid
		self.nodemcuid = nodemcuid
		self.latitude = latitude
		self.ledstatus = ledstatus
		self.ldrstatus = ldrstatus
		self.longitude = longitude

	def putlist(self, itemlist):
		self.num = itemlist[0]
		self.streetlampid = itemlist[1]
		self.nodemcuid = itemlist[2]
		self.ledstatus = itemlist[3]
		self.ldrstatus = itemlist[4]
		self.latitude = itemlist[5]
		self.longitude = itemlist[6]

	def getList(self):
		return [self.num, self.streetlampid, self.nodemcuid, self.ledstatus, self.ldrstatus, self.latitude, self.longitude]

	def printItem(self):
		print("{},{},{},{},{},{},{}".format(self.num, self.streetlampid, self.nodemcuid, self.ledstatus, self.ldrstatus, self.latitude, self.longitude))

	def getcsvtext(self):
		return str("{},{},{},{},{},{},{}".format(self.num, self.streetlampid, self.nodemcuid, self.ledstatus, self.ldrstatus, self.latitude, self.longitude))

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

def appendData(num=0, streetlampid=0, nodemcuid=0, ledstatus=0, ldrstatus=0, latitude=0.0, longitude=0.0):
	newstreetlamp = streetlamp(num,streetlampid,nodemcuid,ledstatus,ldrstatus,latitude,longitude)
	newstreetlamptext = newstreetlamp.getcsvtext()
	with open('database.csv','a') as fd:
		fd.write(newstreetlamptext)

def putData(streetlamps):
	with open('database.csv','w') as fd:
		fd.write('num,streetlampid,nodemcuid,ledstatus,ldrstatus,latitude,longitude\n')
		for streetlamp in streetlamps:
			streetlamptext = streetlamp.getcsvtext()
			fd.write(streetlamptext)

def toggleOn(num):
	newstreetlamps = getData()
	newstreetlamps[num-1].ledstatus = '1'
	putData(newstreetlamps)

def toggleOff(num):
	newstreetlamps = getData()
	newstreetlamps[num-1].ledstatus = '0'
	putData(newstreetlamps)

def toggleldrOn(num):
	newstreetlamps = getData()
	newstreetlamps[num-1].ldrstatus = '1'
	putData(newstreetlamps)

def toggleldrOff(num):
	newstreetlamps = getData()
	newstreetlamps[num-1].ldrstatus = '0'
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

@app.route("/", methods=["POST", "GET"])
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

@app.route("/on")
def on():
	toggleOn(1)
	return redirect(url_for('control'))

@app.route("/off")
def off():
	toggleOff(1)
	return redirect(url_for('control'))

@app.route("/ldron")
def ldron():
	toggleldrOn(1)
	return redirect(url_for('control'))

@app.route("/ldroff")
def ldroff():
	toggleldrOff(1)
	return redirect(url_for('control'))

@app.route("/control", methods=["POST", "GET"])
def control():

	if 'user' in session:
		if request.method == "POST":
			if request.form['submit_button'] == 'on':
				return redirect(url_for('on'))
			if request.form['submit_button'] == 'off':
				return redirect(url_for('off'))
			if request.form['submit_button'] == 'ldron':
				return redirect(url_for('ldron'))
			if request.form['submit_button'] == 'ldroff':
				return redirect(url_for('ldroff'))		
			if request.form['submit_button'] == 'back':
				return redirect(url_for('index'))

		return render_template("control.html")

	return redirect(url_for("auth"))

@app.route("/passwordchange", methods=["POST", "GET"])
def passwordchange():

	if 'user' in session:
	#if AUTHFLAG:
		hashpswrd = ""
		f = open("password.txt", "r")
		hashpswrd = f.readlines()[0]
		f.close()
		if request.method == "POST":
			print(request.form['submit_button'])
			if request.form['submit_button'] == 'back':
				return redirect(url_for('settings'))
			if request.form['submit_button'] == 'Done':
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
				else:
					return render_template("passwordchange.html", warn="Incorrect password.")
			return render_template("passwordchange.html", warn="An error occured. Please try again.")
		else:
			return render_template("passwordchange.html")

@app.route("/settings", methods=["POST", "GET"])
def settings():

	if 'user' in session:
		if request.method == "POST":
			if request.form['submit_button'] == 'Change Password':
				return redirect(url_for('passwordchange'))
			if request.form['submit_button'] == 'back':
				return redirect(url_for('index'))		
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
	ledstatus = str(streetlamps[0].ledstatus)
	ldrstatus = str(streetlamps[0].ldrstatus)

	if idname == 'lamp001':
		return "{}{}".format(ledstatus,ldrstatus)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True, use_reloader=True)
