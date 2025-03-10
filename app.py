from flask import Flask, render_template, redirect, url_for, request



import mysql.connector

# Connection string
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Tamer2006",
    database="SecureApp"
)


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
        # Add your account creation logic here (save credentials)
        return redirect(url_for('index'))  # Redirect back to home after creating account
    return render_template('create_account.html')


def executeQuery(query,values = None):
    cursor = connection.cursor()
    if values is None:
        cursor.execute(query)
        result = cursor.fetchall()
    else:
        cursor.execute(query,values)
        result = cursor.fetchall()

    connection.commit()
    cursor.close()
    return result



if __name__ == '__main__':
    app.run(debug=True)
