from itsdangerous import URLSafeTimedSerializer

from Code.Account import Account
from Code.Password import Password


from flask import Flask, request, jsonify, url_for
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta

class URLGenerator:
   def __init__(self, user_id,salt):
       self.secret_key = Password.read_private_key()
       self.user_id = user_id
       self.salt = salt
       self.serializer = URLSafeTimedSerializer(self.secret_key)

       # Function to generate a 2FA token

   def generate_2fa_token(self):
       # Create a token with the user ID and an expiration time (e.g., 10 minutes)
       return self.serializer.dumps(self.user_id, salt=self.salt)



   def validate_2fa_token(self,token, max_age=600):
       try:
           # Decode the token and check if it's valid and not expired
           user_id = self.serializer.loads(token, salt=self.salt, max_age=max_age)
           return user_id
       except Exception as e:
           # Token is invalid or expired
           print(f"Token validation failed: {e}")
           return None

       # Route to simulate sending a 2FA link

   def create_2fa_link(self):

       # Generate a 2FA token
       token = self.generate_2fa_token()
       verification_url = url_for('verify_2fa', token=token, _external=True)
       return verification_url





