from cryptography.fernet import Fernet
from Config.config import key

f = Fernet(key)

token = f.encrypt(b'Insert Text Here')

print(token)

print(str(f.decrypt(token), encoding='utf-8'))
