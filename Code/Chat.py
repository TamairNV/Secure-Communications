import gnupg

import datetime

from Code.Account import Account


class Chat:
    @staticmethod
    def createChat(name,owner):
        query = "SELECT Name FROM Chat WHERE Owner_ID = %s"
        all_Names = Account.executeQuery(query,owner)
        if name in all_Names:
            return False

        query = "INSERT INTO chats (Name) VALUES (%s)"
        Account.executeQuery(query,[name])

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
        SELECT c.ID AS ChatID, c.Name AS ChatName
        FROM ChatUser cu
        JOIN Chat c ON cu.ChatID = c.ID
        WHERE cu.UserID = %s;
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
        self.createChatMember()

    @staticmethod
    def get_chat_messages(chat_id, user_id):
        query = """
        SELECT m.ID AS MessageID, m.Timestamp, em.EncryptedText
        FROM Message m
        JOIN EncryptedMessage em ON m.ID = em.MessageID
        JOIN ChatUser cu ON em.ChatUserID = cu.ID
        WHERE m.ChatID = %s
          AND cu.UserID = %s;
        """
        result = Account.executeQuery(query, [chat_id, user_id])
        return result


    @staticmethod
    def sendMessage(chat_id,user_id,_message):
        new_message = message(_message,chat_id,user_id)
        new_message.send_message()


    @staticmethod
    def get():
        query = "SELECT m.ID AS MessageID, m.Timestamp, em.EncryptedText FROM Message m JOIN EncryptedMessage em ON m.ID = em.MessageID JOIN ChatUser cu ON em.ChatUserID = cu.ID WHERE m.ChatID = %s   AND cu.UserID = %s;"
        Account.executeQuery(query,)

class message:
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
            self.encrypted_messages.append(self.gpg.encrypt(message,key))



    def get_public_keys(self):
        public_keys = []
        query =" SELECT u.ID FROM ChatUser cu JOIN Users u ON cu.UserID = u.ID WHERE cu.ChatID = %s;"
        users_sent_to = Account.executeQuery(query,[self.chat_id])[0]

        for user in users_sent_to:
            query = "SELECT PublicKey FROM users WHERE id = %s"
            public_key = Account.executeQuery(query, [user])[0][0]
            public_keys.append(public_key)
        return public_keys




    def send_message(self):
        query ="INSERT INTO Message (ChatID, ChatUserID) VALUES (%s, %s)"
        Account.executeQuery(query,[self.chat_id, self.sender_id])

        query = "SELECT LAST_INSERT_ID()"
        result = Account.executeQuery(query)
        message_id = result[0][0]

        for i, encrypted_message in enumerate( self.encrypted_messages):
            query = "INSERT INTO encryptedmessage (MessageID,ChatUserID,EncryptedText) VALUES (%s, %s, %s)"
            Account.executeQuery(query,[message_id,self.users_sent_to[i],encrypted_message])






    def encryptMessage(self, plain_text_password, public_key):

        # Import the public key string temporarily
        import_result = self.gpg.import_keys(public_key)

        # Extract the first fingerprint (or key ID) from the import result
        fingerprint = import_result.fingerprints[0]

        # Perform encryption using the fingerprint of the imported key
        encrypted_data = self.gpg.encrypt(plain_text_password, fingerprint, always_trust=True)
        # Return the encrypted data as a string
        return str(encrypted_data)