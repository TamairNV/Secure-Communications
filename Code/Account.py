
import mysql.connector
from Code.Password import Password

class Account:

    def __init__(self, name,key):
        self.name = name
        self.public_key = key


    def __str__(self):
        return f"Name:{self.name}\nPublic Key:{self.public_key}"

    @staticmethod
    def create_account(name,plain_password, public_key):
        Account.executeQuery("INSERT into SecureApp.Users(Username) VALUES(%s)",values=[name])
        accountID = Account.executeQuery("SELECT ID from SecureApp.Users WHERE Username = %s",values=[name])[0][0]
        password = Password(public_key)
        password.init_password(plain_password)
        Account.executeQuery("INSERT into SecureApp.Passwords(UserID,HashedPassword,Salt,PublicKey) "
                             "VALUES(%s,%s,%s,%s)", values=(accountID,password.hashed_password,password.salt,public_key))




    @staticmethod
    def executeQuery(query,values=None):

        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tamer2006",
            database="SecureApp"
        )

        cursor = connection.cursor()
        if values is None:
            cursor.execute(query)
            result = cursor.fetchall()
        else:
            cursor.execute(query, values)
            result = cursor.fetchall()

        connection.commit()
        cursor.close()
        return result




