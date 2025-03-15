import base64

import gnupg

import datetime

import mysql.connector

from Code.Account import Account
from Code.Password import Password


class Chat:
    @staticmethod
    def createChat(name,owner):
        query = "SELECT Name FROM chat WHERE Owner_ID = %s"
        all_Names = Account.executeQuery(query,[owner])
        if name in all_Names:
            return False

        query = "INSERT INTO chat (Name,owner_id) VALUES (%s,%s)"
        Account.executeQuery(query,[name,owner])

        Chat.addMember(owner,name,owner,"owner")

        return True

    @staticmethod
    def addMember(owner,gc_name,member, permission):
        query = "SELECT ID FROM Chat WHERE owner_ID = %s AND Name = %s"
        ID = Account.executeQuery(query,[owner,gc_name])[0][0]

        if ID:
            query = "INSERT INTO chatuser (UserID,ChatID,PermissionLevel) VALUES (%s,%s,%s)"
            Account.executeQuery(query,[member,ID,permission])

            return True

        return False

    @staticmethod
    def get_user_chats(user_id):
        query = """
            SELECT Chat.ID, Chat.Name, Chat.owner_id 
            FROM SecureApp.Chat
            JOIN SecureApp.ChatUser
            ON Chat.ID = ChatUser.ChatID
            WHERE ChatUser.UserID = %s;
        """
        result = Account.executeQuery(query, [user_id])

        return result


class ChatMember:
    def __init__(self,user_id,chat_id,permission_level):
        self.user_id = user_id
        self.chat_id = chat_id
        query = "SELECT Username FROM users WHERE id = %s"
        username = Account.executeQuery(query,[user_id])[0][0]
        self.username = username
        self.permission_level = permission_level


    @staticmethod
    def get_chat_messages(chat_id, user_id):

        # Step 1: Get messages in the chat
        messages = Account.executeQuery(
            "SELECT ID, ChatUserID, Timestamp FROM SecureApp.Message WHERE ChatID = %s;",
            [chat_id]
        )

        results = []
        for message in messages:
            message_id, sender_chatuser_id, timestamp = message

            # Step 2: Get sender's username
            sender_name = Account.executeQuery(
                "SELECT u.Username FROM SecureApp.ChatUser cu JOIN SecureApp.Users u ON cu.UserID = u.ID WHERE cu.ID = %s;",
                [sender_chatuser_id]
            )[0][0]  # Fetch the first row and column

            # Step 3: Get encrypted message for the recipient
            encrypted_text = Account.executeQuery(
                "SELECT EncryptedText FROM SecureApp.EncryptedMessage WHERE MessageID = %s AND ChatUserID = (SELECT ID FROM SecureApp.ChatUser WHERE UserID = %s AND ChatID = %s);",
                [message_id, user_id, chat_id]
            )[0][0]  # Fetch the first row and column

            results.append({
                "MessageID": message_id,
                "Timestamp": timestamp,
                "EncryptedText": encrypted_text,
                "SenderName": sender_name
            })



        query = "SELECT Username FROM Users WHERE ID = %s"
        username = Account.executeQuery(query,[user_id])[0][0]

        query = "SELECT ProfilePicture FROM Users WHERE ID = %s"
        try:
            profile_pic = Account.executeQuery(query,[user_id])[0][0]
        except:
            profile_pic = None


        # Create a new list with modified tuples
        decoded_result = []
        for row in results:
            align = 'left'
            if username == row["SenderName"]:
                username = "You"
                align = 'right'
            else:
                username = row["SenderName"]



            newRow = (row["MessageID"], row["Timestamp"], base64.b64decode(row["EncryptedText"]).decode('utf-8'),align,profile_pic,username)

            decoded_result.append(newRow)

        return decoded_result






    @staticmethod
    def sendMessage(chat_id,user_id,_message):
        new_message = Message(_message,chat_id,user_id)
        new_message.send_message()



class Message:
    def __init__(self,message,chat_id,sender_id):
        self.gpg = gnupg.GPG()
        self.messages = []
        self.encrypted_messages = []
        self.time = datetime.datetime.now()
        self.sender_id = sender_id
        self.chat_id = chat_id
        self.users_sent_to = []

        public_keys = self.get_public_keys()
        for key in public_keys:
            decoded_key = base64.b64decode(key).decode('utf-8')
            gpg = gnupg.GPG()
            import_result = gpg.import_keys(decoded_key)
            if not import_result.fingerprints:
                raise ValueError("Invalid public key retrieved from the database.")
            else:
                print("good public key")
            encrypted_message = Password.encrypt(message,decoded_key.replace('\r\n', '\n'))
            encrypted_message_encoded = base64.b64encode(str(encrypted_message).encode('utf-8')).decode('utf-8')

            self.encrypted_messages.append(encrypted_message_encoded)



    def get_public_keys(self):
        public_keys = []
        query ="SELECT Users.ID FROM SecureApp.ChatUser JOIN SecureApp.Users ON ChatUser.UserID = Users.ID WHERE ChatUser.ChatID = %s;"
        self.users_sent_to = Account.executeQuery(query,[self.chat_id])


        for user in self.users_sent_to:
            query = "SELECT PublicKey FROM SecureApp.Passwords WHERE UserID = %s"
            public_key = Account.executeQuery(query, [user[0]])[0][0]
            public_keys.append(public_key)
        return public_keys




    def send_message(self):
        print(self.chat_id,self.sender_id)
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tamer2006",
            database="SecureApp"
        )
        cursor = connection.cursor(buffered=True)

        query = "SELECT ID FROM ChatUser WHERE ChatID = %s AND UserID = %s"
        cursor.execute(query,[self.chat_id,self.sender_id])

        chat_user_id = cursor.fetchall()[0][0]


        query ="INSERT INTO Message (ChatID, ChatUserID) VALUES (%s, %s)"
        cursor.execute(query,[self.chat_id,chat_user_id])
        connection.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        message_id = cursor.fetchall()[0][0]
        query = "SELECT ID FROM SecureApp.ChatUser WHERE ChatID = %s;"
        cursor.execute(query,[self.chat_id])
        chat_user_ids = cursor.fetchall()


        for i, encrypted_message in enumerate( self.encrypted_messages):

            query = "INSERT INTO encryptedmessage (MessageID,ChatUserID,EncryptedText) VALUES (%s, %s, %s)"
            cursor.execute(query,[message_id,chat_user_ids[i][0],encrypted_message])
        connection.commit()
        cursor.close()
    def encryptMessage(self, plain_text_password, public_key):

        # Import the public key string temporarily
        import_result = self.gpg.import_keys(public_key)

        # Extract the first fingerprint (or key ID) from the import result
        fingerprint = import_result.fingerprints[0]

        # Perform encryption using the fingerprint of the imported key
        encrypted_data = self.gpg.encrypt(plain_text_password, fingerprint, always_trust=True)
        # Return the encrypted data as a string
        return str(encrypted_data)


