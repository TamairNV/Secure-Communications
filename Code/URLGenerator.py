import mysql.connector
from mysql.connector import pooling
from Code.Account import Account
from Code.Password import Password
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler

class URLGenerator:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="my_pool",
        pool_size=5,
        host="localhost",
        user="root",
        password="Tamer2006",
        database="SecureApp"
    )
    secret_key = Password.read_private_key()
    DEFAULT_TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME", 300))  # Default: 5 minutes

    @staticmethod
    def cleanup_expired_tokens():
        query = "DELETE FROM SecureApp.Tokens WHERE expires_at <= %s"
        URLGenerator.executeQuery(query, [datetime.now()])

    @staticmethod
    def generate_2fa_token(user_id, life_time=DEFAULT_TOKEN_LIFETIME):
        while True:
            token = URLGenerator.generate_token_hash()
            query = "SELECT token_hash FROM SecureApp.Tokens WHERE token_hash = %s"
            result = URLGenerator.executeQuery(query, [token])
            if not result:
                break  # Token is unique
        query = "INSERT INTO SecureApp.Tokens(user_id, token_hash, expires_at) VALUES (%s, %s, %s)"
        URLGenerator.executeQuery(query, [user_id, token, datetime.now() + timedelta(seconds=life_time)])
        return token

    @staticmethod
    def generate_token_hash():
        random_string = secrets.token_urlsafe(16)  # 16 bytes of randomness
         #Hash the random string using SHA-256
        sha256_hash = hashlib.sha256(random_string.encode('utf-8')).digest()

        # Encode the hash in Base64 for URL-safe usage
        base64_token = base64.urlsafe_b64encode(sha256_hash).decode('utf-8')

        return base64_token

    @staticmethod
    def validate_2fa_token(token):
        query = "SELECT user_id FROM SecureApp.Tokens WHERE token_hash = %s AND expires_at > %s"
        result = URLGenerator.executeQuery(query, [token, datetime.now()])
        if not result:
            return -1  # Token not found or expired
        return result[0][0]

    @staticmethod
    def executeQuery(query, values=None):
        connection = URLGenerator.connection_pool.get_connection()
        cursor = connection.cursor()
        try:
            if values is None:
                cursor.execute(query)
                result = cursor.fetchall()
            else:
                cursor.execute(query, values)
                result = cursor.fetchall()
            connection.commit()
            return result
        except Exception as e:
            print(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            connection.close()

# Schedule the cleanup task to run every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(URLGenerator.cleanup_expired_tokens, 'interval', minutes=5)
scheduler.start()