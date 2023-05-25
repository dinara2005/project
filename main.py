from flask import Flask, render_template,request,url_for,redirect, session, flash
from functools import wraps

import psycopg2

app = Flask(__name__)

app.secret_key = 'super proj'

class usr():
    
    def __init__(self, id_usr, name=None, surname=None, age=None, status=None, inst=None, auth=None ):

        self.id_usr = id_usr
        self.name =  name
        self.surname = surname
        self.age = age
        self.status = status
        self.inst = inst
        self.auth = auth

        print(f"auth usr {name}")


def get_connection():
    connection = psycopg2.connect(user="postgres",
                                  password="1234",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="db_for_site")
    return connection

def check_login(login, password):

    try:
        
        cursor = connection.cursor()
        postgreSQL_select_Query = "select id_usr from usr_auth where login = %s and password = %s"

        cursor.execute(postgreSQL_select_Query, (login,password, ))
        record = cursor.fetchall()
        if record is not None:
            return record[0]
        else:
            return None
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None
    
def is_admin(id_usr):
    try:
        
        cursor = connection.cursor()
        postgreSQL_select_Query = "select is_admin from usr_auth where id_usr = %s"

        cursor.execute(postgreSQL_select_Query, (id_usr, ))
        record = cursor.fetchall()
        if record is not None:
            return record[0]
        else:
            return None
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None
   
            
def get_info(id_usr):
    
    try:
        
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from usr_data where id_usr = %s"

        cursor.execute(postgreSQL_select_Query, (id_usr, ))
        record = cursor.fetchall()
        if record is not None:
            record = record[0]
            return usr(record[0],record[1],record[2],record[3],record[4],record[5],True)
        else:
            return None
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None

def get_info_about_post(post_id=None):
    
    try:
        cursor = connection.cursor()
        
        if post_id is not None:
            
            postgreSQL_select_Query = "select * from post_info where post_id = %s"

            cursor.execute(postgreSQL_select_Query, (post_id, ))
            
        else:
            postgreSQL_select_Query = "select * from post_info"

            cursor.execute(postgreSQL_select_Query, (post_id, ))
            
        record = cursor.fetchall()
        if record is not None:
            return record
        else:
            return None    
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None

def update_info(id_usr, request):
    
    
    try:
       
        cursor = connection.cursor()
        postgreSQL_update_Query = "update usr_data set name=%s,surname=%s,age=%s,status=%s,name_institution=%s where id_usr = %s"

        cursor.execute(postgreSQL_update_Query, (request.form['name'],request.form['surname'],request.form['age'],request.form['status'],request.form['inst'], id_usr, ))
        connection.commit()
        
        
        
        return "GOOD"
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None

def add_info(request):
    try:
       
        cursor = connection.cursor()
        postgreSQL_insert_Query = "insert into post_info (name,description,link) VALUES (%s, %s, %s)"

        cursor.execute(postgreSQL_insert_Query, (request.form['name'],request.form['description'],request.form['link']))
        connection.commit()

        return "GOOD"
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None
    
def del_post(request):
    try:
       
        cursor = connection.cursor()
        postgreSQL_insert_Query = "DELETE FROM post_info WHERE id_post = %s"

        cursor.execute(postgreSQL_insert_Query, (request.form['movie_to_delete'],))
        connection.commit()

        return "GOOD"
    
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        return None
    
    
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
#@login_required
def index():
    global user
    
    if 'logged_in' in session:
        data = {"auth" : True, "name" : user.name}
    else:
        data = {"auth" : False}
        
    return render_template('index.html', data=data )

@app.route('/physics')
def physics():
    global user
    
    if 'logged_in' in session:
        data = {"auth" : True, "name" : user.name}
    else:
        data = {"auth" : False}
        
    return render_template('physics.html',data=data )

@app.route('/robotics')
def robotics():
    global user
    
    if 'logged_in' in session:
        data = {"auth" : True, "name" : user.name}
    else:
        data = {"auth" : False}
    return render_template('robotics.html', data=data)

@app.route('/profile')
@login_required
def profile():
    global user
    try:
        user = get_info(user.id_usr)
        return render_template(
            'profile.html',
            name = user.name,
            surname = user.surname,
            age = user.age,
            status = user.status,
            inst = user.inst)
    
    except Exception as e:
        print(e)    
        return redirect(url_for('logout'))
                           

@app.route('/info')
@login_required
def info():
    global user
    try:
        inf = get_info_about_post()
        v = is_admin(user.id_usr)[0]
        print(inf)
        return render_template('for_auth_users.html', data = v, inf = inf)
    except Exception as e:
        print(e)    
        return redirect(url_for('logout'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    error = None
    if request.method == 'POST':
        res = check_login(request.form['username'], request.form['password'])
        if res is None :
            error = 'Invalid Credentials. Please try again.'
        else:
            
            user = get_info(res)
            session['logged_in'] = True
            flash('You were logged in.')
            return render_template(
                'profile.html',
                name = user.name,
                surname = user.surname,
                age = user.age,
                status = user.status,
                inst = user.inst)
        
    return render_template('login.html', error=error)



@app.route('/profile_update', methods=['POST'])
@login_required
def update_profile():
    global user
    
    
    if request.method == 'POST':
        res = update_info(user.id_usr, request)
        
        if res is not None:
            return redirect(url_for('profile'))
        else:
            return render_template('profile.html')




@app.route('/add_new_post', methods=['POST'])
@login_required
def add_post():
    global user
    if is_admin(user.id_usr)[0]:
        if request.method == 'POST':
            res = add_info(request)
           
            
            if res is not None:
                return redirect(url_for('info'))
            else:
                return render_template('profile.html')

@app.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
    global user
    if is_admin(user.id_usr)[0]:
        if request.method == 'POST':
            res = del_post(request)
           
            
            if res is not None:
                return redirect(url_for('info'))
            else:
                return render_template('profile.html')
           
        

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('physics'))

    

if __name__ == '__main__':
    
    connection = get_connection()
    user = usr(None)
    app.run(debug = True)















    
