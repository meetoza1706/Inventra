from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_mysqldb import MySQL
import datetime
from flask_cors import CORS
import qrcode, io, base64
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
import random


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
        cpassword = request.form.get('cpassword')  # Get `cpassword` from the request

        if not username or not email or not password or not cpassword:
            return jsonify({"status": "failure", "message": "All fields are required"}), 400

        if password != cpassword:
            return jsonify({"status": "failure", "message": "Passwords do not match"}), 400

        hashed_password = generate_password_hash(password)  # Hash password before storing

        try:
            cur = mysql.connection.cursor()
            query = "SELECT username, email FROM user_data WHERE username = %s OR email = %s"
            cur.execute(query, (username, email))
            user = cur.fetchone()

            if user:
                return jsonify({"status": "failure", "message": "User already exists"}), 409
            
            insert_query = "INSERT INTO user_data (username, email, password_hash) VALUES (%s, %s, %s)"
            cur.execute(insert_query, (username, email, hashed_password))
            mysql.connection.commit()
            return jsonify({"status": "success", "message": "User registered successfully"}), 201
        except Exception as err:
            print("Registration error:", err)
            return jsonify({"status": "error", "message": str(err)}), 500
        finally:
            if cur:
                cur.close()

    return render_template('sign_up.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('user_logged_in'):
        return jsonify({"status": "success", "message": "Already logged in"}), 200

    if request.method == 'POST':
        # Allow login using username or email
        user_input = request.form.get('username')
        password = request.form.get('password')

        try:
            cur = mysql.connection.cursor()
            query = "SELECT * FROM user_data WHERE username = %s OR email = %s"
            cur.execute(query, (user_input, user_input))
            user = cur.fetchone()

            # If no user is found, return "Incorrect username or email"
            if not user:
                return jsonify({"status": "failure", "message": "Incorrect username or email"}), 401

            # If user exists but password doesn't match, return "Incorrect password"
            if not check_password_hash(user[3], password):
                return jsonify({"status": "failure", "message": "Incorrect password"}), 401

            # Login successful
            user_id = user[0]
            ip_address = request.remote_addr

            cur.execute("""
                SELECT session_id FROM sessions 
                WHERE user_id = %s AND ip_address = %s 
                  AND is_active = 1 AND expiration_time > NOW()
            """, (user_id, ip_address))
            active_session = cur.fetchone()

            if active_session:
                session['user_logged_in'] = True
                session['username'] = user_input
                session['user_id'] = user_id
            else:
                login_time = datetime.datetime.now()
                expiration_time = login_time + datetime.timedelta(hours=1)
                cur.execute("""
                    INSERT INTO sessions (user_id, login_time, expiration_time, is_active, ip_address) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, login_time, expiration_time, 1, ip_address))
                mysql.connection.commit()
                session['user_logged_in'] = True
                session['username'] = user_input
                session['user_id'] = user_id

            return jsonify({"status": "success", "message": "Login successful"}), 200

        except Exception as err:
            print("Login error:", err)
            return jsonify({"message": "Incorrect credentials"}), 500
        finally:
            cur.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    # If you store session_id in your Flask session, mark it inactive in the database.
    session_id = session.get('session_id')
    if session_id:
        try:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE sessions SET is_active = 0 WHERE session_id = %s", (session_id,))
            mysql.connection.commit()
        except Exception as e:
            print("Error updating session:", e)
        finally:
            cur.close()
    session.clear()  # Clear all session data
    return redirect(url_for('login'))

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
    try:
        cur = mysql.connection.cursor()
        # Fetch user info: first_name, user_id, role_name, company_id, company_name, and role_id
        cur.execute("""
            SELECT u.first_name, u.user_id, r.role_name, c.company_id, c.company_name, u.role_id
            FROM user_data u
            LEFT JOIN roles r ON u.role_id = r.role_id
            LEFT JOIN company_data c ON u.company_id = c.company_id
            WHERE u.username = %s
        """, (username,))
        user_info = cur.fetchone()
        if not user_info:
            return redirect(url_for('login'))
        
        first_name, user_id, role_name, company_id, company_name, role_id = user_info

        # If company info is missing, try fetching it from employee_data
        if not company_id or not company_name:
            cur.execute("SELECT company_id, company_name FROM employee_data WHERE user_id = %s", (user_id,))
            emp = cur.fetchone()
            if emp:
                company_id, company_name = emp

        # Store company_id in session for notification endpoints
        session['company_id'] = company_id

        # Fetch apps (user-specific first, then default based on role)
        apps_to_display = []
        if company_id:
            cur.execute("""
                SELECT a.app_name, a.app_description, a.app_route
                FROM user_apps ua
                JOIN apps a ON ua.app_id = a.app_id 
                WHERE ua.user_id = %s AND ua.added_to_dashboard = 1
            """, (user_id,))
            user_apps = cur.fetchall()
            if user_apps:
                apps_to_display = [{"app_name": r[0], "app_description": r[1], "app_route": r[2]} for r in user_apps]
            elif role_name:
                cur.execute("""
                    SELECT a.app_name, a.app_description, a.app_route
                    FROM role_permissions rp
                    JOIN apps a ON rp.permissions = a.app_id
                    WHERE rp.role_name = %s
                """, (role_name,))
                role_apps = cur.fetchall()
                apps_to_display = [{"app_name": r[0], "app_description": r[1], "app_route": r[2]} for r in role_apps]
        else:
            apps_to_display = []

        # Fetch low stock alerts with vendor details using vendor_data columns
        cur.execute("""
            SELECT id.inventory_id, id.item_name, id.quantity, id.reorder_level, 
                   vd.vendor_name, vd.vendor_contact, vd.vendor_email
            FROM inventory_data id
            LEFT JOIN vendor_data vd ON id.vendor_id = vd.vendor_id
            WHERE id.quantity <= id.reorder_level AND id.company_id = %s
        """, (company_id,))
        low_stock_alerts = cur.fetchall()

        # Fetch notifications (admins only) without vendor columns
        notifications = []
        if role_id == 1 and company_id:
            cur.execute("""
                SELECT notification_id, user_id, message, notification_type, created_at
                FROM notifications 
                WHERE company_id = %s 
                ORDER BY created_at DESC 
                LIMIT 10
            """, (company_id,))
            notifications = cur.fetchall()

        return render_template('dashboard.html',
                               username=username,
                               first_name=first_name or '',
                               company_name=company_name or '',
                               apps=apps_to_display,
                               notifications=notifications,
                               low_stock_alerts=low_stock_alerts,
                               is_admin=(role_id == 1))
    except Exception as e:
        print("Error fetching data:", e)
        return "Error", 500
    finally:
        cur.close()


@app.route('/mark_notification/<int:notification_id>', methods=['POST'])
def mark_notification(notification_id):
    if not session.get('user_logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    user_id = session.get('user_id')
    company_id = session.get('company_id')
    
    try:
        cur = mysql.connection.cursor()
        # Verify that the user is an admin
        cur.execute("SELECT role_id FROM user_data WHERE user_id = %s", (user_id,))
        role = cur.fetchone()
        if not role or role[0] != 1:
            return jsonify({"status": "error", "message": "Access denied"}), 403

        cur.execute("""
            DELETE FROM notifications 
            WHERE notification_id = %s AND company_id = %s
        """, (notification_id, company_id))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Notification removed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
@app.route('/clear_all_notifications', methods=['POST'])
def clear_all_notifications():
    if not session.get('user_logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    user_id = session.get('user_id')
    company_id = session.get('company_id')
    
    try:
        cur = mysql.connection.cursor()
        # Verify that the user is an admin
        cur.execute("SELECT role_id FROM user_data WHERE user_id = %s", (user_id,))
        role = cur.fetchone()
        if not role or role[0] != 1:
            return jsonify({"status": "error", "message": "Access denied"}), 403

        cur.execute("DELETE FROM notifications WHERE company_id = %s", (company_id,))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "All notifications cleared"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

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

@app.route('/features', methods=['GET', 'POST'])
def features():
    return render_template('test.html')

@app.route('/home2', methods=['GET', 'POST'])
def home2():
    return render_template('index.html')

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
@app.route('/company_profile', methods=['GET', 'POST'])
def company_profile():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Get user's company and role
        cur.execute("SELECT company_id, role_id FROM user_data WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()
        if not user_data:
            return "User not found", 404
        company_id, role_id = user_data
        if not company_id:
            return "You are not part of any company", 400
        is_admin = (role_id == 1)
        
        if request.method == 'POST':
            if is_admin:
                # Admin updating profile
                if 'update_profile' in request.form:
                    company_name = request.form.get('company_name')
                    email = request.form.get('email')
                    contact_number = request.form.get('contact_number')
                    website = request.form.get('website')
                    date_established = request.form.get('date_established')
                    cur.execute("""
                        UPDATE company_data 
                        SET company_name = %s, email = %s, contact_number = %s, website = %s, date_established = %s 
                        WHERE company_id = %s
                    """, (company_name, email, contact_number, website, date_established, company_id))
                    mysql.connection.commit()
                    return redirect(url_for('company_profile'))
                elif 'delete_company' in request.form:
                    # For now, just display a message (deletion will be implemented later)
                    return "Delete Company functionality will be implemented near project completion.", 200
            else:
                # Non-admin leave company action:
                if 'leave_company' in request.form:
                    # Remove user's app assignments
                    cur.execute("DELETE FROM user_apps WHERE user_id = %s", (user_id,))
                    # Remove company association and role_id from user_data
                    cur.execute("UPDATE user_data SET company_id = NULL, role_id = NULL WHERE user_id = %s", (user_id,))
                    mysql.connection.commit()
                    return redirect(url_for('dashboard'))
                    
        # GET: fetch company profile details
        cur.execute("""
            SELECT company_name, email, contact_number, website, date_established 
            FROM company_data 
            WHERE company_id = %s
        """, (company_id,))
        company = cur.fetchone()
        if not company:
            return "Company not found", 404

        return render_template('company_profile.html', company=company, is_admin=is_admin)
    except Exception as e:
        print("Error in company_profile:", e)
        return "Error", 500
    finally:
        cur.close()

@app.route('/employee/add', methods=['POST'])
def add_employee():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    admin_user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Only Admin can add employee records
        cur.execute("SELECT role_id, company_id FROM user_data WHERE user_id = %s", (admin_user_id,))
        admin_info = cur.fetchone()
        if not admin_info or admin_info[0] != 1:
            return "Unauthorized", 403
        company_id = admin_info[1]
        # Get data from form submission (or JSON)
        user_id = request.form.get('user_id')
        company_name = request.form.get('company_name')
        role_id = request.form.get('role_id')
        when_joined = request.form.get('when_joined')  # optional; otherwise defaults to NOW()
        if not (user_id and company_name and role_id):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        if not when_joined:
            when_joined = datetime.datetime.now()
        cur.execute("""
            INSERT INTO employee_data (user_id, company_id, company_name, role_id, when_joined)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, company_id, company_name, role_id, when_joined))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Employee added"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

