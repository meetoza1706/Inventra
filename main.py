from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
import uuid
import datetime
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = '1707'  # Use a strong secret key
CORS(app)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventra'

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
    # If user is already logged in, redirect to dashboard
    if session.get('user_logged_in'):
        return redirect(url_for('dashboard'))
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
    # Check if the user is already logged in, if so, redirect to the dashboard
    if session.get('user_logged_in'):
        return jsonify({"status": "success", "message": "Already logged in"}), 200

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            cur = mysql.connection.cursor()
            query = "SELECT * FROM user_data WHERE username = %s AND password = %s"
            cur.execute(query, (username, password))
            user = cur.fetchone()

            if user:
                # Create session data
                session_id = str(uuid.uuid4())  # Generate a unique session ID
                login_time = datetime.datetime.now()
                expiration_time = login_time + datetime.timedelta(hours=1)  # Session expires in 1 hour

                # Insert session data into the sessions table
                insert_query = "INSERT INTO sessions (session_id, user_id, login_time, expiration_time, is_active) VALUES (%s, %s, %s, %s, %s)"
                cur.execute(insert_query, (session_id, user[0], login_time, expiration_time, 1))
                mysql.connection.commit()

                # Store session data
                session['session_id'] = session_id
                session['user_logged_in'] = True
                session['username'] = username  # Store username in session
                session['user_id'] = user[0]  # Store user_id in session

                # Return success status
                return jsonify({"status": "success", "message": "Login successful"}), 200
            else:
                return jsonify({"status": "failure", "message": "Invalid username or password"}), 401

        except Exception as err:
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            cur.close()

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # Clear all session ata
    return redirect(url_for('login'))  # Redirect to login page after logout


@app.route('/company_register', methods=['POST', 'GET'])
def company_register():
    if request.method == 'POST':
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
            
            user_id = session.get('user_id')
            print(user_id)

            insert_query = """
                INSERT INTO company_data (company_name, email, contact_number, website, date_established, status, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query, (company_name, email, contact_number, website, established_date, status, user_id))
            mysql.connection.commit()

            return jsonify({"status": "success", "message": "Company registered successfully"}), 201
        except Exception as err:
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            cur.close()

    return render_template('company_register.html')

@app.route('/company_find', methods=['POST', 'GET'])
def company_find():
    companies = None  # Variable to store the search results

    if request.method == 'POST':
        search = request.form.get('search')  # Get search query from form

        try:
            cur = mysql.connection.cursor()

            # SQL query to search for companies by name (case-insensitive search)
            query = "SELECT company_name, email FROM company_data WHERE company_name LIKE %s"
            cur.execute(query, ('%' + search + '%',))  # Search using LIKE with % for partial match
            companies = cur.fetchall()  # Fetch all matching companies

        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred", 500
        finally:
            if 'cur' in locals():
                cur.close()

    return render_template('company_find.html', companies=companies)

@app.route('/dashboard')
def dashboard():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))

    username = session.get('username', None)
    user_id, first_name, company_name = None, None, None

    try:
        cur = mysql.connection.cursor()

        # Fetch first_name and user_id from user_data table
        cur.execute("SELECT first_name, user_id FROM user_data WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            first_name, user_id = user

        # Fetch company_name from company_data table if user_id exists
        if user_id:
            cur.execute("SELECT company_name FROM company_data WHERE user_id = %s", (user_id,))
            company = cur.fetchone()
            if company:
                company_name = company[0]
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        cur.close()

    return render_template('dashboard.html', username=username, first_name=first_name, company_name=company_name)

@app.route('/pricing', methods=['GET','POST'])
def pricing():
    return render_template('pricing.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

# @app.route('/features')
# def features():
#     return render_template('features.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    user_id = session.get('user_id')
    
    try:
        cur = mysql.connection.cursor()

        # Fetch email and username for the given user_id
        fetch_query = """
            SELECT email, username 
            FROM user_data 
            WHERE user_id = %s
        """
        cur.execute(fetch_query, (user_id,))
        user_data = cur.fetchone()

        if not user_data:
            return jsonify({"status": "error", "message": "User not found"}), 404

        email, username = user_data

    except Exception as err:
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cur.close()

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        try:
            cur = mysql.connection.cursor()

            # Update first_name and last_name in the user_data table
            update_query = """
                UPDATE user_data
                SET first_name = %s, last_name = %s
                WHERE user_id = %s
            """
            cur.execute(update_query, (first_name, last_name, user_id))
            mysql.connection.commit()

            return jsonify({"status": "success", "message": "User data updated successfully"}), 200
        except Exception as err:
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            cur.close()

    # Render the template with email and username for GET requests
    return render_template("profile.html", email=email, username=username)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
