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
        
        if password != cpassword:
            return jsonify({"status": "failure", "message": "Passwords do not match"}), 400
        
        try:
            cur = mysql.connection.cursor()
            # Check if user already exists
            query = "SELECT username, email FROM user_data WHERE username = %s OR email = %s"
            cur.execute(query, (username, email))
            user = cur.fetchone()
            
            if user:
                return jsonify({"status": "failure", "message": "User already exists"}), 409
            else:
                # Insert new user into user_data using the correct column name
                insert_query = "INSERT INTO user_data (username, email, password_hash) VALUES (%s, %s, %s)"
                cur.execute(insert_query, (username, email, password))
                mysql.connection.commit()
                return jsonify({"status": "success", "message": "User registered successfully"}), 201
        except Exception as err:
            print("Registration error:", err)
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            cur.close()
    
    return render_template('sign_up.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('user_logged_in'):
        return jsonify({"status": "success", "message": "Already logged in"}), 200

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            cur = mysql.connection.cursor()
            # Use password_hash column in your query
            query = "SELECT * FROM user_data WHERE username = %s AND password_hash = %s"
            cur.execute(query, (username, password))
            user = cur.fetchone()
            print(user)

            if user:
                session_id = str(uuid.uuid4())
                login_time = datetime.datetime.now()
                expiration_time = login_time + datetime.timedelta(hours=1)

                # Insert session data into the sessions table
                insert_query = "INSERT INTO sessions (session_id, user_id, login_time, expiration_time, is_active) VALUES (%s, %s, %s, %s, %s)"
                cur.execute(insert_query, (session_id, user[0], login_time, expiration_time, 1))
                mysql.connection.commit()

                session['session_id'] = session_id
                session['user_logged_in'] = True
                session['username'] = username
                session['user_id'] = user[0]

                return jsonify({"status": "success", "message": "Login successful"}), 200
            else:
                return jsonify({"status": "failure", "message": "Invalid username or password"}), 401

        except Exception as err:
            print("Login error:", err)
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
            # Check if company exists
            query = "SELECT company_name, email FROM company_data WHERE company_name = %s AND email = %s"
            cur.execute(query, (company_name, email))
            if cur.fetchone():
                return jsonify({"status": "failure", "message": "Company already exists"}), 409
            
            user_id = session.get('user_id')
            # Insert new company
            insert_query = """
                INSERT INTO company_data (company_name, email, contact_number, website, date_established, status, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_query, (company_name, email, contact_number, website, established_date, status, user_id))
            company_id = cur.lastrowid
            # Set the company creator as Admin (role_id 1) and update company_id in user_data
            cur.execute("UPDATE user_data SET company_id = %s, role_id = %s WHERE user_id = %s", (company_id, 1, user_id))
            mysql.connection.commit()
            return jsonify({"status": "success", "message": "Company registered successfully"}), 201
        except Exception as err:
            mysql.connection.rollback()
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            cur.close()
    return render_template('company_register.html')

# @app.route('/process_join_request', methods=['POST'])
# def process_join_request():
#     if not session.get('user_logged_in'):
#         return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

#     admin_user_id = session.get('user_id')
#     try:
#         cur = mysql.connection.cursor()
#         # Verify current user is an Admin
#         cur.execute("SELECT role_id, company_id FROM user_data WHERE user_id = %s", (admin_user_id,))
#         admin_info = cur.fetchone()
#         if not admin_info or admin_info[0] != 1:
#             return jsonify({'status': 'error', 'message': 'Not authorized'}), 403
#         admin_company_id = admin_info[1]

#         data = request.get_json()
#         request_id = data.get('request_id')
#         decision = data.get('decision')  # Should be 'accepted' or 'rejected'
#         if not request_id or decision not in ['accepted', 'rejected']:
#             return jsonify({'status': 'error', 'message': 'Invalid input'}), 400

#         # Fetch join request details
#         cur.execute("SELECT user_id, company_id FROM join_requests WHERE request_id = %s", (request_id,))
#         join_req = cur.fetchone()
#         if not join_req:
#             return jsonify({'status': 'error', 'message': 'Join request not found'}), 404
#         join_user_id, join_company_id = join_req
#         if join_company_id != admin_company_id:
#             return jsonify({'status': 'error', 'message': 'Request does not belong to your company'}), 403

#         # Update request status
#         cur.execute("UPDATE join_requests SET status = %s WHERE request_id = %s", (decision, request_id))
#         if decision == 'accepted':
#             # Assign default role Employee (role_id 3) and set company_id for the joining user
#             cur.execute("UPDATE user_data SET company_id = %s, role_id = %s WHERE user_id = %s", (admin_company_id, 3, join_user_id))
#         mysql.connection.commit()
#         return jsonify({'status': 'success', 'message': f'Request {decision}.'})
#     except Exception as e:
#         mysql.connection.rollback()
#         return jsonify({'status': 'error', 'message': str(e)}), 500
#     finally:
#         cur.close()


# @app.route('/company_find', methods=['POST', 'GET'])
# def company_find():
#     companies = None  # Variable to store the search results

#     if request.method == 'POST':
#         search = request.form.get('search')  # Get search query from form

#         try:
#             cur = mysql.connection.cursor()

#             query = "SELECT company_name, email FROM company_data WHERE company_name LIKE %s"
#             cur.execute(query, ('%' + search + '%',))  # Search using LIKE with % for partial match
#             companies = cur.fetchall()  # Fetch all matching companies
#             print(companies)

#         except Exception as e:
#             print(f"Error: {e}")
#             return "An error occurred", 500
#         finally:
#             if 'cur' in locals():
#                 cur.close()

#     return render_template('company_find.html', companies=companies)


@app.route('/company_find', methods=['POST', 'GET'])
def company_find():
    companies = None  # Variable to store the search results

    if request.method == 'POST':
        # Support both JSON and form submissions:
        if request.is_json:
            search = request.json.get('search')
        else:
            search = request.form.get('search')
        
        try:
            cur = mysql.connection.cursor()
            query = "SELECT company_name FROM company_data WHERE company_name LIKE %s"
            cur.execute(query, ('%' + search + '%',))  # Search using LIKE with % for partial match
            # For JSON response, extract company names (assuming company_name is in first column)
            companies = [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(f"Error: {e}")
            if request.is_json:
                return jsonify({"status": "error", "message": "Database error"}), 500
            else:
                return "An error occurred", 500
        finally:
            cur.close()

        # If request is JSON (AJAX), return JSON response:
        if request.is_json:
            return jsonify({"status": "success", "companies": companies})
    
    # For normal GET requests, render the template with companies (if any)
    return render_template('company_find.html', companies=companies)

@app.route('/dashboard')
def dashboard():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))

    username = session.get('username')
    first_name, user_id, role_name, company_name = None, None, None, None
    apps_to_display = []

    try:
        cur = mysql.connection.cursor()
        # Fetch user details along with company info via company_id
        cur.execute("""
            SELECT u.first_name, u.user_id, r.role_name, c.company_name
            FROM user_data u
            LEFT JOIN roles r ON u.role_id = r.role_id
            LEFT JOIN company_data c ON u.company_id = c.company_id
            WHERE u.username = %s
        """, (username,))
        user_info = cur.fetchone()
        if user_info:
            first_name, user_id, role_name, company_name = user_info
            print("DEBUG: company_name =", company_name)  # Debug: Check if company_name is fetched
        else:
            return redirect(url_for('login'))

        # Fetch apps available for the user's role
        if role_name:
            cur.execute("""
                SELECT a.app_name, a.app_description 
                FROM role_permissions rp
                JOIN apps a ON rp.permissions = a.app_id
                WHERE rp.role_name = %s
            """, (role_name,))
            role_apps = cur.fetchall()
            apps_to_display.extend(
                [{"app_name": app[0], "app_description": app[1]} for app in role_apps]
            )

        # Fetch apps manually added by the user
        if user_id:
            cur.execute("""
                SELECT a.app_name, a.app_description 
                FROM user_apps ua
                JOIN apps a ON ua.app_id = a.app_id
                WHERE ua.user_id = %s AND ua.added_to_dashboard = TRUE
            """, (user_id,))
            user_apps = cur.fetchall()
            apps_to_display.extend(
                [{"app_name": app[0], "app_description": app[1]} for app in user_apps]
            )
    except Exception as e:
        print("Error fetching data:", e)
    finally:
        cur.close()

    return render_template('dashboard.html',
                           username=username,
                           first_name=first_name or '',
                           company_name=company_name or '',
                           apps=apps_to_display)

# @app.route('/company_join', methods=['POST'])
# def company_join():
#     user_id = session.get('user_id')
#     company_name = request.json.get('company_name')

#     if not user_id or not company_name:
#         return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

#     try:
#         cur = mysql.connection.cursor()

#         # Get company ID
#         cur.execute("SELECT company_id FROM company_data WHERE company_name = %s", (company_name,))
#         company = cur.fetchone()

#         if not company:
#             return jsonify({'status': 'error', 'message': 'Company not found'}), 404

#         company_id = company[0]

#         # Check if there's an existing pending request for this company
#         cur.execute("""
#             SELECT status FROM join_requests WHERE user_id = %s AND company_id = %s
#         """, (user_id, company_id))
#         existing_request = cur.fetchone()

#         if existing_request:
#             if existing_request[0] == 'pending':
#                 return jsonify({'status': 'error', 'message': 'You already have a pending request for this company'}), 400
#             elif existing_request[0] == 'accepted':
#                 return jsonify({'status': 'error', 'message': 'You are already part of this company'}), 400

#         # Insert request into join_requests table
#         cur.execute("INSERT INTO join_requests (user_id, company_id, status) VALUES (%s, %s, 'pending')",
#                     (user_id, company_id))
#         mysql.connection.commit()

#         return jsonify({'status': 'success', 'message': 'Request sent to admin'})

#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500
#     finally:
#         cur.close()
 
# @app.route('/get_requests', methods=['GET'])
# def get_requests():
#     user_id = session.get('user_id')
    
#     if not user_id:
#         return jsonify({'status': 'error', 'message': 'Not logged in'}), 401

#     try:
#         cur = mysql.connection.cursor()
        
#         # Fetch requests for the logged-in admin
#         cur.execute("""
#             SELECT ar.request_id, u.username, c.company_name 
#             FROM access_requests ar
#             JOIN user_data u ON ar.user_id = u.user_id
#             JOIN company_data c ON ar.company_id = c.company_id
#             WHERE c.company_id = (SELECT company_id FROM user_data WHERE user_id = %s) AND ar.status = 'pending'
#         """, (user_id,))
        
#         requests = cur.fetchall()

#         return jsonify({'status': 'success', 'requests': requests})

#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500
#     finally:
#         cur.close()

@app.route('/company_join', methods=['POST'])
def company_join():
    user_id = session.get('user_id')
    # Support JSON or form submission
    if request.is_json:
        data = request.get_json()
        company_name = data.get('company_name')
    else:
        company_name = request.form.get('company_name')
        
    if not user_id or not company_name:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
        
    try:
        cur = mysql.connection.cursor()
        # Find the company_id based on the company name
        cur.execute("SELECT company_id FROM company_data WHERE company_name = %s", (company_name,))
        company = cur.fetchone()
        if not company:
            return jsonify({"status": "error", "message": "Company not found"}), 404
        company_id = company[0]
        
        # Check if there's already a join request for this company by the user
        cur.execute("SELECT status FROM join_requests WHERE user_id = %s AND company_id = %s", (user_id, company_id))
        existing_request = cur.fetchone()
        if existing_request:
            if existing_request[0] == 'pending':
                return jsonify({"status": "error", "message": "Join request already pending."}), 400
            elif existing_request[0] == 'accepted':
                return jsonify({"status": "error", "message": "You are already a member of this company."}), 400
        
        # Insert a new join request with status 'pending' and current timestamp for created_at
        cur.execute(
            "INSERT INTO join_requests (user_id, company_id, status, created_at) VALUES (%s, %s, 'pending', NOW())",
            (user_id, company_id)
        )
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Join request sent."}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

        
@app.route('/pricing', methods=['GET','POST'])
def pricing():
    return render_template('pricing.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

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

# from here only apps
@app.route('/access_control', methods=['GET', 'POST'])
def access_control():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    admin_user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Verify the current user is admin and get their company_id
        cur.execute("SELECT role_id, company_id FROM user_data WHERE user_id = %s", (admin_user_id,))
        admin_info = cur.fetchone()
        if not admin_info or admin_info[0] != 1:
            return "Unauthorized", 403
        company_id = admin_info[1]
        
        if request.method == 'POST':
            # If adding an assignment
            if 'assign' in request.form:
                target_user_id = request.form.get('target_user_id')
                app_id = request.form.get('app_id')
                if target_user_id and app_id:
                    cur.execute(
                        "INSERT INTO user_apps (user_id, app_id, added_to_dashboard) VALUES (%s, %s, TRUE)",
                        (target_user_id, app_id)
                    )
                    mysql.connection.commit()
            # If removing an assignment
            elif 'remove_assignment' in request.form:
                assignment_id = request.form.get('assignment_id')
                if assignment_id:
                    cur.execute("DELETE FROM user_apps WHERE user_app_id = %s", (assignment_id,))
                    mysql.connection.commit()
            # Process join request (accept/reject)
            elif 'process_request' in request.form:
                req_id = request.form.get('request_id')
                decision = request.form.get('decision')  # expected 'accepted' or 'rejected'
                if req_id and decision in ['accepted', 'rejected']:
                    cur.execute("UPDATE join_requests SET status = %s WHERE request_id = %s", (decision, req_id))
                    if decision == 'accepted':
                        cur.execute("SELECT user_id FROM join_requests WHERE request_id = %s", (req_id,))
                        join_user = cur.fetchone()
                        if join_user:
                            join_user_id = join_user[0]
                            # Set the joining user as Employee (role_id 3) and assign company_id
                            cur.execute("UPDATE user_data SET company_id = %s, role_id = %s WHERE user_id = %s",
                                        (company_id, 3, join_user_id))
                    mysql.connection.commit()
            # Upgrade user role
            elif 'upgrade_role' in request.form:
                target_user_id = request.form.get('upgrade_target_user_id')
                new_role = request.form.get('new_role')
                if target_user_id and new_role:
                    cur.execute("UPDATE user_data SET role_id = %s WHERE user_id = %s", (new_role, target_user_id))
                    mysql.connection.commit()
            return redirect(url_for('access_control'))
        
        # GET section:
        # 1. List all users in the admin's company (with their role)
        cur.execute("SELECT user_id, username, role_id FROM user_data WHERE company_id = %s", (company_id,))
        company_users = cur.fetchall()
        
        # 2. List available apps from the apps table
        cur.execute("SELECT app_id, app_name FROM apps")
        apps = cur.fetchall()
        
        # 3. Get current app assignments for users in the company
        cur.execute("""
            SELECT ua.user_app_id, u.username, a.app_name, u.role_id
            FROM user_apps ua
            JOIN user_data u ON ua.user_id = u.user_id
            JOIN apps a ON ua.app_id = a.app_id
            WHERE u.company_id = %s
        """, (company_id,))
        assignments = []
        role_map = {1: "Admin", 2: "Manager", 3: "Employee"}
        for row in cur.fetchall():
            assignments.append({
                "assignment_id": row[0],
                "username": row[1],
                "app_name": row[2],
                "user_role": role_map.get(row[3], "Custom")
            })
        
        # 4. Get pending join requests for the company
        cur.execute("SELECT request_id, user_id, created_at FROM join_requests WHERE company_id = %s AND status = 'pending'", (company_id,))
        join_requests = []
        for req in cur.fetchall():
            req_id, u_id, created_at = req
            cur.execute("SELECT username FROM user_data WHERE user_id = %s", (u_id,))
            user_row = cur.fetchone()
            username = user_row[0] if user_row else "Unknown"
            join_requests.append({
                "request_id": req_id,
                "username": username,
                "created_at": created_at
            })
        
        return render_template('access_control.html', 
                               company_users=company_users, 
                               apps=apps, 
                               assignments=assignments, 
                               join_requests=join_requests)
    except Exception as e:
        print("Error in access_control:", e)
        return "Error", 500
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
