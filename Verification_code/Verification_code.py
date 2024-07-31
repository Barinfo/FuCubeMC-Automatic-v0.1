import random
import string
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def generate_captcha_with_base64(length=5, image_width=240, image_height=135, font_sizes=[50, 45, 40]):
    def generate_random_string(length):
        chars = '0123456789abdefghjklmnpqrst@#$%&uwyABDEFGHJKLMNPQRSTUY'
        return ''.join(random.choices(chars, k=length))

    def draw_rotated_text(image, text, font_sizes, image_width, image_height):
        draw = ImageDraw.Draw(image)
        char_images = []

        for font_size in sorted(font_sizes, reverse=True):
            char_images.clear()
            for char in text:
                font = ImageFont.truetype("arial.ttf", font_size)
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

    image = Image.new('RGB', (image_width, image_height), color='white')
    
    text = generate_random_string(length)
    draw_rotated_text(image, text, font_sizes, image_width, image_height)
    draw = ImageDraw.Draw(image)
    add_interference_lines(draw, image_width, image_height)
    add_interference_dots(draw, image_width, image_height)
    add_interference_polygons(draw, image_width, image_height)
    add_interference_bezier(draw, image_width, image_height)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode()

    return text, base64_image

# 运行生成验证码的函数
captcha_text, captcha_base64 = generate_captcha_with_base64()
print(f"Verification code is: {captcha_text}")
print(f"Base64 image data: {captcha_base64}")
