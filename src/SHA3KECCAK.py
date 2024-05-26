import numpy as np

# Constants for Keccak permutation steps
RHO_OFFSETS = [
     1,  3,  6, 10, 15, 21,
    28, 36, 45, 55,  2, 14,
    27, 41, 56,  8, 25, 43,
    62, 18, 39, 61, 20, 44
]

PI_INDEXES = [
    10,  7, 11, 17, 18, 3,
     5, 16,  8, 21, 24, 4,
    15, 23, 19, 13, 12, 2,
    20, 14, 22,  9,  6, 1
]

ROUND_CONSTANTS = np.array([
  0x0000000000000001, 0x0000000000008082,
  0x800000000000808a, 0x8000000080008000,
  0x000000000000808b, 0x0000000080000001,
  0x8000000080008081, 0x8000000000008009,
  0x000000000000008a, 0x0000000000000088,
  0x0000000080008009, 0x000000008000000a,
  0x000000008000808b, 0x800000000000008b,
  0x8000000000008089, 0x8000000000008003,
  0x8000000000008002, 0x8000000000000080,
  0x000000000000800a, 0x800000008000000a,
  0x8000000080008081, 0x8000000000008080,
  0x0000000080000001, 0x8000000080008008
], dtype=np.uint64)

ABSORBING = 1
SQUEEZING = 2

def rotate_left(x, shift):
    return (np.uint64(x) << np.uint64(shift)) ^ (np.uint64(x) >> np.uint64(64 - shift))

class KeccakPermutation:
    def __init__(self):
        self.state = np.zeros(25, dtype=np.uint64)

    def F1600(self):
        state = self.state
        temp_state = np.zeros(5, dtype=np.uint64)

        for round_index in range(24):
            
            # Step 1: Calculate parity
            for x in range(5):
                temp_state[x] = 0
                for y in range(0, 25, 5):
                    temp_state[x] ^= state[x + y]

            # Step 2: Apply theta step
            for x in range(5):
                theta_val = temp_state[(x + 4) % 5] ^ rotate_left(temp_state[(x + 1) % 5], 1)
                for y in range(0, 25, 5):
                    state[y + x] ^= theta_val

            # Step 3: Apply rho and pi steps
            current_val = state[1]
            for x in range(24):
                temp_state[0] = state[PI_INDEXES[x]]
                state[PI_INDEXES[x]] = rotate_left(current_val, RHO_OFFSETS[x])
                current_val = temp_state[0]

            # Step 4: Apply chi step
            for y in range(0, 25, 5):
                for x in range(5):
                    temp_state[x] = state[y + x]
                for x in range(5):
                    state[y + x] = temp_state[x] ^ ((~temp_state[(x + 1) % 5]) & temp_state[(x + 2) % 5])

            # Step 5: Apply iota step
            state[0] ^= ROUND_CONSTANTS[round_index]

        self.state = state

    def __repr__(self):
        return '\n'.join(
            ' '.join(f'{self.state[i+j]:016x}'.replace('0', '-') for j in range(5))
            for i in range(0, 25, 5)
        )

class KeccakHash:
    def __init__(self, data=b'', rate=None, delimited_suffix=None):
        if rate < 0 or rate > 199:
            raise ValueError("Rate must be between 0 and 199.")
        self.rate = rate
        self.delimited_suffix = delimited_suffix
        self.buffer_index = 0
        self.permutation = KeccakPermutation()
        self.buffer = np.zeros(200, dtype=np.uint8)
        self.direction = ABSORBING
        self.absorb(data)

    def absorb(self, data):
        data_len = len(data)
        index = 0
        while data_len > 0:
            space_available = self.rate - self.buffer_index
            bytes_to_absorb = min(space_available, data_len)
            self.buffer[self.buffer_index:self.buffer_index + bytes_to_absorb] ^= \
                np.frombuffer(data[index:index + bytes_to_absorb], dtype=np.uint8)
            self.buffer_index += bytes_to_absorb
            if self.buffer_index == self.rate:
                self.permute()
            data_len -= bytes_to_absorb
            index += bytes_to_absorb

    def squeeze(self, output_length):
        remaining = output_length
        output = b''
        while remaining > 0:
            available_to_squeeze = self.rate - self.buffer_index
            bytes_to_squeeze = min(available_to_squeeze, remaining)
            output += self.permutation.state.view(dtype=np.uint8)[self.buffer_index:self.buffer_index + bytes_to_squeeze].tobytes()
            self.buffer_index += bytes_to_squeeze
            if self.buffer_index == self.rate:
                self.permute()
            remaining -= bytes_to_squeeze
        return output

    def pad(self):
        self.buffer[self.buffer_index] ^= self.delimited_suffix
        self.buffer[self.rate - 1] ^= 0x80
        self.permute()

    def permute(self):
        self.permutation.state ^= self.buffer.view(dtype=np.uint64)
        self.permutation.F1600()
        self.buffer_index = 0
        self.buffer[:] = 0

    def update(self, data):
        if self.direction == SQUEEZING:
            self.permute()
            self.direction = ABSORBING
        self.absorb(data)
        return self

    def __repr__(self):
        return f"KeccakHash(rate={self.rate}, delimited_suffix=0x{self.delimited_suffix:02x})"

# # Test Keccak (SHA-3) implementation
# if __name__ == "__main__":
#     # Example input data
#     data = b"hello world"

#     # Instantiate KeccakHash with a rate of 1088 bits (136 bytes) and delimited suffix of 0x06
#     keccak = KeccakHash(data, rate=136, delimited_suffix=0x06)

#     # Pad and squeeze the hash
#     keccak.pad()
#     digest = keccak.squeeze(32)  # 256-bit output

#     # Print the hash in hexadecimal format
#     print("SHA3-256('hello world') =", digest.hex())
