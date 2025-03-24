import base64

from flask import Flask, render_template, redirect, url_for, request, session, app

from Code.Account import Account
from Code.routes.Chat import Chat, ChatMember
from Code.Password import Password
from Code.URLGenerator import URLGenerator
from Code.routes.Messenger import Messenger


# Connection string

class App:
    app = Flask(__name__)
    app.secret_key = Password.read_private_key()
    URL = URLGenerator()
    app.register_blueprint(Messenger, url_prefix='/Messenger')

    @staticmethod
    @app.route('/')
    def index():
        return render_template('index.html')

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

            passwordObj = Password(base64.b64decode(passwordData[2]).decode('utf-8'))
            passwordObj.load_password(passwordData[1],passwordData[0])

            isPasswordCorrect = passwordObj.check_password(password)



            token = URLGenerator.generate_2fa_token(userID,life_time=300)

            verification_url = url_for('verify_2fa', token=token,_external=True)

            certificate = passwordObj.generate_certificate(verification_url)
            message = passwordObj.encrypt(str(certificate),passwordObj.publicKey)

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

        session['user_id'] = user_id


        return  render_template('Messenger.html', user_chats=Chat.get_user_chats(user_id),user_requests = Account.get_all_friend_requests(user_id))

    # Route to view messages in a specific chat







    @staticmethod
    @app.route('/create_account', methods=['GET', 'POST'])
    def create_account():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            public_key = request.form['public key']
            print(public_key)
            encoded_key = base64.b64encode(public_key.encode('utf-8')).decode('utf-8')

            accounts = Account.executeQuery("SELECT Username FROM SecureApp.Users WHERE Username = %s", values=[username])

            if not accounts:
                Account.create_account(username, password,encoded_key)
                query = "SELECT ID FROM SecureApp.Users WHERE Username = %s"
                id = Account.executeQuery(query, [username])[0][0]

                query = "SELECT PublicKey FROM SecureApp.Passwords WHERE UserID = %s"
                key = Account.executeQuery(query, [id])[0][0]
                decoded_key =  base64.b64decode(key).decode('utf-8')
                print(decoded_key)
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
