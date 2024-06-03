from PIL import Image

class LSBSteganography():
    #encoding images
    def encoding(self,images, messages):
        length = len(messages)
        if length > 255:
            print("ukuran teks terlalu panjang melebihi 255 karakter!")
            return False
        encoded = images.copy()
        width, height = images.size
        index = 0
        for row in range(height):
            for col in range(width):
                if images.mode != 'RGB':
                    r, g, b ,a = images.getpixel((col, row))
                elif images.mode == 'RGB':
                    r, g, b = images.getpixel((col, row))
                # first value is length of messages
                if row == 0 and col == 0 and index < length:
                    asc = length
                elif index <= length:
                    c = messages[index -1]
                    asc = ord(c)
                else:
                    asc = b
                encoded.putpixel((col, row), (r, g , asc))
                index += 1
        return encoded

    #decoding images
    def decoding(self,images):
        width, height = images.size
        messages = ""
        index = 0
        for row in range(height):
            for col in range(width):
                if images.mode != 'RGB':
                    r, g, b ,a = images.getpixel((col, row))
                elif images.mode == 'RGB':
                    r, g, b = images.getpixel((col, row))  
                # first pixel r value is length of message
                if row == 0 and col == 0:
                    length = b
                elif index <= length:
                    messages += chr(b)
                index += 1

        return messages


# Load the image
# original_image = Image.open("D:\Tech Projects\JOKI\ImageToCipherImages\Images\HiddenImage.jpg")

# # Create an instance of LSBSteganography
# steganography = LSBSteganography()

# # Encode a message into the image
# encoded_image = steganography.encoding(original_image, "b7308f8e3a1acccdf661a53365ea4839121305a6b4d47a69b16a41007024b467")
# encoded_image.save("encoded_image.png")

# # Decode the message from the image
# decoded_message = steganography.decoding(encoded_image)
# print("Decoded message:", decoded_message)
