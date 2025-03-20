from werkzeug.security import generate_password_hash

hashed_password = generate_password_hash("test")
print(hashed_password)
