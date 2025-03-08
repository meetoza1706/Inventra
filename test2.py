from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Update with your actual database credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventra'

mysql = MySQL(app)

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print("Database connection successful:", result)
        cur.close()
    except Exception as e:
        print("Error connecting to database:", e)
