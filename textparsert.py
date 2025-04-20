import re

def parser_response(data):
    # Инициализируем списки
    titles = []
    texts = []
    promt_imgs = []

    # Разделяем данные на блоки по разделителю ---
    blocks = data.strip().split('---')

    for block in blocks:
        # Убираем пустые строки и пробелы
        block = block.strip()
        if not block:
            continue

        # Разделяем блок на строки
        lines = block.split('\n')
        title = ''
        text = ''
        promt_img = ''

        for line in lines:
            line = line.strip()
            # Проверяем строку с заголовком
            if line.startswith('**Title:'):
                title = line.replace('**Title:', '').replace('**', '').strip()
            # Проверяем строку с текстом
            elif line.startswith('**Text:'):
                text = line.replace('**Text:', '').replace('**', '').strip()
            # Проверяем строку с промптом изображения
            elif line.startswith('**Prompt img:'):
                promt_img = line.replace('**Prompt img:', '').replace('**', '').strip()

        # Добавляем данные в списки, если они найдены
        if title:
            titles.append(title)
        if text:
            texts.append(text)
        if promt_img:
            promt_imgs.append(promt_img)

    return titles, promt_imgs, texts

