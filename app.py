from flask import Flask, render_template, redirect, url_for, request
import os


import mysql.connector

from Code.Account import Account
from Code.Password import Password
from Code.URLGenerator import URLGenerator


# Connection string

class App:
    app = Flask(__name__)
    app.secret_key = Password.read_private_key()

    @staticmethod
    @app.route('/')
    def index():
        return render_template('index.html')

    @staticmethod
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            getUserID = "SELECT ID FROM SecureApp.Users WHERE Username = %s"
            getPasswordData = "SELECT HashedPassword, Salt,PublicKey FROM SecureApp.Passwords WHERE UserID = %s"

            userID = Account.executeQuery(getUserID, values=[username])
            if not userID:
                return render_template('index.html')

            userID = userID[0][0]

            passwordData = Account.executeQuery(getPasswordData,values=[userID])[0]

            passwordObj = Password(passwordData[2])
            passwordObj.load_password(passwordData[1],passwordData[0])

            isPasswordCorrect = passwordObj.check_password(password)


            url_generator = URLGenerator(user_id=userID, salt=passwordData[1])
            link = url_generator.create_2fa_link()
            certificate = passwordObj.generate_certificate(link)
            message = passwordObj.encrypt(str(certificate))

            if isPasswordCorrect:
                return render_template('public_key_verification.html',text = message)






            # Add your login logic here (check credentials)
            return redirect(url_for('index'))  # Redirect back to home after login
        return render_template('login.html')

    @staticmethod
    @app.route('/verify_2fa/<token>')
    def verify_2fa(token):
        return render_template('index.html', token=token)

    @staticmethod
    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            public_key = request.form['public key']

            accounts = Account.executeQuery("SELECT Username FROM SecureApp.Users WHERE Username = %s", values=[username])
            if not accounts:
                Account.create_account(username, password,public_key)
                return redirect(url_for('index'))
            else:
                return redirect(url_for('create_account'))

             # Redirect back to home after creating account
        return render_template('create_account.html')

    @staticmethod
    @app.route('/public_key_verification')
    def public_key_verification(encrypted_message):
        return render_template('public_key_verification.html',text=encrypted_message)



if __name__ == '__main__':
    App.app.run(debug=True)
