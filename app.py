from flask import Flask, flash, render_template, request, redirect
from werkzeug import generate_password_hash, check_password_hash
import MySQLdb as my 
import yaml
from get_movie import *

"""This File uses MySQL ONLY"""

app = Flask(__name__)
db = my.connect(ADDRESS, USERNAME, PASSWORD, "login")
app.secret_key = KEY
home_address = "http://%s:%d" % (ADDRESS, PORT)
USN = ''
EMAIL = ''

# ___________________________________________________ #
"""Home Page """


@app.route('/')
def home():
    print "home"
    return render_template('index.html', addr=home_address)
# ___________________________________________________ #
"""Sign up and Sign in functions"""


@app.route('/signup')
def signup_help():
    global USN, EMAIL
    email = EMAIL
    USN = EMAIL = ''
    print "signup", USN, EMAIL
    return render_template('sign.html', type=1, email=email, username='')


@app.route('/signin')
def signin_help():
    global USN, EMAIL
    username = USN
    USN = EMAIL = ''
    print "signin", USN, EMAIL
    return render_template('sign.html', type=2, email='', username=username)


@app.route('/main', methods=['POST', 'GET'])
def sign_up_in():
    global EMAIL, USN
    print "main"
    if request.method == 'POST':
        result = request.form
        print "Result:", result
    if result['email']:                           # If email present : it means it is sign up, else sign in!
        dump_to_json('signup.json', result)         # Temporarily write to json, the db funcs will use this to insert or validate.
        if not update_db():
            EMAIL = result['email']
            return redirect('/signup')
        return redirect('/movie')    
    else:
        dump_to_json('signin.json', result)
        if check_with_db():
            return redirect('/movie')
        else:
            flash("Please Try Again")
            USN = result['username']
            return redirect('/signin')


@app.route('/movie')
def movie():
    print "movie"
    return render_template('movie.html')

# ___________________________________________________________ #
"""Results from api: Use get_movie.py"""


@app.route('/results', methods=['POST', 'GET'])
def results():
    print "results"
    if request.method == 'POST':    
        result = request.form
    try:
        movie_info = get_movie(result['Title'].encode('utf-8'))
        return render_template('results.html', dict=movie_info)
    except:
        flash("Invalid, try again!")
        return redirect('/movie')


@app.route('/senti')
def senti():
    f = open('movie.json', 'r').read()
    parsed_json = yaml.safe_load(f)
    senti_dict = senti_analysis(parsed_json['Title'])
    return render_template('senti.html', list=senti_dict['document_tone']['tone_categories'])

# ______________________________________________________ #


@app.route('/logout')
def logout():
    """
    # Try Later if time permits
    query = "delete UserName from logged_users where UserName ..."
    """
    dump_to_json("signin.json", {})
    dump_to_json("signup.json", {})
    return home()
    
# _______________________________________________________ #
"""Database stuff"""


def check_with_db():
    f = open('signin.json').read() 
    f = json.loads(f)
    password = f['password']
    sql = "Select password from user where userName = '" + f['username'] + "';"
    try:
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        data = list(cursor.fetchone()) + [password]
        return check_password_hash(data[0], data[1])
    except:
        db.rollback()
        return False


def update_db():
    f = open('signup.json').read()
    f = json.loads(f)
    password = generate_password_hash(f['password'])
    try:
        sql = "insert into user values('" + f['username'] + "','" + f['email'] + "' ,'"+ password +"');"
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        return False
    return True

# _______________________________________________________ #

if __name__ == "__main__":
    app.run(debug=True, port=PORT)

