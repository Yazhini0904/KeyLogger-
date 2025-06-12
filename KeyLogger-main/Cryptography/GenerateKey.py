from cryptography.fernet import Fernet

# Generate a key
key = Fernet.generate_key()

# Write the key to a file
with open("encryption_key.txt", "wb") as file:
    file.write(key)