@app.route('/employee/remove', methods=['POST'])
def remove_employee():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    admin_user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Only Admin can remove employee records
        cur.execute("SELECT role_id FROM user_data WHERE user_id = %s", (admin_user_id,))
        admin_info = cur.fetchone()
        if not admin_info or admin_info[0] != 1:
            return "Unauthorized", 403
        employee_id = request.form.get('employee_id')
        if not employee_id:
            return jsonify({"status": "error", "message": "Missing employee_id"}), 400
        cur.execute("DELETE FROM employee_data WHERE employee_id = %s", (employee_id,))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Employee removed"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

@app.route('/employee/update', methods=['POST'])
def update_employee():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    admin_user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Only Admin can update employee records
        cur.execute("SELECT role_id FROM user_data WHERE user_id = %s", (admin_user_id,))
        admin_info = cur.fetchone()
        if not admin_info or admin_info[0] != 1:
            return "Unauthorized", 403
        employee_id = request.form.get('employee_id')
        if not employee_id:
            return jsonify({"status": "error", "message": "Missing employee_id"}), 400
        
        # Build the update query dynamically based on provided fields
        update_fields = []
        params = []
        if request.form.get('user_id'):
            update_fields.append("user_id = %s")
            params.append(request.form.get('user_id'))
        if request.form.get('company_name'):
            update_fields.append("company_name = %s")
            params.append(request.form.get('company_name'))
        if request.form.get('role_id'):
            update_fields.append("role_id = %s")
            params.append(request.form.get('role_id'))
        if request.form.get('when_joined'):
            update_fields.append("when_joined = %s")
            params.append(request.form.get('when_joined'))
        if not update_fields:
            return jsonify({"status": "error", "message": "No fields to update"}), 400
        params.append(employee_id)
        query = "UPDATE employee_data SET " + ", ".join(update_fields) + " WHERE employee_id = %s"
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Employee updated"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return jsonify({"status": "error", "message": "All fields are required"}), 400
        
        if new_password != confirm_password:
            return jsonify({"status": "error", "message": "New passwords do not match"}), 400
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT password_hash FROM user_data WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            if not result:
                return jsonify({"status": "error", "message": "User not found"}), 404
            
            if not check_password_hash(result[0], current_password):
                return jsonify({"status": "error", "message": "Current password is incorrect"}), 401
            
            new_hash = generate_password_hash(new_password)
            cur.execute("UPDATE user_data SET password_hash = %s WHERE user_id = %s", (new_hash, user_id))
            mysql.connection.commit()
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            cur.close()
    
    return render_template("change_password.html")

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Step 2: OTP submission and password reset
        if 'otp' in request.form:
            input_otp = request.form.get('otp').strip()
            new_password = request.form.get('new_password').strip()
            confirm_password = request.form.get('confirm_password').strip()
            if not new_password or not confirm_password:
                return render_template("forgot_password.html", step=2, error="New password fields are required.")
            if new_password != confirm_password:
                return render_template("forgot_password.html", step=2, error="Passwords do not match.")
            session_otp = session.get('otp')
            email = session.get('reset_email')
            if not session_otp or input_otp != session_otp:
                return render_template("forgot_password.html", step=2, error="Invalid OTP.")
            try:
                cur = mysql.connection.cursor()
                hashed_password = generate_password_hash(new_password)
                cur.execute("UPDATE user_data SET password_hash = %s WHERE email = %s", (hashed_password, email))
                mysql.connection.commit()
                cur.close()
                session.pop('otp', None)
                session.pop('reset_email', None)
                return redirect(url_for('login'))
            except Exception as e:
                mysql.connection.rollback()
                return jsonify({"status": "error", "message": str(e)}), 500
        # Step 1: Email submission to send OTP
        else:
            email = request.form.get('email').strip()
            if not email:
                return render_template("forgot_password.html", step=1, error="Email is required.")
            try:
                cur = mysql.connection.cursor()
                cur.execute("SELECT email FROM user_data WHERE email = %s", (email,))
                user = cur.fetchone()
                cur.close()
                if not user:
                    return render_template("forgot_password.html", step=1, error="Email not found.")
                # Generate OTP
                otp = str(random.randint(100000, 999999))
                sender = 'inventra8@gmail.com'
                recipient = email
                subject = 'Your OTP for Password Reset'
                body = f'Your OTP for password reset is: {otp}'
                msg = MIMEText(body)
                msg['From'] = sender
                msg['To'] = recipient
                msg['Subject'] = subject
                try:
                    with smtplib.SMTP('smtp.gmail.com', 587) as server:
                        server.starttls()
                        server.login(sender, 'nrse ieig itce hltm')
                        server.sendmail(sender, recipient, msg.as_string())
                except Exception as e:
                    return render_template("forgot_password.html", step=1, error=f"Error sending email: {e}")
                session['otp'] = otp
                session['reset_email'] = email
                return render_template("forgot_password.html", step=2, message="OTP sent to your email.")
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

    return render_template("forgot_password.html", step=1)

