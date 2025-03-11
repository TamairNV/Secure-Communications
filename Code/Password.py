
import bcrypt
import gnupg

class Password:
    def __init__(self,plain_text_password,salt = None, hashed_Password = None,key = None):
        self.gpg = gnupg.GPG()
        # Generate a salt and hash the password using bcrypt
        if salt is None and hashed_Password is None and key is None:
            self.salt = bcrypt.gensalt()
            self.hashed_password = bcrypt.hashpw(plain_text_password.encode(), self.salt)
            self.key = self.generate_key_pair(plain_text_password)
            #self.export_keys(plain_text_password)
        else:
            self.salt = salt
            self.hashed_password = hashed_Password
            self.key = key

    def __str__(self):
        return f"Hashed Password:{self.hashed_password}\nSalt:{self.salt}\n Key figure Print:{self.key}"

    def check_password(self, plain_text_password, hashed_password):
        # Validate a password against the stored hash
        return bcrypt.hashpw(plain_text_password.encode(), self.salt) == hashed_password

    def generate_key_pair(self,password):
        # Generate GPG public/private key pair
        input_data = self.gpg.gen_key_input(
            name_real="name",
            name_email="email",
            passphrase=password
        )
        key = self.gpg.gen_key(input_data)
        return str(key)

    def export_keys(self, output_dir="keys/"):
        # Export public and private keys to files
        with open(f"{output_dir}public_key.asc", "w") as pub_file:
            pub_file.write(self.gpg.export_keys(self.key))
        with open(f"{output_dir}private_key.asc", "w") as priv_file:
            priv_file.write(self.gpg.export_keys(self.key, True))

    def get_public_key(self):
        return self.gpg.export_keys(str(self.key))



# Example usage
if __name__ == "__main__":
    sp = Password("Tamer2006")
    print(sp)
    # Verify the password
    is_valid = sp.check_password("Tamer2006", sp.hashed_password)
    print("Password Valid:", is_valid)

    # Generate GPG key pair

    print("Key Pair Generated:", sp.key)

