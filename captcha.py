import io
import base64
import os
import random
from PIL import Image, ImageDraw, ImageFont
from secrets import choice
from flask import session


class Captcha:
    def __init__(self, length=5, width=240, height=135, font_sizes=[50, 45, 40]) -> None:
        """
        参数:
        - length -- 验证码文本的长度，默认为5。
        - image_width -- 验证码图片的宽度，默认为240像素。
        - image_height -- 验证码图片的高度，默认为135像素。
        - font_sizes -- 用于渲染验证码文本的字体大小列表，默认为[50, 45, 40]。
        """
        self.length = length
        self.image_width = width
        self.image_height = height
        self.font_sizes = font_sizes

    def generate_random_text(self, length=5):
        return ''.join(choice('0123456789abdefghjkimnpqrst@#$%&uwyABDEFGHJKLMNPQRSTUY') for _ in range(length))

    def generate_captcha_image(self, text, font_sizes, image_width=240, image_height=135):
        image = Image.new('RGB', (image_width, image_height), color='white')
        char_images = self.draw_characters(text, font_sizes, image_width)
        self.place_characters(image, char_images)
        self.draw_distractions(image, image_width, image_height)
        return image

    def draw_characters(self, text, font_sizes, image_width):
        for font_size in sorted(font_sizes, reverse=True):
            char_image_list = []
            for char in text:
                font = ImageFont.truetype(os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), "arial.ttf"), font_size)
                angle = random.randint(-30, 30)
                text_image = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
                text_draw = ImageDraw.Draw(text_image)
                text_draw.text((0, 0), char, font=font, fill=(0, 0, 0))
                rotated = text_image.rotate(angle, expand=True)
                bbox = rotated.getbbox()
                char_image_list.append((rotated, bbox))
            total_width = sum(
                bbox[2] for _, bbox in char_image_list) + (len(char_image_list) - 1) * 5
            if total_width <= image_width:
                break
        return char_image_list

    def place_characters(self, image, char_images):
        x = (image.width - sum(bbox[2] for _, bbox in char_images)) // 2
        for rotated, bbox in char_images:
            image.paste(rotated, (x, (image.height - bbox[3]) // 2), rotated)
            x += bbox[2] + 5

    def draw_distractions(self, image, image_width, image_height):
        draw = ImageDraw.Draw(image)
        self.draw_lines(draw, image_width, image_height, 5)
        self.draw_curves(draw, image_width, image_height, 3)
        self.draw_arcs(draw, image_width, image_height, 3)
        self.draw_dots(draw, image_width, image_height)
        self.draw_polygons(draw, image_width, image_height, 2)
        self.draw_bezier_curves(draw, image_width, image_height, 2)

    def draw_lines(self, draw, image_width, image_height, count):
        for _ in range(count):
            x1, y1 = random.randint(
                0, image_width), random.randint(0, image_height)
            x2, y2 = random.randint(
                0, image_width), random.randint(0, image_height)
            draw.line([x1, y1, x2, y2], fill=(0, 0, 0), width=2)

    def draw_curves(self, draw, image_width, image_height, count):
        for _ in range(count):
            points = [(random.randint(0, image_width), random.randint(
                0, image_height)) for _ in range(5)]
            draw.line(points, fill=(0, 0, 0), width=2)

    def draw_arcs(self, draw, image_width, image_height, count):
        for _ in range(count):
            start_x = random.randint(0, image_width // 2)
            start_y = random.randint(0, image_height // 2)
            end_x = random.randint(image_width // 2, image_width)
            end_y = random.randint(image_height // 2, image_height)
            draw.arc([start_x, start_y, end_x, end_y], start=random.randint(
                0, 360), end=random.randint(0, 360), fill=(0, 0, 0), width=2)

    def draw_dots(self, draw, image_width, image_height):
        for _ in range(500):
            x, y = random.randint(
                0, image_width), random.randint(0, image_height)
            draw.point([x, y], fill=(0, 0, 0))

    def draw_polygons(self, draw, image_width, image_height, count):
        for _ in range(count):
            points = [(random.randint(0, image_width), random.randint(
                0, image_height)) for _ in range(6)]
            draw.polygon(points, outline=(0, 0, 0))

    def draw_bezier_curves(self, draw, image_width, image_height, count):
        for _ in range(count):
            start = (random.randint(0, image_width),
                     random.randint(0, image_height))
            control1 = (random.randint(0, image_width),
                        random.randint(0, image_height))
            control2 = (random.randint(0, image_width),
                        random.randint(0, image_height))
            end = (random.randint(0, image_width),
                   random.randint(0, image_height))
            draw.line([start, control1, control2, end],
                      fill=(0, 0, 0), width=2)

    def get(self)->str:
        """
        生成验证码，并将文本存入session。

        该函数生成文本验证码，并将其渲染为图片形式，最后以Base64编码的PNG格式返回，
        同时将生成的文本验证码存入当前用户的session中。
        返回:
        - base64_image -- 返回验证码文本对应的Base64编码图片。
        """
        text = self.generate_random_text(self.length)
        session['captcha_text'] = text
        image = self.generate_captcha_image(
            text, self.font_sizes, self.image_width, self.image_height)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        base64_image = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{base64_image}"

    def validate_captcha(self, user_input)->bool:
        """
        验证用户输入的文本与session中存储的验证码是否一致。

        参数:
        - user_input -- 用户输入的验证码文本。

        返回:
        bool -- 如果用户输入的验证码与session中的验证码一致，返回True；否则返回False。
        """
        return user_input == session.get('captcha_text')
