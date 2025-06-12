from cryptography.fernet import Fernet

# Generate and save encryption key
key = Fernet.generate_key()
with open("encryption_key.txt", "wb") as key_file:
    key_file.write(key)

# Encrypt the file
input_file = "plain_text.txt"       # The file you want to encrypt
output_file = "e_system.txt"        # The encrypted output

with open(input_file, "rb") as f:
    data = f.read()

fernet = Fernet(key)
encrypted_data = fernet.encrypt(data)

with open(output_file, "wb") as f:
    f.write(encrypted_data)

print("[+] File encrypted successfully.")
