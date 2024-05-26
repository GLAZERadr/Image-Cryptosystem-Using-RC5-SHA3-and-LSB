from PIL import Image

# ini yang buat nyisipin image tapi pixelnya itu kebesaran gk bisa jadi hidden images
class LSBSteganography2:
    # Encoding part
    def encode_image(self, base_image_path, hidden_image_path, output_image_path):
        # Open base image (steganography image)
        base_image = Image.open(base_image_path)
        base_pixels = base_image.load()

        # Open hidden image
        hidden_image = Image.open(hidden_image_path)
        hidden_pixels = hidden_image.load()

        # Check if hidden image fits into base image
        if hidden_image.size[0] * hidden_image.size[1] > base_image.size[0] * base_image.size[1]:
            print("Hidden image is too large for base image.")
            return False

        # Embed hidden image into base image LSB
        for y in range(hidden_image.size[1]):
            for x in range(hidden_image.size[0]):
                # Get pixel values of hidden image
                hidden_pixel = hidden_pixels[x, y]
                hidden_r, hidden_g, hidden_b = hidden_pixel

                # Get pixel values of base image
                base_x = x % base_image.size[0]
                base_y = y % base_image.size[1]
                base_pixel = base_pixels[base_x, base_y]
                base_r, base_g, base_b = base_pixel

                # Modify LSB of base image pixels with hidden image pixels
                modified_r = (base_r & 0xFE) | ((hidden_r & 0xC0) >> 6)
                modified_g = (base_g & 0xFC) | ((hidden_g & 0xF0) >> 4)
                modified_b = (base_b & 0xF8) | ((hidden_b & 0xF8) >> 3)

                # Update base image pixel with modified values
                base_pixels[base_x, base_y] = (modified_r, modified_g, modified_b)

        # Save the modified base image
        base_image.save(output_image_path)
        return True

    # Decoding part
    def decode_image(self, base_image_path, hidden_image_size, output_image_path):
        # Open base image (steganography image)
        base_image = Image.open(base_image_path)
        base_pixels = base_image.load()

        # Create an image for the hidden image
        hidden_image = Image.new("RGB", hidden_image_size)
        hidden_pixels = hidden_image.load()

        # Extract hidden image from base image LSB
        for y in range(hidden_image.size[1]):
            for x in range(hidden_image.size[0]):
                # Get pixel values of base image
                base_x = x % base_image.size[0]
                base_y = y % base_image.size[1]
                base_pixel = base_pixels[base_x, base_y]
                base_r, base_g, base_b = base_pixel

                # Extract LSB and reconstruct hidden image pixels
                hidden_r = (base_r & 0x01) << 6
                hidden_g = (base_g & 0x03) << 4
                hidden_b = (base_b & 0x07) << 3

                # Combine extracted bits to form the hidden pixel
                hidden_pixel = (hidden_r, hidden_g, hidden_b)
                hidden_pixels[x, y] = hidden_pixel

        # Save the extracted hidden image
        hidden_image.save(output_image_path)
        return True

steganography = LSBSteganography2()
steganography.encode_image('D:\Tech Projects\JOKI\ImageToCipherImages\Images\HiddenImage.jpg', 'D:\Tech Projects\JOKI\ImageToCipherImages\Images\HiddenImage.jpg', 'output_image.png')