
import bcrypt
import gnupg
import os
import configparser
import os


class Password:
    config = configparser.ConfigParser()
    config.read("config.ini")

    def __init__(self,public_key):
        self.hashed_password = None
        self.salt = None
        self.publicKey = public_key
        self.gpg = gnupg.GPG()
        self.store_public_key = Password.read_public_key()





    def __str__(self):
        return f"Hashed Password:{self.hashed_password}\nSalt:{self.salt}\n Key figure Print:{self.key}"

    def check_password(self, plain_text_password):
        # Validate a password against the stored hash
        return bcrypt.hashpw(plain_text_password.encode(), bytes(self.salt)) == self.hashed_password

    def init_password(self,plain_text_password):
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(plain_text_password.encode(), self.salt)

    def load_password(self,salt,hashed_password):
        self.salt = salt
        self.hashed_password = hashed_password



    def encrypt(self, plain_text_password):

        # Import the public key string temporarily
        import_result = self.gpg.import_keys(self.publicKey)

        # Extract the first fingerprint (or key ID) from the import result
        fingerprint = import_result.fingerprints[0]

        # Perform encryption using the fingerprint of the imported key
        encrypted_data = self.gpg.encrypt(plain_text_password, fingerprint, always_trust=True)
        # Return the encrypted data as a string
        return str(encrypted_data)

    def generate_certificate(self,message):
        import_result = self.gpg.import_keys(Password.read_private_key())
        fingerprint = import_result.fingerprints[0]
        signed_message = self.gpg.sign(
            message,
            default_key =fingerprint
        )
        return signed_message

    @staticmethod
    def read_private_key():
       # Path to your private key file
       key_file_path = Password.config.get("SECURITY", "private_key_path")


       # Check if the file exists

       if os.path.exists(key_file_path):
           with open(key_file_path, 'r') as key_file:
                private_key = key_file.read()
                return private_key
       else:
           raise FileNotFoundError("Private key file not found!")

    @staticmethod
    def read_public_key():
        key_file_path = Password.config.get("SECURITY", "public_key_path")  # Path to your public key file

        # Check if the file exists
        if os.path.exists(key_file_path):
            with open(key_file_path, 'r') as key_file:
                private_key = key_file.read()
                return private_key
        else:
            raise FileNotFoundError("Private key file not found!")



# Example usage
if __name__ == "__main__":
    pass

