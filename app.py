from flask import Flask,flash,render_template, json, request,redirect,url_for,jsonify
from werkzeug import generate_password_hash, check_password_hash
import MySQLdb as my 
import json
from get_movie import*

"""This File uses MySQL ONLY"""

app = Flask(__name__)
db = my.connect("localhost","root","themenwhopause","login" )
app.secret_key='123456'

#___________________________________________________#
"""Stupid Home Page """

@app.route('/')
def home():
	return render_template('index.html')
#____________________________________________________#
"""Sign up and Sign in functions"""

@app.route('/signup_help')
def signup_help():
	return render_template('form.html')

@app.route('/signin_help')
def signin_help():
	return render_template('signin_form.html')

@app.route('/main',methods = ['POST','GET'])
def sign_up_in():
	if request.method == 'POST':
		result = request.form 
		#print result
	try:
		print result['email']				# If email present : it means it is sign up, else sign in!
		with open('signup.json','w') as f:
			f.write(json.dumps(result))		#Temporarily write to json, the db funcs will use this to insert or validate.
		update_db()
		return render_template('main.html')	
	except:
		with open('signin.json','w') as f:
			f.write(json.dumps(result))

		if check_with_db():
			return render_template('main.html')
		else:
			flash("Please Try Again")
			return render_template('login_fail.html')

#___________________________________________________________#
"""Results from api: Use get_movie.py"""

@app.route('/results',methods = ['POST','GET'])
def results():
	if request.method == 'POST':	
		result = request.form 
		#print result
	try:
		movie_info = get_movie(result['Title'].encode('utf-8'))
		print movie_info
		return render_template('results.html',dict = movie_info)
	except:
		flash("Invalid, try again!")

#______________________________________________________#
@app.route('/logout')
def logout():
	"""
	#Try Later if time permits
	query = "delete UserName from logged_users where UserName ..."
	"""
	pass
	
#_______________________________________________________#

"""Database stuff"""

def check_with_db():
	f = open('signin.json').read() 
	f = json.loads(f)
	password = f['password']
	sql = "Select password from user where UserName = \'" + f['username'] + "\';"
	try:
		cursor = db.cursor()
		cursor.execute(sql)
		db.commit()
		data = list(cursor.fetchone()) + [password]
		#print data 
		return check_password_hash(data[0],data[1])
	except:
		db.rollback()
		return False

def update_db():
	f = open('signup.json').read() 
	f = json.loads(f)
	password = generate_password_hash(f['password'])
	try:
		sql = "insert into user values(\'" + f['username'] + "\',\'" + f['email'] + "\' ,\'"+ password +'\')'+';'
		print sql
		cursor = db.cursor()
		cursor.execute(sql)
		db.commit()
		print'Success-> commit'
	except:
		print"Nope rollback!!"
		db.rollback()

#_______________________________________________________#

if __name__ == "__main__":
	app.run(port=5000)

