import base64
import os

class RC5Encryption(object):
    def __init__(self, key):
        self.key = key
        self.bs = 32
        self.r = 12
        self._key = key.encode('utf-8')
        self.init_vector = os.urandom(self.bs // 8)

    @staticmethod
    def _key_expansion(key, ws, r):
        def _align_key(key, value):
            while len(key) % value:
                key += b'\x00'
            L = []
            for i in range(0, len(key), value):
                L.append(int.from_bytes(key[i:i + value], byteorder='little'))
            return L

        def _constant(w):
            if w == 16:
                return (0xB7E1, 0x9E37)
            elif w == 32:
                return (0xB7E15163, 0x9E3779B9)
            elif w == 64:
                return (0xB7E151628AED2A6B, 0x9E3779B97F4A7C15)
            else:
                raise ValueError("w must be 16, 32, or 64")
            
        def _extending_key(w, r):
            P, Q = _constant(w)
            S = [P]
            t = 2 * (r + 1)
            for i in range(1, t):
                S.append((S[i - 1] + Q) % 2**w)
            return S
        
        def _mixing(L, S, r, w, c):
            t = 2 * (r + 1)
            m = max(c, t)
            A = B = i = j = 0
            for k in range(3 * m):
                A = S[i] = RC5Encryption._rotate_left((S[i] + A + B) % 2**w, 3, w)
                B = L[j] = RC5Encryption._rotate_left((L[j] + A + B) % 2**w, (A + B) % w, w)
                i = (i + 1) % t
                j = (j + 1) % c
            return S
        
        aligned_key = _align_key(key, ws // 8)
        extended_key = _extending_key(ws, r)
        S = _mixing(aligned_key, extended_key, r, ws, len(aligned_key))
        return S

    @staticmethod
    def _rotate_left(val, r_bits, max_bits):
        return ((val << r_bits % max_bits) & (2 ** max_bits - 1)) | ((val & (2 ** max_bits - 1)) >> (max_bits - (r_bits % max_bits)))

    @staticmethod
    def _rotate_right(val, r_bits, max_bits):
        return ((val & (2 ** max_bits - 1)) >> r_bits % max_bits) | (val << (max_bits - r_bits % max_bits) & (2 ** max_bits - 1))

    @staticmethod
    def _encrypt_block(data, expanded_key, block_size, rounds):
        half_block_size = block_size // 2
        block = block_size // 8

        firstPart = int.from_bytes(data[:block // 2], byteorder='little')
        secPart = int.from_bytes(data[block // 2:], byteorder='little')

        firstPart = (firstPart + expanded_key[0]) % 2**half_block_size
        secPart = (secPart + expanded_key[1]) % 2**half_block_size

        for i in range(1, rounds + 1):
            firstPart = (RC5Encryption._rotate_left((firstPart ^ secPart), secPart, half_block_size) + expanded_key[2 * i]) % 2**half_block_size
            secPart = (RC5Encryption._rotate_left((firstPart ^ secPart), firstPart, half_block_size) + expanded_key[2 * i + 1]) % 2**half_block_size

        encrypted_block = firstPart.to_bytes(block // 2, byteorder='little') + secPart.to_bytes(block // 2, byteorder='little')
        return encrypted_block

    @staticmethod
    def _decrypt_block(data, expanded_key, block_size, rounds):
        half_block_size = block_size // 2
        block = block_size // 8

        firstPart = int.from_bytes(data[:block // 2], byteorder='little')
        secPart = int.from_bytes(data[block // 2:], byteorder='little')

        for i in range(rounds, 0, -1):
            secPart = RC5Encryption._rotate_right((secPart - expanded_key[2 * i + 1]) % 2**half_block_size, firstPart, half_block_size) ^ firstPart
            firstPart = RC5Encryption._rotate_right((firstPart - expanded_key[2 * i]) % 2**half_block_size, secPart, half_block_size) ^ secPart

        secPart = (secPart - expanded_key[1]) % 2**half_block_size
        firstPart = (firstPart - expanded_key[0]) % 2**half_block_size

        decrypted_block = firstPart.to_bytes(block // 2, byteorder='little') + secPart.to_bytes(block // 2, byteorder='little')
        return decrypted_block

    def encrypt_file(self, input_file, output_file):
        block_size = self.bs // 8
        init_vector = self.init_vector

        output_file.write(init_vector)
        expanded_key = RC5Encryption._key_expansion(self._key, self.bs, self.r)

        chunk = input_file.read(block_size)
        while chunk:
            chunk = chunk.ljust(block_size, b'\x00')
            chunk = bytes([a ^ b for a, b in zip(init_vector, chunk)])
            encrypted_chunk = RC5Encryption._encrypt_block(chunk, expanded_key, self.bs, self.r)
            output_file.write(encrypted_chunk)
            init_vector = encrypted_chunk
            chunk = input_file.read(block_size)

    def decrypt_file(self, input_file, output_file):
        block_size = self.bs // 8
        init_vector = input_file.read(block_size)
        expanded_key = RC5Encryption._key_expansion(self._key, self.bs, self.r)

        chunk = input_file.read(block_size)
        while chunk:
            decrypted_chunk = RC5Encryption._decrypt_block(chunk, expanded_key, self.bs, self.r)
            decrypted_chunk = bytes([a ^ b for a, b in zip(init_vector, decrypted_chunk)])
            output_file.write(decrypted_chunk)
            init_vector = chunk
            chunk = input_file.read(block_size)

    ### Methods to Encrypt and Decrypt Image
    def encrypt_image(self, input_image_path, output_image_path):
        with open(input_image_path, "rb") as input_file:
            with open(output_image_path, "wb") as output_file:
                self.encrypt_file(input_file, output_file)

    def decrypt_image(self, input_image_path, output_image_path):
        with open(input_image_path, "rb") as input_file:
            with open(output_image_path, "wb") as output_file:
                self.decrypt_file(input_file, output_file)