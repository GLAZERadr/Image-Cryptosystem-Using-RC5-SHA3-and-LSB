import cv2
import numpy as np

def calculate_mse_and_psnr(plainImagePath, coverImagePath):
    # Memuat gambar
    plainImage = cv2.imread(plainImagePath)
    coverImage = cv2.imread(coverImagePath)

    # Memeriksa apakah gambar berhasil dimuat
    if plainImage is None or coverImage is None:
        print("Failed to load one or both images.")
        return None, None

    # Mengubah ukuran gambar kedua agar sesuai dengan ukuran gambar pertama
    h, w, c = coverImage.shape
    plainImage = cv2.resize(plainImage, (w, h))
    
    # Mengubah tipe data gambar dari integer (misalnya, uint8) ke float32 untuk menghindari overflow saat perhitungan dan meningkatkan akurasi.
    plainImage = plainImage.astype(np.float32)
    coverImage = coverImage.astype(np.float32)

    # Menghitung selisih antara gambar asli dan terdistorsi untuk setiap pixel.
    diff = np.subtract(plainImage, coverImage)
    # Menghitung kuadrat dari selisih tersebut.
    squared_diff = np.square(diff)
    # Menghitung rata-rata dari kuadrat selisih
    mse = np.mean(squared_diff)
    
    if mse == 0:
        # Menghindari pembagian dengan nol dan mengembalikan nilai PSNR tak hingga
        psnr = float('inf')
    else:
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel) - 10 * np.log10(mse)
    
    return mse, psnr

# Path ke gambar
plainImagePath = 'D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\BarangTerlaku TiapNegara.png'
coverImagePath = 'D:\Tech Projects\JOKI\Cryptosystem RC5 SHA3 LSB\Images\HiddenImage.jpg'

# Menghitung MSE dan PSNR
mse, psnr_score = calculate_mse_and_psnr(plainImagePath, coverImagePath)

if mse is not None and psnr_score is not None:
    print("MSE:", mse)
    print("PSNR:", psnr_score)
