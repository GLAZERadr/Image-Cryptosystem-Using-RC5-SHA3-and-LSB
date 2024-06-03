# import sys
# from PIL import Image
# sys.path.append('encryption')

# from RC5Encryption import RC5Encryption
# from LSBSteganography import LSBSteganography
# from SHA3KECCAK import KeccakHash

# def cryptography():
#     key = "secretkey123"

#     #images path
#     input_image_path = "D:\Tech Projects\JOKI\ImageToCipherImages\Images\Barang Terlaku Tiap Negara.png" # ini path untuk input image yang mau di enkripsi
#     encrypted_image_path = "D:\Tech Projects\JOKI\ImageToCipherImages\Images\Results\Encrypted\encrypted_image.txt" # ini path untuk nyimpen hasil enkripsi 
#     decrypted_image_path = "D:\Tech Projects\JOKI\ImageToCipherImages\Images\Results\Decrypted\decrypted_image.jpg" # ini path untuk nyimpen hasil dekripsi
#     cover_images_path = "D:\Tech Projects\JOKI\ImageToCipherImages\Images\HiddenImage.jpg" # path untuk input cover image yang mau disipin hash value
#     encoded_image_path = "D:\Tech Projects\JOKI\ImageToCipherImages\Images\Results\Encoded\encoded_image.png" # path untuk nyimpen hasil encoding

#     hash_output_length = 32  # 256-bit hash

#     # Encrypt the image using RC5
#     rc5 = RC5Encryption(key)
#     rc5.encrypt_image(input_image_path, encrypted_image_path)

#     # Hash the encrypted image using SHA-3 (Keccak)
#     with open(encrypted_image_path, "rb") as encrypted_file:
#         encrypted_data = encrypted_file.read()

#     keccak = KeccakHash(encrypted_data, rate=136, delimited_suffix=0x06)
#     keccak.pad()
#     digest = keccak.squeeze(hash_output_length)
#     hash_value = digest.hex()

#     # Print the hash in hexadecimal format
#     print("SHA3-256 hash of the encrypted image:", hash_value)

#     # penyisipan cover images
#     lsb = LSBSteganography()

#     cover_images_file = Image.open(cover_images_path)
    
#     encoded_image =  lsb.encoding(cover_images_file, hash_value)
#     encoded_image.save(encoded_image_path)

#     encoded_image = Image.open(encoded_image_path)

#     hidden_messages = lsb.decoding(encoded_image)
#     print("Decoded message:", hidden_messages)

#     # hash the encrypted images
#     with open(encrypted_image_path, "rb") as encrypted_file:
#         encrypted_data = encrypted_file.read()

#     keccak = KeccakHash(encrypted_data, rate=136, delimited_suffix=0x06)
#     keccak.pad()
#     digest = keccak.squeeze(hash_output_length)
#     hash_value_of_encrypted_image_for_integrity_check = digest.hex()
#     print("hash value of encrypted image for integrity check: ", hash_value_of_encrypted_image_for_integrity_check)

#     # integrity checking 
#     if hash_value_of_encrypted_image_for_integrity_check == hidden_messages:
#         print("The integrity of the encrypted image has been verified.")

#         rc5.decrypt_image(encrypted_image_path, decrypted_image_path)
#     else:
#         print("The integrity of the encrypted image has been compromised.")

# if __name__ == "__main__":
#     main()