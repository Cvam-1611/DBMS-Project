from flask import Flask, request, jsonify, render_template,redirect, url_for, session
from flask_mysqldb import MySQL
import random
import MySQLdb.cursors
import re
import pickle
from nltk.util import in_idle
import pandas as pd
import numpy  as np
import nltk
import string
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk import pos_tag
lemmatizer = WordNetLemmatizer()

from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer

#####################FUNCTIONS FOR PREPROCESSING##########################
def get_simple_pos(tag) :
    if tag.startswith('J') :
        return wordnet.ADJ
    elif tag.startswith('V') :
        return wordnet.VERB
    elif tag.startswith('N') :
        return wordnet.NOUN
    elif tag.startswith('R') :
        return wordnet.ADV
    else:
        return wordnet.NOUN

#nltk.download('stopwords')
stops = set(stopwords.words('english'))
punctuations = list(string.punctuation)
stops.update(punctuations)
stops

#cleaning
def clean_review(review) :
    words = word_tokenize(review)
    output_words = []
    for w in words :
        if w.lower() not in stops :
            pos = pos_tag([w])
            clean_word = lemmatizer.lemmatize(w,pos = get_simple_pos(pos[0][1]))
            output_words.append(clean_word.lower())
    #print(output_words)
    return " ".join(output_words)

##########################################################################

#creating an instance for the flask app
app = Flask(__name__)
app.secret_key = 'SMRS'
#Configure database
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Summer@2019'
app.config['MYSQL_DB']='SMRS'

db=MySQL(app)

#Loading The ML model using pickle
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template("home.html")
    
@app.route('/login' , methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        username=request.form['username']
        password=request.form['password']
        

        #check if account exists in Database
        cursor=db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from accounts where username=%s and password=%s',(username,password,))
        account = cursor.fetchone()
        
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            admin=account['admin']
            print(admin)
            if admin==1:
                return render_template("admin.html")
            else:
                cursor=db.connection.cursor(MySQLdb.cursors.DictCursor)
                resultvalue=cursor.execute('SELECT * from movie')
                if resultvalue>0:
                    moviedetails=cursor.fetchall()
                    print(moviedetails)
                    
                    return render_template('movie.html',moviedetails=moviedetails)

        else:
            msg='Incorrect username/password!'
    return render_template("home.html",msg=msg)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password"POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        name=request.form['name']
        age=request.form['age']
        gender=request.form['gender']
        city=request.form['city']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            
            admin=0
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s,%s,%s)', (username, password,name,age,gender,city,admin,))
            db.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route("/aboutus")
def about():
    return render_template("AboutUs.html")



@app.route("/list", methods=['POST'])
def hello():
    id = request.form.get("movieDropdown")
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    print('user_ID:',session['id'])
    result=cursor.execute('SELECT user_id,username,city,review,rating FROM mov_review join movie on movie.mov_id=mov_review.mov_id join accounts on  mov_review.user_id=accounts.id where movie.mov_id = %s', (id,))

    review=cursor.fetchall()
    cursor.execute('SELECT * from movie where mov_id=%s',(id,))
    movie=cursor.fetchall()
    print(review)
    return render_template("index.html" ,review=review,id=id, movie=movie)

#    code for cursor and database
    
    
@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI'''
    phrase= request.form['Review']
    text=phrase
    id=request.form['id']
    print(phrase,id)

    phrase = [(clean_review(phrase))]

    count_vec = pickle.load(open('count_vec.pkl','rb'))
    test = count_vec.transform(phrase)
    prediction = model.predict(test)[0]
    prediction=prediction+1

    cursor=db.connection.cursor(MySQLdb.cursors.DictCursor)
    n = random.randint(0,10000)
    
    # data=cursor.execute('Select user_id FROM mov_review join movie on movie.mov_id=mov_review.mov_id join accounts on  mov_review.user_id=accounts.id where movie.mov_id = %s', (id,))
    # user_id=cursor.fetchall()
    # user_id=user_id[0]['user_id']
    # if session.get("KEY"):
    #     user_id=session['id']
    # else:
    #     return render_template("login.html")
    user_id=session['id']
    print('USER_ID2: ',user_id)
    print(n,id,text,prediction,user_id)
    cursor.execute('INSERT INTO mov_review VALUES (%s, %s, %s, %s, %s)', (n,id,text,prediction,user_id,))
    db.connection.commit()
    result=cursor.execute('SELECT user_id,username,city,review,rating FROM mov_review join movie on movie.mov_id=mov_review.mov_id join accounts on  mov_review.user_id=accounts.id where movie.mov_id = %s', (id,))
    review=cursor.fetchall()
    cursor.execute('SELECT * from movie where mov_id=%s',(id,))
    movie=cursor.fetchall()
    return render_template('index.html',review=review,id=id,movie=movie)

@app.route("/addmovies" ,methods=['POST'])
def addmovies():
    msg=''
    mov_id=random.randint(0,10000)
    if request.method=='POST' and 'movie_name' in request.form and 'release_date' in request.form and 'actor' in request.form and 'img' in request.form and 'Description' in request.form:

        movie_name=request.form['movie_name']
        release_date=request.form['release_date']
        actor=request.form['actor']
        img=request.form['img']
        Description=request.form['Description']

        cursor=db.connection.cursor(MySQLdb.cursors.DictCursor)
        print(mov_id,movie_name,release_date,actor,img,Description)
        cursor.execute('INSERT INTO movie VALUES (%s, %s, %s, %s, %s, %s)', (mov_id,movie_name,release_date,actor,img,Description,))
        db.connection.commit()
        msg='Movie added Successfully'
    return render_template("admin.html",msg=msg)

    

if __name__ == "__main__":
    app.run(debug=True)
