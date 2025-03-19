from werkzeug.security import generate_password_hash

hashed_password = generate_password_hash("12")
print(hashed_password)
