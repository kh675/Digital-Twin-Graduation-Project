from PIL import Image, ImageDraw, ImageFont
import os

def create_banner():
    # Create a blue banner
    img = Image.new('RGB', (800, 300), color = '#1f77b4')
    d = ImageDraw.Draw(img)
    
    # Save it
    if not os.path.exists('dashboard/assets'):
        os.makedirs('dashboard/assets')
    img.save('dashboard/assets/banner.png')
    print("Banner created successfully")

if __name__ == "__main__":
    create_banner()
