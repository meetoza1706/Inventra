from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign_up', methods=['POST','GET'])
def sign_up():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')

    if username:
        print(username,email,password,cpassword)
        return jsonify({'message': f'Success for {username}.'})
    
    return render_template('sign_up.html')

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username and password:
        print(username, password)
        return jsonify({'message': f'Success for {username}.'})
    
    return render_template('login.html')

@app.route('/test')
def test():
    return render_template('content.html')

@app.route('/test2')
def test2():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(port=5000)
    app.run(debug=True)
