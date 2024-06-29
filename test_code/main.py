# import sys
# import io
# from PIL import Image
# sys.path.append('encryption')

# from encryption.RC5Encryption import RC5Encryption
# from encryption.LSBSteganography import LSBSteganography
# from encryption.SHA3KECCAK import KeccakHash


# def main():
#     key = "AdrianBadjideh11"  # Ganti dengan kunci yang ingin Anda gunakan
#     rc5 = RC5Encryption(key)

#     input_image_path = "D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\Barang Terlaku Tiap Negara.png"
#     encrypted_image_path = "D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\Results\Encrypted\encrypted_image.jpg"
#     decrypted_image_path = "D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\Results\Decrypted\decrypted_image.jpg"
#     cover_images_path = "D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\HiddenImage.jpg" # path untuk input cover image yang mau disipin hash value
#     encoded_image_path = "D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\Results\Encoded\encoded_image.png" # path untuk nyimpen hasil encoding

#     # Enkripsi gambar
#     rc5.encrypt_image(input_image_path, encrypted_image_path)
#     print(f"Gambar telah berhasil dienkripsi menjadi {encrypted_image_path}")

#     # Membuka dan menampilkan gambar terenskripsi sebagai bytes
#     with open(encrypted_image_path, "rb") as file:
#         encrypted_data = file.read()

#     encrypted_image = Image.frombytes('L', (512, 512), encrypted_data[:512*512])
#     encrypted_image.show()

#     # Dekripsi gambar
#     # rc5.decrypt_image(encrypted_image_path, decrypted_image_path)
#     # print(f"Gambar telah berhasil didekripsi menjadi {decrypted_image_path}")

#     keccak_hash = KeccakHash(data=encrypted_data, rate=1088 // 8, delimited_suffix=0x06)
#     hash_output = keccak_hash.squeeze(32)  # 32 bytes = 256 bits
#     hash_hex = hash_output.hex()
#     print(f"SHA-3 hash of the encrypted image: {hash_hex}")

#     lsb = LSBSteganography()

#     cover_images_file = Image.open(cover_images_path)
    
#     encoded_image =  lsb.encoding(cover_images_file, hash_hex)
#     encoded_image.save(encoded_image_path)

#     encoded_image = Image.open(encoded_image_path)

#     hidden_messages = lsb.decoding(encoded_image)
#     print("Decoded message:", hidden_messages)

# if __name__ == "__main__":
#     main()
