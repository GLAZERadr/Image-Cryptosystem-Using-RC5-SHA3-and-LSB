from flask import Flask, request, render_template, send_file, redirect, flash, url_for, send_from_directory
import os
from io import BytesIO
import zipfile
from PIL import Image
import numpy as np
import cv2
from werkzeug.utils import secure_filename

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

@app.route('/pengujian', methods=['GET', 'POST'])
def testing():
    if request.method == 'POST':
        if 'plain_image' not in request.files or 'cover_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        plain_image_file = request.files['plain_image']
        cover_image_file = request.files['cover_image']

        if plain_image_file.filename == '' or cover_image_file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        plain_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(plain_image_file.filename))
        cover_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(cover_image_file.filename))

        plain_image_file.save(plain_image_path)
        cover_image_file.save(cover_image_path)

        plainImage = cv2.imread(plain_image_path)
        coverImage = cv2.imread(cover_image_path)

        # Resize images to 400x400
        plainImage_resized = cv2.resize(plainImage, (400, 400))
        coverImage_resized = cv2.resize(coverImage, (400, 400))

        # Save resized images to temporary paths
        plain_image_resized_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resized_' + plain_image_file.filename)
        cover_image_resized_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resized_' + cover_image_file.filename)

        cv2.imwrite(plain_image_resized_path, plainImage_resized)
        cv2.imwrite(cover_image_resized_path, coverImage_resized)

        h, w, c = coverImage.shape
        plainImage = cv2.resize(plainImage, (w, h))
        
        plainImage = plainImage.astype(np.float32)
        coverImage = coverImage.astype(np.float32)

        # Menghitung MSE
        diff = np.subtract(plainImage, coverImage)
        squared_diff = np.square(diff)
        mse = np.mean(squared_diff)
        
        if mse == 0:
            psnr = float('inf')
        else:
            # Menghitung PSNR
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel) - 10 * np.log10(mse)
        
        return render_template('hasil_pengujian.html', 
                        plain_image_path=url_for('uploaded_file', filename='resized_' + plain_image_file.filename),
                        cover_image_path=url_for('uploaded_file', filename='resized_' + cover_image_file.filename),
                        mse=mse, 
                        psnr=psnr)
    
    return render_template('pengujian.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
