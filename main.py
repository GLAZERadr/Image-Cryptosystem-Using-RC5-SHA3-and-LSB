import sys
from PIL import Image
sys.path.append('src')

from RC5Encryption import RC5Encryption

# Test Methods
key = 'supersecretkey'
rc5 = RC5Encryption(key)

# Encrypt the image
rc5.encrypt_image('Images\TestImages.jpg', 'Images\Results\Encrypted\encrypted_image.rc5')

# Decrypt the image
rc5.decrypt_image('Images\Results\Encrypted\encrypted_image.rc5', 'Images\Results\Decrypted\decrypted_image.jpg')

with open('Images\Results\Encrypted\encrypted_image.rc5', "rb") as file:
    encrypted_data = file.read()

encrypted_image = Image.frombytes('L', (256, 256), encrypted_data[:256*256])
encrypted_image.show()