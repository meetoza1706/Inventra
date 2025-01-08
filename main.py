from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session
from flask_mysqldb import MySQL
import uuid
import datetime
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = '1707'
CORS(app) 

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventra'

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        
        if password == cpassword:
            try:
                cur = mysql.connection.cursor()
                # Check if user already exists
                query = "SELECT username, email FROM user_data WHERE username = %s AND email = %s"
                cur.execute(query, (username, email))
                user = cur.fetchone()
                
                if user:
                    return jsonify({"status": "failure", "message": "User already exists"}), 409
                else:
                    # Insert new user
                    insert_query = "INSERT INTO user_data (username, email, password) VALUES (%s, %s, %s)"
                    cur.execute(insert_query, (username, email, password))
                    mysql.connection.commit()
                    return jsonify({"status": "success", "message": "User registered successfully"}), 201
            except Exception as err:
                return jsonify({"status": "error", "message": str(err)}), 500
            finally:
                cur.close()
        else:
            return jsonify({"status": "failure", "message": "Passwords do not match"}), 400
    
    return render_template('sign_up.html')  

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            cur = mysql.connection.cursor()
            query = "SELECT * FROM user_data WHERE username = %s AND password = %s"
            cur.execute(query, (username, password))
            user = cur.fetchone()

            if user:
                print("you have logged in")

                # Create session data
                session_id = str(uuid.uuid4())  # Generate a unique session ID
                login_time = datetime.datetime.now()
                expiration_time = login_time + datetime.timedelta(hours=1)  # Example: session expires in 1 hour

                # Insert session data into the sessions table
                insert_query = "INSERT INTO sessions (session_id, user_id, login_time, expiration_time, is_active) VALUES (%s, %s, %s, %s, %s)"
                cur.execute(insert_query, (session_id, user[0], login_time, expiration_time, 1))  # Adjust index for tuple
                mysql.connection.commit()

                session['session_id'] = session_id
                print("session created")
                return jsonify({"status": "success", "message": "Login successful"})

            else:
                print("no log in")
                return jsonify({"status": "failure", "message": "Invalid username or password"}), 401

        except Exception as err:
            print("error", err)
            return jsonify({"status": "error", "message": str(err)}), 500

        finally:
            cur.close()

    return render_template('login.html')       

@app.route('/company_register', methods=['POST', 'GET'])
def company_register():
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        website = request.form.get('website')
        email = request.form.get('email')
        established_date = request.form.get('established_date')
        contact_number = request.form.get('contact_number')
        status = request.form.get('status')

        try:
            cur = mysql.connection.cursor()

            # Check if company already exists
            query = "SELECT company_name, email FROM company_data WHERE company_name = %s AND email = %s"
            cur.execute(query, (company_name, email))
            company = cur.fetchone()

            if company:
                return jsonify({"status": "failure", "message": "Company already exists"}), 409

            # Insert new company data
            insert_query = """
                INSERT INTO company_data (company_name, email, contact_number, website, date_established, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query, (company_name, email, contact_number, website, established_date, status))
            mysql.connection.commit()

            return jsonify({"status": "success", "message": "Company registered successfully"}), 201
        except Exception as err:
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            cur.close()

    return render_template('company_register.html')

@app.route('/company_find', methods=['POST', 'GET'])
def company_find():
    if request.method == 'POST':
        search = request.form.get('search')
        print(search)
    return render_template('company_find.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True) 