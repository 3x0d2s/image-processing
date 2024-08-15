import io

from PIL import Image, ImageDraw, ImageFont


def add_text_to_image(image: bytes, text: str, font_name: str, font_size: int) -> bytes:
    image = Image.open(io.BytesIO(image))
    image_width, image_height = image.size

    font = ImageFont.truetype(f"src/fonts/{font_name}", font_size)

    dummy_draw = ImageDraw.Draw(image)
    # Разбиваем текст на строки, чтобы он помещался в заданную ширину
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        # Проверяем, помещается ли слово в текущей строке
        temp_line = current_line + word + " "
        #
        temp_line_textbox = dummy_draw.textbbox((0, 0), temp_line, font=font)
        temp_line_width = temp_line_textbox[2] - temp_line_textbox[0]
        #
        if temp_line_width <= image_width - 20:
            current_line = temp_line
        else:
            lines.append(current_line)
            current_line = word + " "
    # Добавляем последнюю строку
    if current_line:
        lines.append(current_line)
    text = '\n'.join(lines)

    # Определяем размеры текста
    text_bbox = dummy_draw.multiline_textbbox((0, 0), text, font=font)
    text_height = text_bbox[3] - text_bbox[1]

    # Определяем высоту черного фона
    padding = 10
    new_image_height = image_height + text_height + 2 * padding

    # Создаем новое изображение с дополнительным черным фоном
    new_image = Image.new('RGB', (image_width, new_image_height), color=(0, 0, 0))
    new_image.paste(image, (0, 0))

    # Рисуем текст внизу на черном фоне
    draw = ImageDraw.Draw(new_image)
    text_x = padding
    text_y = image_height
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    output = io.BytesIO()
    new_image.save(output, 'JPEG')
    output.seek(0)
    return output.read()