#notification generation
def check_and_generate_notification(inventory_id, company_id, user_id):
    try:
        cur = mysql.connection.cursor()
        
        # Get stock level and reorder level
        cur.execute("""
            SELECT SUM(quantity) AS stock_level, reorder_level, item_name 
            FROM inventory_data 
            WHERE inventory_id = %s AND company_id = %s
        """, (inventory_id, company_id))
        
        result = cur.fetchone()
        if not result or result[0] is None:
            return  # No stock data found
        
        stock_level, reorder_level, item_name = result
        
        # Check if stock is below the reorder level
        if stock_level < reorder_level:
            notification_text = f"⚠️ Low Stock Alert: {item_name} is below reorder level ({stock_level} left)."
            
            # Insert notification if it doesn’t already exist
            cur.execute("""
                SELECT COUNT(*) FROM notifications 
                WHERE company_id = %s AND message = %s
            """, (company_id, notification_text))
            exists = cur.fetchone()[0]
            
            if exists == 0:
                cur.execute("""
                    INSERT INTO notifications (user_id, company_id, message, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, company_id, notification_text))
                mysql.connection.commit()
                
    except Exception as e:
        print(f"Error in notification generation: {e}")
    finally:
        cur.close()


# from here only apps
@app.route('/access_control', methods=['GET', 'POST'])
def access_control():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    admin_user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Verify current user is Admin and fetch company_id
        cur.execute("SELECT role_id, company_id FROM user_data WHERE user_id = %s", (admin_user_id,))
        admin_info = cur.fetchone()
        if not admin_info or admin_info[0] != 1:
            return "Unauthorized", 403
        company_id = admin_info[1]
        
        if request.method == 'POST':
            # Add custom app assignment with duplicate check
            if 'assign' in request.form:
                target_user_id = request.form.get('target_user_id')
                app_id = request.form.get('app_id')
                if target_user_id and app_id:
                    # Check if this app is already assigned to the user
                    cur.execute("SELECT COUNT(*) FROM user_apps WHERE user_id = %s AND app_id = %s", 
                                (target_user_id, app_id))
                    exists = cur.fetchone()[0]
                    if exists > 0:
                        # Already assigned – no further processing (you can also flash a message)
                        print(f"User {target_user_id} already has access to app {app_id}")
                    else:
                        cur.execute("""
                            INSERT INTO user_apps (user_id, app_id, added_to_dashboard) 
                            VALUES (%s, %s, TRUE)
                        """, (target_user_id, app_id))
                        mysql.connection.commit()
            # Remove a custom assignment
            elif 'remove_assignment' in request.form:
                assignment_id = request.form.get('assignment_id')
                if assignment_id:
                    cur.execute("DELETE FROM user_apps WHERE user_app_id = %s", (assignment_id,))
                    mysql.connection.commit()
            # Remove default access by inserting an override record
            elif 'remove_default' in request.form:
                target_user_id = request.form.get('target_user_id')
                app_id = request.form.get('app_id')
                if target_user_id and app_id:
                    cur.execute("INSERT INTO user_apps (user_id, app_id, added_to_dashboard) VALUES (%s, %s, 0)", 
                                (target_user_id, app_id))
                    mysql.connection.commit()
            # Process join request (accept/reject)
            elif 'process_request' in request.form:
                req_id = request.form.get('request_id')
                decision = request.form.get('decision')  # Expected value from form
                if req_id and decision:
                    decision_lower = decision.strip().lower()
                    print("Received decision:", decision_lower)  # Debug output
                    if decision_lower in ['approve', 'approved', 'accept', 'accepted']:
                        decision_mapped = 'approved'
                    elif decision_lower in ['reject', 'rejected', 'decline', 'declined']:
                        decision_mapped = 'rejected'
                    else:
                        return jsonify({"status": "error", "message": "Invalid decision value: " + decision_lower}), 400
                    # Update join_requests with the mapped decision
                    cur.execute("UPDATE join_requests SET status = %s WHERE request_id = %s", (decision_mapped, req_id))
                    if decision_mapped == 'approved':
                        cur.execute("SELECT user_id FROM join_requests WHERE request_id = %s", (req_id,))
                        join_user = cur.fetchone()
                        if join_user:
                            join_user_id = join_user[0]
                            cur.execute("UPDATE user_data SET company_id = %s, role_id = %s WHERE user_id = %s",
                                        (company_id, 3, join_user_id))
                    mysql.connection.commit()
            # Upgrade a user's role
            elif 'upgrade_role' in request.form:
                target_user_id = request.form.get('upgrade_target_user_id')
                new_role = request.form.get('new_role')
                if target_user_id and new_role:
                    cur.execute("UPDATE user_data SET role_id = %s WHERE user_id = %s", (new_role, target_user_id))
                    mysql.connection.commit()
            return redirect(url_for('access_control'))
        
        # GET section:
        # 1. Get all users in the company (with their role info)
        cur.execute("SELECT user_id, username, role_id FROM user_data WHERE company_id = %s", (company_id,))
        company_users = cur.fetchall()
        
        role_map = {1: "Admin", 2: "Manager", 3: "Employee"}
        
        # 2. Get all available apps for dropdown (and for fallback)
        cur.execute("SELECT app_id, app_name, app_description FROM apps")
        all_apps = cur.fetchall()
        
        # 3. Build full track of app assignments for each user
        assignments = []
        for user in company_users:
            u_id, username, r_id = user
            role_name = role_map.get(r_id, "Custom")
            # Get custom assignments for this user
            cur.execute("""
                SELECT ua.user_app_id, a.app_id, a.app_name, a.app_description
                FROM user_apps ua
                JOIN apps a ON ua.app_id = a.app_id
                WHERE ua.user_id = %s AND ua.added_to_dashboard = TRUE
            """, (u_id,))
            custom_apps = cur.fetchall()
            # Add custom assignments if they exist
            for row in custom_apps:
                assignments.append({
                    "assignment_id": row[0],
                    "username": username,
                    "user_id": u_id,
                    "app_id": row[1],
                    "app_name": row[2],
                    "app_description": row[3],
                    "user_role": role_name,
                    "custom": True
                })
            # Fallback: For admin, fetch ALL apps; for others, use role_permissions mapping.
            if r_id == 1:
                # Admin: always see all apps
                for app in all_apps:
                    # Skip if a custom assignment already exists for this app
                    if any(c[1] == app[0] for c in custom_apps):
                        continue
                    assignments.append({
                        "assignment_id": None,
                        "username": username,
                        "user_id": u_id,
                        "app_id": app[0],
                        "app_name": app[1],
                        "app_description": app[2],
                        "user_role": role_name,
                        "custom": False
                    })
            else:
                # Non-admin: fallback to apps via role_permissions mapping
                cur.execute("""
                    SELECT a.app_id, a.app_name, a.app_description 
                    FROM role_permissions rp
                    JOIN apps a ON rp.permissions = a.app_id
                    WHERE rp.role_name = %s
                """, (role_name,))
                default_apps = cur.fetchall()
                for row in default_apps:
                    # Skip if a custom assignment already exists for this app
                    if any(c[1] == row[0] for c in custom_apps):
                        continue
                    # Check if an override exists for this user & app (removed default access)
                    cur.execute("SELECT COUNT(*) FROM user_apps WHERE user_id = %s AND app_id = %s AND added_to_dashboard = FALSE", 
                                (u_id, row[0]))
                    override_count = cur.fetchone()[0]
                    if override_count > 0:
                        continue
                    assignments.append({
                        "assignment_id": None,
                        "username": username,
                        "user_id": u_id,
                        "app_id": row[0],
                        "app_name": row[1],
                        "app_description": row[2],
                        "user_role": role_name,
                        "custom": False
                    })
        
        # 4. Get pending join requests for the company.
        cur.execute("SELECT request_id, user_id, created_at FROM join_requests WHERE company_id = %s AND status = 'pending'", (company_id,))
        join_requests = []
        for req in cur.fetchall():
            req_id, u_id, created_at = req
            cur.execute("SELECT username FROM user_data WHERE user_id = %s", (u_id,))
            user_row = cur.fetchone()
            req_username = user_row[0] if user_row else "Unknown"
            join_requests.append({
                "request_id": req_id,
                "username": req_username,
                "created_at": created_at
            })
        
        return render_template('access_control.html', 
                               company_users=company_users, 
                               apps=all_apps, 
                               assignments=assignments, 
                               join_requests=join_requests)
    except Exception as e:
        print("Error in access_control:", e)
        return "Error", 500
    finally:
        cur.close()

#Inventory
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('username')
    try:
        cur = mysql.connection.cursor()
        # Get company_id for the current user
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        result = cur.fetchone() #tis one
        if not result or result[0] is None:
            return "You are not part of a company.", 400
        company_id = result[0]

        if request.method == 'POST':
            item_name = request.form.get('item_name')
            quantity = request.form.get('quantity')
            location_id = request.form.get('location_id')
            unit_price = request.form.get('unit_price')
            reorder_level = request.form.get('reorder_level')
            item_description = request.form.get('item_description')

            try:
                quantity = int(quantity)
            except ValueError:
                return "Invalid quantity", 400

            # Check if the item exists
            cur.execute("""
                SELECT inventory_id, quantity 
                FROM inventory_data 
                WHERE company_id = %s AND item_name = %s AND location_id = %s
            """, (company_id, item_name, location_id))
            existing_item = cur.fetchone()
            if existing_item:
                inventory_id = existing_item[0]
                new_quantity = int(existing_item[1]) + quantity
                cur.execute("""
                    UPDATE inventory_data 
                    SET quantity = %s, updated_at = NOW(), unit_price = %s, 
                        reorder_level = %s, item_description = %s 
                    WHERE inventory_id = %s
                """, (new_quantity, unit_price, reorder_level, item_description, inventory_id))
                mysql.connection.commit()

                cur.execute("""
                    SELECT stock_id, quantity 
                    FROM stock_levels 
                    WHERE inventory_id = %s AND location_id = %s
                """, (inventory_id, location_id))
                stock_record = cur.fetchone()
                if stock_record:
                    new_stock = int(stock_record[1]) + quantity
                    cur.execute("""
                        UPDATE stock_levels 
                        SET quantity = %s, last_updated = NOW() 
                        WHERE stock_id = %s
                    """, (new_stock, stock_record[0]))
                else:
                    cur.execute("""
                        INSERT INTO stock_levels (inventory_id, location_id, quantity)
                        VALUES (%s, %s, %s)
                    """, (inventory_id, location_id, quantity))
                mysql.connection.commit()
            else:
                cur.execute("""
                    INSERT INTO inventory_data 
                    (company_id, item_name, quantity, location_id, unit_price, reorder_level, item_description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (company_id, item_name, quantity, location_id, unit_price, reorder_level, item_description))
                mysql.connection.commit()
                inventory_id = cur.lastrowid

                cur.execute("""
                    INSERT INTO stock_levels (inventory_id, location_id, quantity)
                    VALUES (%s, %s, %s)
                """, (inventory_id, location_id, quantity))
                mysql.connection.commit()

            return redirect(url_for('inventory'))

        # GET: Fetch locations for Manage Locations
        cur.execute("SELECT location_id, location_name, address FROM inventory_locations WHERE company_id = %s", (company_id,))
        locations = cur.fetchall()

        # Create a mapping of location_id to location_name
        loc_map = {str(loc[0]): loc[1] for loc in locations}
        # Query all inventory data for the company
        cur.execute("""
            SELECT inventory_id, item_name, quantity, location_id, updated_at
            FROM inventory_data
            WHERE company_id = %s
            ORDER BY updated_at DESC
        """, (company_id,))
        all_inventory_data = cur.fetchall()

        # Group inventory items by location name
        inventory_by_location = {}
        for item in all_inventory_data:
            inv_id, item_name, quantity, loc_id, updated_at = item
            loc_key = loc_map.get(str(loc_id), "Unknown")
            inventory_by_location.setdefault(loc_key, []).append((inv_id, item_name, quantity, updated_at))

        return render_template("inventory.html", locations=locations, inventory_by_location=inventory_by_location)
    except Exception as e:
        print("Error fetching inventory:", e)
        return "Error", 500
    finally:
        cur.close()

@app.route('/add_location', methods=['POST'])
def add_location():
    if not session.get('user_logged_in'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    location_name = request.form.get('location_name')
    address = request.form.get('address')
    user_id = session.get('user_id')

    try:
        cur = mysql.connection.cursor()
        # Fetch the company_id of the current user
        cur.execute("SELECT company_id FROM user_data WHERE user_id = %s", (user_id,))
        company = cur.fetchone()
        if not company or not company[0]:
            return jsonify({"status": "error", "message": "Company not found"}), 400
        company_id = company[0]

        # Insert new location
        cur.execute("""
            INSERT INTO inventory_locations (company_id, location_name, address)
            VALUES (%s, %s, %s)
        """, (company_id, location_name, address))
        mysql.connection.commit()

        location_id = cur.lastrowid  # Get the inserted location's ID
        return jsonify({"status": "success", "location_id": location_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        cur.close()

@app.route('/edit_location', methods=['POST'])
def edit_location():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    location_id = request.form.get('location_id')
    new_location_name = request.form.get('location_name')
    new_address = request.form.get('address')
    
    if not location_id or not new_location_name:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE inventory_locations
            SET location_name = %s, address = %s
            WHERE location_id = %s
        """, (new_location_name, new_address, location_id))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Location updated", "location_id": location_id, "location_name": new_location_name})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

@app.route('/delete_location', methods=['POST'])
def delete_location():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    location_id = request.form.get('location_id')
    if not location_id:
        return jsonify({"status": "error", "message": "Location ID required"}), 400
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM inventory_locations WHERE location_id = %s", (location_id,))
        mysql.connection.commit()
        return jsonify({"status": "success", "message": "Location deleted", "location_id": location_id})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()

@app.route('/stock_entry', methods=['GET', 'POST'])
def stock_entry():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('username')
    user_id = session.get('user_id')
    try:
        cur = mysql.connection.cursor()
        # Get company_id for the user
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result or result[0] is None:
            return "You are not part of a company.", 400
        company_id = result[0]
        
        if request.method == 'POST':
            entry_type = request.form.get('entry_type')
            inventory_id = request.form.get('inventory_id')
            try:
                quantity = int(request.form.get('quantity'))
            except ValueError:
                return "Invalid quantity", 400
            
            if entry_type == 'add':
                location_id = request.form.get('location_id')
                # Record movement (IN)
                cur.execute("""
                    INSERT INTO stock_movements (inventory_id, from_location, to_location, quantity, movement_type, performed_by)
                    VALUES (%s, NULL, %s, %s, 'IN', %s)
                """, (inventory_id, location_id, quantity, user_id))
                mysql.connection.commit()
                # Update stock_levels
                cur.execute("""
                    SELECT stock_id, quantity FROM stock_levels 
                    WHERE inventory_id = %s AND location_id = %s
                """, (inventory_id, location_id))
                stock_record = cur.fetchone()
                if stock_record:
                    new_stock = int(stock_record[1]) + quantity
                    cur.execute("""
                        UPDATE stock_levels 
                        SET quantity = %s, last_updated = NOW() 
                        WHERE stock_id = %s
                    """, (new_stock, stock_record[0]))
                else:
                    cur.execute("""
                        INSERT INTO stock_levels (inventory_id, location_id, quantity)
                        VALUES (%s, %s, %s)
                    """, (inventory_id, location_id, quantity))
                mysql.connection.commit()
                # Update inventory_data record for that location
                cur.execute("""
                    UPDATE inventory_data 
                    SET quantity = quantity + %s, updated_at = NOW()
                    WHERE inventory_id = %s
                """, (quantity, inventory_id))
                mysql.connection.commit()
                # <-- Added notification check for "add" branch -->
                check_and_generate_notification(inventory_id, company_id, user_id)
            
            elif entry_type == 'transfer':
                from_location = request.form.get('from_location')
                to_location = request.form.get('to_location')
                # --- Update stock_levels ---
                # Subtract from source location
                cur.execute("""
                    SELECT stock_id, quantity 
                    FROM stock_levels 
                    WHERE inventory_id = %s AND location_id = %s
                """, (inventory_id, from_location))
                from_stock = cur.fetchone()
                if not from_stock or int(from_stock[1]) < quantity:
                    return "Insufficient stock in the source location", 400
                new_from_stock = int(from_stock[1]) - quantity
                cur.execute("""
                    UPDATE stock_levels 
                    SET quantity = %s, last_updated = NOW() 
                    WHERE stock_id = %s
                """, (new_from_stock, from_stock[0]))
                # Add to destination location
                cur.execute("""
                    SELECT stock_id, quantity 
                    FROM stock_levels 
                    WHERE inventory_id = %s AND location_id = %s
                """, (inventory_id, to_location))
                to_stock = cur.fetchone()
                if to_stock:
                    new_to_stock = int(to_stock[1]) + quantity
                    cur.execute("""
                        UPDATE stock_levels 
                        SET quantity = %s, last_updated = NOW() 
                        WHERE stock_id = %s
                    """, (new_to_stock, to_stock[0]))
                else:
                    cur.execute("""
                        INSERT INTO stock_levels (inventory_id, location_id, quantity)
                        VALUES (%s, %s, %s)
                    """, (inventory_id, to_location, quantity))
                # --- Update inventory_data ---
                # Get the source inventory_data record (it corresponds to from_location)
                cur.execute("""
                    SELECT inventory_id, quantity, item_name, unit_price, reorder_level, item_description
                    FROM inventory_data
                    WHERE inventory_id = %s AND location_id = %s
                """, (inventory_id, from_location))
                from_inv = cur.fetchone()
                if not from_inv or int(from_inv[1]) < quantity:
                    return "Insufficient inventory quantity at source", 400
                new_from_inv_qty = int(from_inv[1]) - quantity
                cur.execute("""
                    UPDATE inventory_data 
                    SET quantity = %s, updated_at = NOW()
                    WHERE inventory_id = %s
                """, (new_from_inv_qty, inventory_id))
                # Check for an existing record in inventory_data for the destination location
                cur.execute("""
                    SELECT inventory_id, quantity 
                    FROM inventory_data
                    WHERE company_id = %s AND item_name = %s AND location_id = %s
                """, (company_id, from_inv[2], to_location))
                to_inv = cur.fetchone()
                if to_inv:
                    new_to_inv_qty = int(to_inv[1]) + quantity
                    cur.execute("""
                        UPDATE inventory_data 
                        SET quantity = %s, updated_at = NOW()
                        WHERE inventory_id = %s
                    """, (new_to_inv_qty, to_inv[0]))
                else:
                    # Insert a new record for destination with same product details
                    cur.execute("""
                        INSERT INTO inventory_data 
                        (company_id, item_name, quantity, location_id, unit_price, reorder_level, item_description, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (company_id, from_inv[2], quantity, to_location, from_inv[3], from_inv[4], from_inv[5]))
                # Record the transfer movement
                cur.execute("""
                    INSERT INTO stock_movements (inventory_id, from_location, to_location, quantity, movement_type, performed_by)
                    VALUES (%s, %s, %s, %s, 'TRANSFER', %s)
                """, (inventory_id, from_location, to_location, quantity, user_id))
                mysql.connection.commit()
                # <-- Added notification check for "transfer" branch -->
                check_and_generate_notification(inventory_id, company_id, user_id)
            
            elif entry_type == 'sold':
                location_id = request.form.get('location_id')
                cur.execute("""
                    SELECT stock_id, quantity 
                    FROM stock_levels 
                    WHERE inventory_id = %s AND location_id = %s
                """, (inventory_id, location_id))
                stock_record = cur.fetchone()
                if not stock_record or int(stock_record[1]) < quantity:
                    return "Insufficient stock in the location", 400
                new_stock = int(stock_record[1]) - quantity
                cur.execute("""
                    UPDATE stock_levels 
                    SET quantity = %s, last_updated = NOW() 
                    WHERE stock_id = %s
                """, (new_stock, stock_record[0]))
                cur.execute("""
                    INSERT INTO stock_movements (inventory_id, from_location, to_location, quantity, movement_type, performed_by)
                    VALUES (%s, %s, NULL, %s, 'OUT', %s)
                """, (inventory_id, location_id, quantity, user_id))
                mysql.connection.commit()
                # Update inventory_data for sold stock (decrease quantity)
                cur.execute("""
                    UPDATE inventory_data 
                    SET quantity = quantity - %s, updated_at = NOW()
                    WHERE inventory_id = %s AND location_id = %s
                """, (quantity, inventory_id, location_id))
                mysql.connection.commit()
                # <-- Added notification check for "sold" branch -->
                check_and_generate_notification(inventory_id, company_id, user_id)
            
            return redirect(url_for('stock_entry'))
        
        # GET: Retrieve products and locations
        cur.execute("SELECT inventory_id, item_name FROM inventory_data WHERE company_id = %s", (company_id,))
        products = cur.fetchall()
        cur.execute("SELECT location_id, location_name FROM inventory_locations WHERE company_id = %s", (company_id,))
        locations = cur.fetchall()
        
        # Retrieve recent stock movements (last 10)
        cur.execute("""
            SELECT sm.movement_id, id.item_name,
                   (SELECT il.location_name FROM inventory_locations il WHERE il.location_id = sm.from_location) AS from_loc,
                   (SELECT il.location_name FROM inventory_locations il WHERE il.location_id = sm.to_location) AS to_loc,
                   sm.quantity, sm.movement_type, sm.created_at
            FROM stock_movements sm
            JOIN inventory_data id ON sm.inventory_id = id.inventory_id
            WHERE id.company_id = %s
            ORDER BY sm.created_at DESC
            LIMIT 10
        """, (company_id,))
        movements = cur.fetchall()
        movement_list = []
        for row in movements:
            movement_list.append({
                "movement_id": row[0],
                "product_name": row[1],
                "from_location": row[2] if row[2] else "N/A",
                "to_location": row[3] if row[3] else "N/A",
                "quantity": row[4],
                "movement_type": row[5],
                "created_at": row[6]
            })
        
        return render_template("stock_entry.html", products=products, locations=locations, movements=movement_list)
    except Exception as e:
        mysql.connection.rollback()
        print("Error in stock_entry:", e)
        return "Error", 500
    finally:
        cur.close()


@app.route('/undo_movement', methods=['POST'])
def undo_movement():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('username')
    cur = mysql.connection.cursor()
    # Get company_id for the current user
    cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
    result = cur.fetchone()
    if not result:
        return "Company not found", 404
    company_id = result[0]
    
    movement_id = request.form.get('movement_id')
    if not movement_id:
        return "Movement ID not provided", 400

    try:
        # Retrieve the movement details
        cur.execute("""
            SELECT movement_type, inventory_id, from_location, to_location, quantity 
            FROM stock_movements WHERE movement_id = %s
        """, (movement_id,))
        movement = cur.fetchone()
        if not movement:
            return "Movement not found", 404
        
        movement_type, inventory_id, from_location, to_location, qty = movement
        qty = int(qty)
        
        if movement_type == 'IN':
            # Reverse addition: subtract from destination's stock_levels
            cur.execute("""
                SELECT stock_id, quantity FROM stock_levels 
                WHERE inventory_id = %s AND location_id = %s
            """, (inventory_id, to_location))
            record = cur.fetchone()
            if not record:
                return "Stock record not found", 404
            new_qty = int(record[1]) - qty
            if new_qty < 0:
                return "Cannot undo: insufficient stock", 400
            cur.execute("""
                UPDATE stock_levels SET quantity = %s, last_updated = NOW() 
                WHERE stock_id = %s
            """, (new_qty, record[0]))
            # Update inventory_data: subtract qty
            cur.execute("""
                UPDATE inventory_data SET quantity = quantity - %s, updated_at = NOW()
                WHERE inventory_id = %s
            """, (qty, inventory_id))
        
        elif movement_type == 'OUT':
            # Reverse sold: add back to source's stock_levels
            cur.execute("""
                SELECT stock_id, quantity FROM stock_levels 
                WHERE inventory_id = %s AND location_id = %s
            """, (inventory_id, from_location))
            record = cur.fetchone()
            if record:
                new_qty = int(record[1]) + qty
                cur.execute("""
                    UPDATE stock_levels SET quantity = %s, last_updated = NOW()
                    WHERE stock_id = %s
                """, (new_qty, record[0]))
            else:
                cur.execute("""
                    INSERT INTO stock_levels (inventory_id, location_id, quantity)
                    VALUES (%s, %s, %s)
                """, (inventory_id, from_location, qty))
            # Update inventory_data: add qty
            cur.execute("""
                UPDATE inventory_data SET quantity = quantity + %s, updated_at = NOW()
                WHERE inventory_id = %s AND location_id = %s
            """, (qty, inventory_id, from_location))
        
        elif movement_type == 'TRANSFER':
            # Reverse transfer: subtract from destination and add back to source
            
            # Subtract from destination's stock_levels
            cur.execute("""
                SELECT stock_id, quantity FROM stock_levels 
                WHERE inventory_id = %s AND location_id = %s
            """, (inventory_id, to_location))
            dest_record = cur.fetchone()
            if not dest_record:
                return "Destination stock record not found", 404
            new_dest_qty = int(dest_record[1]) - qty
            if new_dest_qty < 0:
                return "Cannot undo transfer: insufficient stock at destination", 400
            cur.execute("""
                UPDATE stock_levels SET quantity = %s, last_updated = NOW()
                WHERE stock_id = %s
            """, (new_dest_qty, dest_record[0]))
            
            # Add back to source's stock_levels
            cur.execute("""
                SELECT stock_id, quantity FROM stock_levels 
                WHERE inventory_id = %s AND location_id = %s
            """, (inventory_id, from_location))
            source_record = cur.fetchone()
            if source_record:
                new_source_qty = int(source_record[1]) + qty
                cur.execute("""
                    UPDATE stock_levels SET quantity = %s, last_updated = NOW()
                    WHERE stock_id = %s
                """, (new_source_qty, source_record[0]))
            else:
                cur.execute("""
                    INSERT INTO stock_levels (inventory_id, location_id, quantity)
                    VALUES (%s, %s, %s)
                """, (inventory_id, from_location, qty))
            
            # Reverse inventory_data updates using JOIN to avoid subquery update errors:
            # Add qty back to source's inventory_data record
            cur.execute("""
                UPDATE inventory_data i
                JOIN (SELECT item_name FROM inventory_data WHERE inventory_id = %s) sub
                  ON i.company_id = %s AND i.location_id = %s AND i.item_name = sub.item_name
                SET i.quantity = i.quantity + %s, i.updated_at = NOW()
            """, (inventory_id, company_id, from_location, qty))
            # Subtract qty from destination's inventory_data record
            cur.execute("""
                UPDATE inventory_data i
                JOIN (SELECT item_name FROM inventory_data WHERE inventory_id = %s) sub
                  ON i.company_id = %s AND i.location_id = %s AND i.item_name = sub.item_name
                SET i.quantity = i.quantity - %s, i.updated_at = NOW()
            """, (inventory_id, company_id, to_location, qty))
        
        # Finally, delete the movement record
        cur.execute("DELETE FROM stock_movements WHERE movement_id = %s", (movement_id,))
        mysql.connection.commit()
        return redirect(url_for('stock_entry'))
    except Exception as e:
        mysql.connection.rollback()
        print("Error undoing movement:", e)
        return "Error", 500
    finally:
        cur.close()

# analytics
@app.route('/analytics')
def analytics():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('username')
    try:
        cur = mysql.connection.cursor()
        # Get company_id for the current user
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result or not result[0]:
            return "You are not part of a company.", 400
        company_id = result[0]
        
        # Query 1: Total unique inventory items
        cur.execute("SELECT COUNT(*) FROM inventory_data WHERE company_id = %s", (company_id,))
        total_items = cur.fetchone()[0]
        
        # Query 2: Total stock quantity (using stock_levels joined with inventory_data)
        cur.execute("""
            SELECT SUM(sl.quantity)
            FROM stock_levels sl
            JOIN inventory_data id ON sl.inventory_id = id.inventory_id
            WHERE id.company_id = %s
        """, (company_id,))
        total_stock = cur.fetchone()[0] or 0
        
        # Query 3: Total inventory value (unit_price * quantity)
        cur.execute("""
            SELECT SUM(id.unit_price * id.quantity)
            FROM inventory_data id
            WHERE id.company_id = %s
        """, (company_id,))
        total_value = cur.fetchone()[0] or 0
        
        # Query 4: Low stock count (items where quantity <= reorder_level)
        cur.execute("""
            SELECT COUNT(*) 
            FROM inventory_data 
            WHERE company_id = %s AND quantity <= reorder_level
        """, (company_id,))
        low_stock_count = cur.fetchone()[0]
        
        # Query 5: Stock movements aggregated by type
        cur.execute("""
            SELECT sm.movement_type, SUM(sm.quantity)
            FROM stock_movements sm
            JOIN inventory_data id ON sm.inventory_id = id.inventory_id
            WHERE id.company_id = %s
            GROUP BY sm.movement_type
        """, (company_id,))
        movement_counts = {row[0]: row[1] for row in cur.fetchall()}
        
        # Query 6: Inventory distribution by location
        cur.execute("""
            SELECT il.location_name, SUM(sl.quantity)
            FROM stock_levels sl
            JOIN inventory_data id ON sl.inventory_id = id.inventory_id
            JOIN inventory_locations il ON sl.location_id = il.location_id
            WHERE id.company_id = %s
            GROUP BY il.location_name
        """, (company_id,))
        location_distribution = cur.fetchall()
        
        # Query 7: Top 5 vendors by items supplied
        cur.execute("""
            SELECT vd.vendor_name, COUNT(id.inventory_id) AS total_items_supplied
            FROM vendor_data vd
            JOIN inventory_data id ON vd.vendor_id = id.vendor_id
            WHERE id.company_id = %s
            GROUP BY vd.vendor_name
            ORDER BY total_items_supplied DESC
            LIMIT 5
        """, (company_id,))
        vendor_performance = cur.fetchall()
        
        # Query 8: Sales Report - Total Sold per Item (using movement_type = 'OUT')
        cur.execute("""
            SELECT id.item_name, SUM(sm.quantity) AS total_sold
            FROM stock_movements sm
            JOIN inventory_data id ON sm.inventory_id = id.inventory_id
            WHERE sm.movement_type = 'OUT' AND id.company_id = %s
            GROUP BY id.item_name
            ORDER BY total_sold DESC
        """, (company_id,))
        sales_report = cur.fetchall()
        
        # Prepare sales data for chart: labels and values
        sales_labels = [row[0] for row in sales_report]
        sales_values = [row[1] for row in sales_report]
        
        return render_template("analytics.html",
                               total_items=total_items,
                               total_stock=total_stock,
                               total_value=total_value,
                               low_stock_count=low_stock_count,
                               movement_counts=movement_counts,
                               location_distribution=location_distribution,
                               vendor_performance=vendor_performance,
                               sales_labels=sales_labels,
                               sales_values=sales_values)
    except Exception as e:
        print("Error in analytics:", e)
        return "Error", 500
    finally:
        cur.close()
@app.route('/vendor_list', methods=['GET', 'POST'])
def vendor_list():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    username = session.get('username')
    try:
        cur = mysql.connection.cursor()
        # Get company_id for the current user from user_data
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result or result[0] is None:
            return "You are not part of a company.", 400
        company_id = result[0]

        # POST: Add new vendor (including products column)
        if request.method == 'POST':
            vendor_name = request.form.get('vendor_name')
            vendor_contact = request.form.get('vendor_contact')
            vendor_address = request.form.get('vendor_address')
            vendor_email = request.form.get('vendor_email')
            vendor_products = request.form.get('vendor_products')  # new column

            cur.execute("""
                INSERT INTO vendor_data 
                (company_id, vendor_name, vendor_contact, vendor_address, vendor_email, vendor_products)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (company_id, vendor_name, vendor_contact, vendor_address, vendor_email, vendor_products))
            mysql.connection.commit()
            return redirect(url_for('vendor_list'))

        # GET: Retrieve all vendors for the current company
        cur.execute("""
            SELECT vendor_id, vendor_name, vendor_contact, vendor_address, vendor_email, vendor_products 
            FROM vendor_data WHERE company_id = %s
        """, (company_id,))
        vendors = cur.fetchall()
        return render_template("vendor_list.html", vendors=vendors)
    except Exception as e:
        print("Error in vendor_list:", e)
        return "Error", 500
    finally:
        cur.close()


@app.route('/vendor/edit/<int:vendor_id>', methods=['GET', 'POST'])
def edit_vendor(vendor_id):
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    try:
        cur = mysql.connection.cursor()
        username = session.get('username')
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        company = cur.fetchone()
        if not company:
            return "Invalid user", 400

        cur.execute("""
            SELECT vendor_id, vendor_name, vendor_contact, vendor_address, vendor_email, vendor_products
            FROM vendor_data
            WHERE vendor_id = %s AND company_id = %s
        """, (vendor_id, company[0]))
        vendor = cur.fetchone()
        if not vendor:
            return "Vendor not found", 404

        if request.method == 'POST':
            vendor_name = request.form.get('vendor_name')
            vendor_contact = request.form.get('vendor_contact')
            vendor_address = request.form.get('vendor_address')
            vendor_email = request.form.get('vendor_email')
            vendor_products = request.form.get('vendor_products')
            cur.execute("""
                UPDATE vendor_data
                SET vendor_name = %s, vendor_contact = %s, vendor_address = %s, vendor_email = %s, vendor_products = %s
                WHERE vendor_id = %s AND company_id = %s
            """, (vendor_name, vendor_contact, vendor_address, vendor_email, vendor_products, vendor_id, company[0]))
            mysql.connection.commit()
            return redirect(url_for('vendor_list'))
        return render_template("edit_vendor.html", vendor=vendor)
    except Exception as e:
        print("Edit vendor error:", e)
        return "Error", 500
    finally:
        cur.close()


@app.route('/vendor/delete/<int:vendor_id>', methods=['POST'])
def delete_vendor(vendor_id):
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    try:
        cur = mysql.connection.cursor()
        username = session.get('username')
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        company = cur.fetchone()
        if not company:
            return "Invalid user", 400

        cur.execute("SELECT vendor_id FROM vendor_data WHERE vendor_id = %s AND company_id = %s", (vendor_id, company[0]))
        if not cur.fetchone():
            return "Unauthorized", 403

        cur.execute("DELETE FROM vendor_data WHERE vendor_id = %s AND company_id = %s", (vendor_id, company[0]))
        mysql.connection.commit()
        return redirect(url_for('vendor_list'))
    except Exception as e:
        print("Delete vendor error:", e)
        return "Error", 500
    finally:
        cur.close()


#QR code
@app.route('/barcode')
def barcode_home():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    return render_template("barcode_home.html")

@app.route('/barcode/generate', methods=['GET', 'POST'])
def barcode_generate():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    username = session.get('username')
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT company_id FROM user_data WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result or result[0] is None:
            return "You are not part of a company.", 400
        company_id = result[0]
        
        # Fetch products and locations for dropdowns
        cur.execute("SELECT inventory_id, item_name FROM inventory_data WHERE company_id = %s", (company_id,))
        products = cur.fetchall()
        cur.execute("SELECT location_id, location_name FROM inventory_locations WHERE company_id = %s", (company_id,))
        locations = cur.fetchall()
        
        if request.method == 'POST':
            inventory_id = request.form.get('inventory_id')
            location_id = request.form.get('location_id')
            quantity = request.form.get('quantity')
            
            # Fetch item and location names
            cur.execute("SELECT item_name FROM inventory_data WHERE inventory_id = %s", (inventory_id,))
            item_name = cur.fetchone()[0]
            cur.execute("SELECT location_name FROM inventory_locations WHERE location_id = %s", (location_id,))
            location_name = cur.fetchone()[0]
            
            # Encode data with names for better readability
            data = f"{inventory_id},{location_id},{quantity},{item_name},{location_name}"
            qr = qrcode.make(data)
            
            # Save QR code to buffer
            buf = io.BytesIO()
            qr.save(buf, format='PNG')
            buf.seek(0)
            img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            return render_template("barcode_generate.html", products=products, locations=locations, qr_code=img_b64, qr_data=data)
        
        return render_template("barcode_generate.html", products=products, locations=locations)
    except Exception as e:
        print("Error in barcode_generate:", e)
        return "Error", 500
    finally:
        cur.close()


@app.route('/barcode/download_qr')
def download_qr():
    """Allows users to download the last generated QR code."""
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    
    data = request.args.get('data')
    if not data:
        return "No QR code found.", 400

    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)

    return send_file(buf, mimetype="image/png", as_attachment=True, download_name="qr_code.png")


@app.route('/barcode/scan', methods=['GET'])
def barcode_scan():
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))
    return render_template("barcode_scan.html")



@app.route('/get_item_location/<int:inventory_id>/<int:location_id>')
def get_item_location(inventory_id, location_id):
    cursor = mysql.connection.cursor()

    # Fetch item name
    cursor.execute("SELECT name FROM inventory_data WHERE id = %s", (inventory_id,))
    item_row = cursor.fetchone()
    item_name = item_row[0] if item_row else None

    # Fetch location name
    cursor.execute("SELECT name FROM inventory_locations WHERE id = %s", (location_id,))
    location_row = cursor.fetchone()
    location_name = location_row[0] if location_row else None

    cursor.close()

    if not item_name or not location_name:
        return jsonify({"error": "Invalid inventory or location ID"}), 400

    return jsonify({"item_name": item_name, "location_name": location_name})

if __name__ == '__main__':  
    app.run(port=5000, debug=True)   