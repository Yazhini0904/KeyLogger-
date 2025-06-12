from cryptography.fernet import Fernet

# Load encryption key
with open("encryption_key.txt", "rb") as key_file:
    key = key_file.read()

# Read the encrypted file
with open("e_system.txt", "rb") as encrypted_file:
    encrypted_data = encrypted_file.read()

# Decrypt the data
fernet = Fernet(key)
decrypted_data = fernet.decrypt(encrypted_data)

# Save decrypted file
with open("decrypted_output.txt", "wb") as decrypted_file:
    decrypted_file.write(decrypted_data)

print("[+] File decrypted successfully.")
