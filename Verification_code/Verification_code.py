import random
import string
import os
from PIL import Image, ImageDraw, ImageFont

def generate_random_string(length=5):
    chars = '0123456789abdefghjklmnpqrst~!@#$%^&*()uwyABDEFGHJKLMNPQRSTUY'
    return ''.join(random.choices(chars, k=length))

def generate_random_filename(length=16):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length)) + '.png'

def draw_rotated_text(image, text, font_sizes, image_width, image_height):
    draw = ImageDraw.Draw(image)
    char_images = []

    for font_size in sorted(font_sizes, reverse=True):
        char_images.clear()
        for char in text:
            font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), "arial.ttf"), font_size)
            angle = random.randint(-30, 30)

            text_image = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_image)
            text_draw.text((0, 0), char, font=font, fill=(0, 0, 0))

            rotated = text_image.rotate(angle, expand=True)
            bbox = rotated.getbbox()
            char_images.append((rotated, bbox))

        total_width = sum(bbox[2] for _, bbox in char_images) + (len(char_images) - 1) * 5
        if total_width <= image_width:
            break

    x = (image_width - total_width) // 2

    for rotated, bbox in char_images:
        image.paste(rotated, (x, (image_height - bbox[3]) // 2), rotated)
        x += bbox[2] + 5

def add_interference_lines(draw, image_width, image_height):
    for _ in range(5):
        x1, y1 = random.randint(0, image_width), random.randint(0, image_height)
        x2, y2 = random.randint(0, image_width), random.randint(0, image_height)
        draw.line([x1, y1, x2, y2], fill=(0, 0, 0), width=2)
    
    for _ in range(3):
        points = [(
            random.randint(0, image_width),
            random.randint(0, image_height)
        ) for _ in range(5)]
        draw.line(points, fill=(0, 0, 0), width=2)
    
    for _ in range(3):
        start_x = random.randint(0, image_width // 2)
        start_y = random.randint(0, image_height // 2)
        end_x = random.randint(image_width // 2, image_width)
        end_y = random.randint(image_height // 2, image_height)
        draw.arc([start_x, start_y, end_x, end_y], start=random.randint(0, 360), end=random.randint(0, 360), fill=(0, 0, 0), width=2)

    for _ in range(2):
        start_x = random.randint(0, image_width // 2)
        start_y = random.randint(0, image_height)
        end_x = start_x + random.randint(20, 40)
        for _ in range(5):
            draw.arc([start_x, start_y, start_x + 20, start_y + 20], 0, 180, fill=(0, 0, 0), width=2)
            start_x += 20

def add_interference_dots(draw, image_width, image_height):
    for _ in range(500):
        x, y = random.randint(0, image_width), random.randint(0, image_height)
        draw.point([x, y], fill=(0, 0, 0))

def add_interference_polygons(draw, image_width, image_height):
    for _ in range(2):
        points = [(
            random.randint(0, image_width),
            random.randint(0, image_height)
        ) for _ in range(6)]
        draw.polygon(points, outline=(0, 0, 0))

def add_interference_bezier(draw, image_width, image_height):
    for _ in range(2):
        start = (random.randint(0, image_width), random.randint(0, image_height))
        control1 = (random.randint(0, image_width), random.randint(0, image_height))
        control2 = (random.randint(0, image_width), random.randint(0, image_height))
        end = (random.randint(0, image_width), random.randint(0, image_height))
        draw.line([start, control1, control2, end], fill=(0, 0, 0), width=2)

def generate_captcha():
    image_width, image_height = 240, 135
    image = Image.new('RGB', (image_width, image_height), color='white')
    
    text = generate_random_string()
    font_sizes = [50, 45, 40]

    draw_rotated_text(image, text, font_sizes, image_width, image_height)
    draw = ImageDraw.Draw(image)
    add_interference_lines(draw, image_width, image_height)
    add_interference_dots(draw, image_width, image_height)
    add_interference_polygons(draw, image_width, image_height)
    add_interference_bezier(draw, image_width, image_height)

    filename = generate_random_filename()
    image.save(filename)

    print(f"Verification code is: {text}, saved as {filename}")

# 运行生成验证码的函数
generate_captcha()
