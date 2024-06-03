from flask import Flask, request, render_template, send_file, redirect, flash
import os
from io import BytesIO
import zipfile
from PIL import Image

# cryptography system
from encryption.RC5Encryption import RC5Encryption
from encryption.LSBSteganography import LSBSteganography
from encryption.SHA3KECCAK import KeccakHash

app = Flask(__name__)
app.secret_key = "CryptoGraphy12"
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

SECRET_KEY = "AdrianBadjideh11"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        input_image = request.files['input_image']
        cover_image = request.files['cover_image']

        if input_image.filename == '' or cover_image.filename == '':
            return redirect(request.url)

        input_image_path = os.path.join(app.config['UPLOAD_FOLDER'], input_image.filename)
        cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_image.filename)
        encrypted_image_path = input_image_path + ".txt"
        encoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "encoded_image.png")

        input_image.save(input_image_path)
        cover_image.save(cover_image_path)

        # Encrypt the image using RC5
        rc5 = RC5Encryption(SECRET_KEY)
        rc5.encrypt_image(input_image_path, encrypted_image_path)

        # Hash the encrypted image using SHA-3 (Keccak)
        with open(encrypted_image_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        keccak = KeccakHash(encrypted_data, rate=136, delimited_suffix=0x06)
        keccak.pad()
        digest = keccak.squeeze(32)
        hash_value = digest.hex()

        # Embed the hash into the cover image using LSB steganography
        lsb = LSBSteganography()
        cover_images_file = Image.open(cover_image_path)
        encoded_image = lsb.encoding(cover_images_file, hash_value)
        encoded_image.save(encoded_image_path)

        # Create a ZIP file containing both the encrypted image and the encoded image
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.write(encrypted_image_path, os.path.basename(encrypted_image_path))
            zip_file.write(encoded_image_path, os.path.basename(encoded_image_path))

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="encrypted_and_encoded_images.zip"
        )

    return render_template('encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        encrypted_file = request.files['encrypted_file']
        encoded_image_file = request.files['encoded_image_file']

        if encrypted_file.filename == '' or encoded_image_file.filename == '':
            return redirect(request.url)

        encrypted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_file.filename)
        encoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], encoded_image_file.filename)
        decrypted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "decrypted_image.jpg")

        encrypted_file.save(encrypted_image_path)
        encoded_image_file.save(encoded_image_path)

        # Decode the hash from the encoded image
        lsb = LSBSteganography()
        encoded_image = Image.open(encoded_image_path)
        hidden_message = lsb.decoding(encoded_image)

        # Verify the integrity of the encrypted image
        with open(encrypted_image_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        keccak = KeccakHash(encrypted_data, rate=136, delimited_suffix=0x06)
        keccak.pad()
        digest = keccak.squeeze(32)
        hash_value_of_encrypted_image_for_integrity_check = digest.hex()

        if hash_value_of_encrypted_image_for_integrity_check == hidden_message:
            rc5 = RC5Encryption(SECRET_KEY)
            rc5.decrypt_image(encrypted_image_path, decrypted_image_path)
            return send_file(decrypted_image_path, as_attachment=True)
        else:
            flash("The integrity of the encrypted image has been compromised.")

    return render_template('decrypt.html')

if __name__ == "__main__":
    app.run(debug=True)
