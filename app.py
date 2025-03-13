from flask import Flask, render_template, redirect, url_for, request, jsonify, session
import os
import bcrypt

import mysql.connector
from itsdangerous import URLSafeTimedSerializer

from Code.Account import Account
from Code.Chat import Chat, ChatMember
from Code.Password import Password
from Code.URLGenerator import URLGenerator


# Connection string

class App:
    app = Flask(__name__)
    app.secret_key = Password.read_private_key()
    URL = URLGenerator()

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



            token = URLGenerator.generate_2fa_token(userID,life_time=300)

            verification_url = url_for('verify_2fa', token=token,_external=True)

            certificate = passwordObj.generate_certificate(verification_url)
            message = passwordObj.encrypt(str(certificate))

            if isPasswordCorrect:
                return render_template('public_key_verification.html',text = verification_url)

            # Add your login logic here (check credentials)
            return redirect(url_for('index'))  # Redirect back to home after login
        return render_template('login.html')





    @staticmethod
    @app.route('/verify_2fa/<token>')
    def verify_2fa(token):

        user_id = URLGenerator.validate_2fa_token(token)
        if user_id == -1:
            return render_template('create_account.html')

        user_chats = Chat.get_user_chats(user_id)
        session['user_id'] = user_id
        return render_template('friendRequestPage.html')

    # Route to view messages in a specific chat
    @staticmethod
    @app.route('/Messenger/<int:chat_id>')
    def view_chat(chat_id):
        # Retrieve user_id from session
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('verify_2fa'))  # Redirect if user is not logged in

        # Fetch user chats and messages for the selected chat
        user_chats = Chat.get_user_chats(user_id)
        chat_messages = ChatMember.get_chat_messages(chat_id, user_id)
        selected_chat = next((chat for chat in user_chats if chat['ChatID'] == chat_id), None)

        return render_template('messenger.html', user_chats=user_chats, selected_chat=selected_chat,
                               chat_messages=chat_messages)

    # Route to send a message
    @staticmethod
    @app.route('/send_message', methods=['POST'])
    def send_message():
        # Retrieve user_id from session
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('verify_2fa'))  # Redirect if user is not logged in

        # Get chat_id and message content from the form
        chat_id = request.form['chat_id']
        message_content = request.form['message']

        # Send the message using the ChatMember class
        ChatMember.sendMessage(chat_id, user_id, message_content)

        # Redirect back to the chat view
        return redirect(url_for('view_chat', chat_id=chat_id))

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

    @app.route('/chat_creation', methods=['GET', 'POST'])
    @staticmethod
    def create_chat():
        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'search':
                # Handle search functionality
                search_query = request.form.get('search_friends', '').lower()
                filtered_friends = [friend for friend in friends if search_query in friend['name'].lower()]
                return render_template('chat_creation.html', friends=filtered_friends)

            elif action == 'create_chat':
                # Handle chat creation
                chat_name = request.form.get('chat_name')
                selected_friends = request.form.getlist('selected_friends')
                print(f"Creating chat '{chat_name}' with friends: {selected_friends}")
                return redirect(url_for('home'))  # Redirect to home or chat list page

        # Render the form with all friends by default
        return render_template('chat_creation.html', friends=friends)

    @staticmethod
    @app.route('/public_key_verification')
    def public_key_verification(encrypted_message):
        return render_template('public_key_verification.html',text=encrypted_message)


    @staticmethod
    @app.route('/friendRequestPage', methods=['GET', 'POST'])
    def find_friends():
        search_results = []
        if request.method == 'POST':
            search_query = request.form.get('search_query', '').lower()
            query = "SELECT Username FROM SecureApp.Users WHERE Username LIKE '%{}%'".format(search_query)
            search_results = Account.executeQuery(query)[0]

        return render_template('friendRequestPage.html', search_results=search_results)

    @app.route('/send_friend_request', methods=['POST'])
    @staticmethod
    def send_friend_request():
        friend_id = request.form.get('friend_id')
        print(f"Friend request sent to user with ID: {friend_id}")
        return redirect(url_for('find_friends'))

if __name__ == '__main__':
    App.app.run(debug=True)
