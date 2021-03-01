import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Defining the function that opens sqlite database and creates table


def create_student_table():
    connect = sqlite3.connect('database.db')
    print("Databases has opened")

    connect.execute('CREATE TABLE IF NOT EXISTS users (id_no INTEGER PRIMARY KEY , fullname TEXT, surname TEXT, contact TEXT, pin TEXT )')
    print("Table was created successfully")
    connect.close()


create_student_table()


def create_admin_table():
    con = sqlite3.connect('database.db')
    con.execute('CREATE TABLE IF NOT EXISTS admin (adminID INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    print("Admin table was created successfully")
    con.close()


create_admin_table()


def add_admin():
    username = "admin"
    password = "admin"
    conn = sqlite3.connect('database.db')
    conn.execute('INSERT INTO admin (username, password) VALUES(?, ?)', (username, password))
    conn.commit()
    print("Admin has been created")
    conn.close()


add_admin()




# Route for opening the registration form and rendering template
@app.route('/')
@app.route('/register-student/', methods=['GET'])
def register_form():
    return render_template('register.html')


# Fetching form info and adding user to database
@app.route('/')
@app.route('/add-student/', methods=['POST'])
def add_student():
    try:
        id_no = request.form['id']
        fullname = request.form['fullname']
        surname = request.form['surname']
        contact = request.form['contact']
        pin = request.form['pin']
        confirm = request.form['confirm']

        if pin == confirm:
            with sqlite3.connect('database.db') as con:
                cursor = con.cursor()
                cursor.execute("INSERT INTO users (id_no, fullname, surname, contact, pin ) VALUES (?, ?, ?, ?, ?)", (id_no, fullname, surname, contact, pin))
                con.commit()
                msg = fullname + " was added to the databases"
    except Exception as e:
        con.rollback()
        msg = "Error occured in insert" + str(e)
    finally:
        con.close()
    return jsonify(msg=msg)


@app.route('/show-students/', methods=['GET'])
def show_students():
    students = []
    try:
        with sqlite3.connect('database.db') as connect:
            connect.row_factory = dict_factory
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM users")
            students = cursor.fetchall()
    except Exception as e:
        connect.rollback()
        print("There was an error fetching results from the database: " + str(e))
    finally:
        connect.close()
        return jsonify(students)


@app.route('/login/', methods=['GET'])
def login():
    msg = None
    try:
        id_no = request.form['id']
        fullname = request.form['fullname']        
        pin = request.form['pin']

        with sqlite3.connect('database.db') as con:
            con.row_factory = dict_factory
            mycursor = con.cursor()
            mycursor.execute('SELECT * FROM users WHERE id_no = ? and fullname = ? and pin = ?', (id_no, fullname, pin))
            data = mycursor.fetchone()
            msg = fullname + " has logged in."
    except Exception as e:
        con.rollback()
        msg = "There was a problem logging in try again later " + str(e)
    finally:
        con.close()
    return jsonify(data, msg=msg)



@app.route('/show-admin/', methods=['GET'])
def show_admin():
    try:
        with sqlite3.connect('database.db') as connect:
            connect.row_factory = dict_factory
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM admin WHERE username = ? and pin=?", ("admin", "admin"))
            admin = cursor.fetchone()
    except Exception as e:
        connect.rollback()
        print("There was an error fetching results from the database: " + str(e))
    finally:
        connect.close()
    return jsonify(admin)





if __name__ == '__main__':
    app.run(debug=True)