import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt(minutiae, password):
    encoded_minutiae = json.dumps(minutiae).encode('utf-8')    
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(16)

    # Encrypt the minutiae data
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the data to the block size of the cipher
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(encoded_minutiae) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Encode the salt, IV, and encrypted data to store or transmit
    encrypted_package = {
        'salt': urlsafe_b64encode(salt).decode('utf-8'),
        'iv': urlsafe_b64encode(iv).decode('utf-8'),
        'data': urlsafe_b64encode(encrypted_data).decode('utf-8')
    }

    return encrypted_package

def decrypt(encrypted_package, password):
    # Decode the salt, IV, and encrypted data for decryption
    salt = urlsafe_b64decode(encrypted_package['salt'])
    iv = urlsafe_b64decode(encrypted_package['iv'])
    encrypted_data = urlsafe_b64decode(encrypted_package['data'])

    # Derive the key again using the same password and salt
    key = derive_key(password, salt)

    # Decrypt the minutiae data
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Unpad the data to retrieve the original minutiae
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    # Convert bytes back to JSON string and then to original data structure
    decrypted_minutiae = json.loads(decrypted_data.decode('utf-8'))

    return decrypted_minutiae

def main():
    # Sample minutiae data
    minutiae = [
        {'locX': 123, 'locY': 456, 'Orientation': 30, 'Type': 'ending'},
        {'locX': 789, 'locY': 101, 'Orientation': 60, 'Type': 'bifurcation'}
    ]
    
    # Password for encryption and decryption
    password = "strongpassword"

    print("Original minutiae data:")
    for m in minutiae:
        print(m)
    
    # Encrypt the minutiae data
    encrypted_package = encrypt(minutiae, password)
    print("\nEncrypted package:")
    print(encrypted_package)

    # Decrypt the minutiae data
    decrypted_minutiae = decrypt(encrypted_package, password)
    print("\nDecrypted minutiae data:")
    for m in decrypted_minutiae:
        print(m)

if __name__ == "__main__":
    main()
