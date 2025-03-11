import gnupg

class Multisig:
    def __init__(self,message,user1,user2,user3):
        self.message = message
        self.user1 = user1
        self.user2 = user2
        self.user3 = user3
        self.encryptedMessages = {"":"","":"","":"","":""}


    def encrypt(self):
        # Encrypt the message using the public keys
        gpg = gnupg.GPG()
        encrypted_data = gpg.encrypt(self.message, [self.pubKey1, self.pubKey2, self.pubKey3], always_trust=True)
        return str(encrypted_data)







