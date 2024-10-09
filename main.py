from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def sign_up():
    return render_template('sign-up.html')

if __name__ == '__main__':
    app.run(debug=True)
