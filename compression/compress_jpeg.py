from PIL import Image
import sys
import os

def compress_jpeg(input_path, output_path, quality=70):
    """
    Compress a JPEG image to half its original dimensions.
    
    Args:
        input_path (str): Path to the input JPEG image
        output_path (str): Path where the compressed image will be saved
        quality (int): JPEG quality (1-100), lower means more compression
    """
    try:
        with Image.open(input_path) as img:
            width, height = img.size
            
            new_width = width // 2
            new_height = height // 2
            
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            resized_img.save(output_path, "JPEG", quality=quality)
            
            print(f"Successfully compressed image from {width}x{height} to {new_width}x{new_height}")
            original_size = os.path.getsize(input_path) / 1024 
            new_size = os.path.getsize(output_path) / 1024  
            print(f"File size reduced from {original_size:.2f}KB to {new_size:.2f}KB")
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compress_jpeg.py <input_path> <output_path> [quality]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    quality = 70
    if len(sys.argv) > 3:
        try:
            quality = int(sys.argv[3])
            if quality < 1 or quality > 100:
                print("Quality must be between 1 and 100, using default quality of 70")
                quality = 70
        except ValueError:
            print("Invalid quality value, using default quality of 70")
    
    compress_jpeg(input_path, output_path, quality)