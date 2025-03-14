
import mysql.connector
from Code.Password import Password
from flask import Flask, render_template, redirect, url_for, request
import os


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
    def get_user_salt(user_id):
        salt = Account.executeQuery("SELECT Salt from SecureApp.Users WHERE UserID = %s", values=[user_id])
        if not salt:
            return -1
        return salt[0][0]

    @staticmethod
    def add_friend(user_id,friend_id):
        query = "INSERT INTO SecureApp.Friend(User_ID,Friend_ID) VALUES(%s,%s)"
        Account.executeQuery(query,values=[user_id,friend_id])
        Account.executeQuery(query,values=[friend_id,user_id])
        query = "DELETE FROM SecureApp.FriendRequest WHERE Sender_ID = %s AND User_ID = %s"
        Account.executeQuery(query,values=[friend_id,user_id])

    @staticmethod
    def reject_request(user_id, friend_id):
        query = "DELETE FROM SecureApp.FriendRequest WHERE Sender_ID = %s AND User_ID = %s"
        Account.executeQuery(query,values=[friend_id,user_id])

    @staticmethod
    def request_friend(user_id, friend_id):
        # Check if a friend request or friendship already exists
        check_query = """
        SELECT * FROM SecureApp.FriendRequest 
        WHERE (Sender_ID = %s AND User_ID = %s) 
           OR (Sender_ID = %s AND User_ID = %s)
        """
        existing_request = Account.executeQuery(check_query, [user_id, friend_id, friend_id, user_id])

        if existing_request:
            return False  # A friend request or friendship already exists

        # If no existing request or friendship, insert the new friend request
        insert_query = "INSERT INTO SecureApp.FriendRequest (Sender_ID, User_ID) VALUES (%s, %s)"
        Account.executeQuery(insert_query, [user_id, friend_id])
        return True  # Friend request successfully sent


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


    @staticmethod
    def get_all_friend_requests(user_id):
        query = """
        SELECT 
            FriendRequest.Sender_ID, 
            FriendRequest.Status, 
            Users.Username
        FROM 
            SecureApp.FriendRequest
        JOIN 
            SecureApp.Users ON FriendRequest.Sender_ID = Users.ID
        WHERE 
            FriendRequest.User_ID = %s
           
        ORDER BY 
            FriendRequest.Timestamp DESC 
        LIMIT 1
        """
        return Account.executeQuery(query, [user_id])

    @staticmethod
    def get_all_chats(user_id):
        query = """
        SELECT Chat.ID, Chat.Name, Chat.owner_id 
        FROM SecureApp.Chat 
        JOIN SecureApp.ChatUser ON Chat.ID = ChatUser.ChatID 
        WHERE ChatUser.UserID = %s;
        """
        chats = Account.executeQuery(query, [user_id])

        return chats



