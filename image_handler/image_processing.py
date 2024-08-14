import io

from PIL import Image, ImageDraw, ImageFont


def add_text_to_image(image: bytes, text: str, font_size: int) -> bytes:
    # Открываем изображение
    image = Image.open(io.BytesIO(image))
    image_width, image_height = image.size

    # Настраиваем шрифт (DejaVuSans поддерживает кириллицу и встроен в PIL)
    font = ImageFont.truetype('Arial.ttf', font_size)

    # Создаем объект для рисования
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
    # text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Определяем высоту черного фона
    padding = 10
    new_image_height = image_height + text_height + 2 * padding

    # Создаем новое изображение с дополнительным черным фоном
    new_image = Image.new('RGB', (image_width, new_image_height), color=(0, 0, 0))
    # Вставляем исходное изображение в верхнюю часть нового изображения
    new_image.paste(image, (0, 0))

    # Рисуем текст внизу на черном фоне
    draw = ImageDraw.Draw(new_image)
    text_x = padding
    text_y = image_height
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    new_image.save('output.jpg')
    return new_image.tobytes()
