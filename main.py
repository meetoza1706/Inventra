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
            # Verify user credentials
            query = "SELECT * FROM user_data WHERE username = %s AND password_hash = %s"
            cur.execute(query, (username, password))
            user = cur.fetchone()

            if user:
                user_id = user[0]
                ip_address = request.remote_addr
                # Check for an active session from the current IP address
                cur.execute("""
                    SELECT session_id FROM sessions 
                    WHERE user_id = %s AND ip_address = %s 
                      AND is_active = 1 AND expiration_time > NOW()
                """, (user_id, ip_address))
                active_session = cur.fetchone()

                if active_session:
                    session['user_logged_in'] = True
                    session['username'] = username
                    session['user_id'] = user_id
                else:
                    # Create a new session record (auto-increment session_id)
                    login_time = datetime.datetime.now()
                    expiration_time = login_time + datetime.timedelta(hours=1)
                    cur.execute("""
                        INSERT INTO sessions (user_id, login_time, expiration_time, is_active, ip_address) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, login_time, expiration_time, 1, ip_address))
                    mysql.connection.commit()
                    
                    session['user_logged_in'] = True
                    session['username'] = username
                    session['user_id'] = user_id

                # Return JSON response to trigger redirection on the client-side
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
        # Fetch user info: first_name, user_id, role_name, and company_name
        cur.execute("""
            SELECT u.first_name, u.user_id, r.role_name, c.company_name
            FROM user_data u
            LEFT JOIN roles r ON u.role_id = r.role_id
            LEFT JOIN company_data c ON u.company_id = c.company_id
            WHERE u.username = %s
        """, (username,))
        user_info = cur.fetchone()
        if not user_info:
            return redirect(url_for('login'))
        first_name, user_id, role_name, company_name = user_info
        print("DEBUG: company_name =", company_name)
        print("DEBUG: role_name =", role_name)
        
        # If company_name is None, try fetching it from employee_data (for non-admins)
        if not company_name:
            cur.execute("SELECT company_name FROM employee_data WHERE user_id = %s", (user_id,))
            emp = cur.fetchone()
            if emp:
                company_name = emp[0]
        
        apps_to_display = []
        # Only fetch apps if the user is part of a company
        cur.execute("SELECT company_id FROM user_data WHERE user_id = %s", (user_id,))
        comp_result = cur.fetchone()
        if comp_result and comp_result[0]:
            # First, try to fetch user-specific apps from user_apps (with dynamic route)
            cur.execute("""
                SELECT a.app_name, a.app_description, a.app_route
                FROM user_apps ua
                JOIN apps a ON ua.app_id = a.app_id 
                WHERE ua.user_id = %s AND ua.added_to_dashboard = 1
            """, (user_id,))
            user_apps = cur.fetchall()
            if user_apps:
                apps_to_display = [
                    {"app_name": r[0], "app_description": r[1], "app_route": r[2]} 
                    for r in user_apps
                ]
            else:
                # Fallback: fetch default apps from role_permissions based on role_name (with dynamic route)
                if role_name:
                    cur.execute("""
                        SELECT a.app_name, a.app_description, a.app_route
                        FROM role_permissions rp
                        JOIN apps a ON rp.permissions = a.app_id
                        WHERE rp.role_name = %s
                    """, (role_name,))
                    role_apps = cur.fetchall()
                    apps_to_display = [
                        {"app_name": r[0], "app_description": r[1], "app_route": r[2]} 
                        for r in role_apps
                    ]
        else:
            # User not in a company so no company-specific apps are shown.
            apps_to_display = []
        
        return render_template('dashboard.html',
                               username=username,
                               first_name=first_name or '',
                               company_name=company_name or '',
                               apps=apps_to_display)
    except Exception as e:
        print("Error fetching data:", e)
        return "Error", 500
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
            # Add custom app assignment
            if 'assign' in request.form:
                target_user_id = request.form.get('target_user_id')
                app_id = request.form.get('app_id')
                if target_user_id and app_id:
                    cur.execute(
                        "INSERT INTO user_apps (user_id, app_id, added_to_dashboard) VALUES (%s, %s, TRUE)",
                        (target_user_id, app_id)
                    )
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
                    # Expand allowed values
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
        
        # 2. Get all available apps for dropdown
        cur.execute("SELECT app_id, app_name FROM apps")
        apps = cur.fetchall()
        
        # 3. Build full track of app assignments for each non-admin user
        assignments = []
        for user in company_users:
            u_id, username, r_id = user
            if r_id == 1:  # Skip admin's own assignments
                continue
            role_name = role_map.get(r_id, "Custom")
            # Check for custom assignments for this user
            cur.execute("""
                SELECT ua.user_app_id, a.app_id, a.app_name, a.app_description
                FROM user_apps ua
                JOIN apps a ON ua.app_id = a.app_id
                WHERE ua.user_id = %s AND ua.added_to_dashboard = TRUE
            """, (u_id,))
            custom_apps = cur.fetchall()
            if custom_apps:
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
            else:
                # Fallback to default apps from role_permissions for the user's role
                cur.execute("""
                    SELECT a.app_id, a.app_name, a.app_description 
                    FROM role_permissions rp
                    JOIN apps a ON rp.permissions = a.app_id
                    WHERE rp.role_name = %s
                """, (role_name,))
                default_apps = cur.fetchall()
                for row in default_apps:
                    app_id = row[0]
                    # Check if an override exists for this user & app
                    cur.execute("SELECT COUNT(*) FROM user_apps WHERE user_id = %s AND app_id = %s AND added_to_dashboard = FALSE", 
                                (u_id, app_id))
                    override_count = cur.fetchone()[0]
                    if override_count > 0:
                        continue  # Skip this default app since access was removed
                    assignments.append({
                        "assignment_id": None,
                        "username": username,
                        "user_id": u_id,
                        "app_id": app_id,
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
