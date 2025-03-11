from flask import Flask, render_template, redirect, url_for, request



import mysql.connector

from Code.Account import Account

# Connection string



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your login logic here (check credentials)
        return redirect(url_for('index'))  # Redirect back to home after login
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        accounts = Account.executeQuery("SELECT Username FROM SecureApp.Users WHERE Username = %s", values=[username])
        if not accounts:
            Account.create_account(username, password)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('create_account'))

         # Redirect back to home after creating account
    return render_template('create_account.html')






if __name__ == '__main__':
    app.run(debug=True)
