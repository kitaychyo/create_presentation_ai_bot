import json
import textparsert
import os
import base64
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ai import AIConsultant, get_api_keys as get_ai_keys
from img_creater import FusionBrainAPI, get_api_keys as get_img_keys
from create_presentation import Create


# Telegram-обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать в бот для создания презентаций! Используйте /create, чтобы начать, указав тему. Используйте /help для получения справки."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Запустить бот\n"
        "/create - Создать презентацию, указав тему\n"
        "/help - Показать справку\n\n"
        "Пример: После /create введите тему, например, 'Искусственный интеллект в медицине'."
    )


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите тему для презентации (например, 'Искусственный интеллект в медицине').")
    context.user_data['awaiting_topic'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_topic'):
        topic = update.message.text
        context.user_data['awaiting_topic'] = False
        await update.message.reply_text(f"Создаю презентацию на тему: {topic}... Это может занять некоторое время.")

        # Загрузка конфигураций
        try:
            ai_keys = get_ai_keys("api.ini")
            img_keys = get_img_keys("img_api.ini")
        except Exception as e:
            await update.message.reply_text(f"Ошибка загрузки конфигурации: {str(e)}")
            return

        # Инициализация API
        consultant = AIConsultant(ai_keys['DeepSeek'])
        api = FusionBrainAPI('https://api-key.fusionbrain.ai/', img_keys['Fusion Brain']['key'],
                             img_keys['Fusion Brain']['secret_key'])
        pipeline_id = api.get_pipeline()

        promt = (f'Сгенерируй презентацию на тему "{topic}" в следующем формате:\n\n'
                 f'---\n'
                 f'**Title:** Заголовок слайда\n'
                 f'**Text:** Текст слайда в 2-3 предложения\n'
                 f'**Prompt img:** Описание картинки к слайду на английском\n'
                 f'---\n\n'
                 f'Повтори этот формат для каждого слайда. Сгенерируй не менее 5 слайдов. '
                 f'Убедись, что поле **Text** содержит текст слайда, а **Prompt img** — описание изображения.')
        # Генерация содержимого слайдов
        slides_content = []

        text = consultant.get_ai_response(promt)
        title, img_promt,text = textparsert.parser_response(text)
        print(title)
        print()
        print(img_promt)
        print()
        print(text)
        for i in range(len(img_promt)):
            # Генерация и сохранение изображения
            uuid = api.generate(img_promt[i], pipeline_id)
            files = api.check_generation(uuid)
            if files:
                image_base64 = files[0]
                image_data = base64.b64decode(image_base64)
                img_path = f"slide_{i + 1}.jpg"
                with open(img_path, "wb") as file:
                    file.write(image_data)
            else:
                img_path = "default.jpg"  # Запасное изображение
                print(f"Не удалось сгенерировать изображение для слайда {i + 1}.")

            slides_content.append({
                "title": title[i],
                "content": text[i],
                "image": img_path
            })


        print(slides_content)
        # Создание презентации
        try:
            with open("slides_content.json", "w", encoding="utf-8") as json_file:
                json.dump(slides_content, json_file, ensure_ascii=False, indent=4)
            print("slides_content сохранен в slides_content.json")
        except Exception as e:
            print(f"Ошибка сохранения slides_content: {str(e)}")
            await update.message.reply_text(f"Ошибка сохранения данных слайдов: {str(e)}")


        try:
            prs = Create()
            prs.create_prez(slides_content)
            with open("test.pptx", "rb") as file:
                await update.message.reply_document(document=file, filename="presentation.pptx")
            await update.message.reply_text("Презентация успешно создана и отправлена!")
        except Exception as e:
            await update.message.reply_text(f"Ошибка создания презентации: {str(e)}")
        finally:
            # Очистка временных файлов
            for slide in slides_content:
                if os.path.exists(slide["image"]) and slide["image"] != "default.jpg":
                    os.remove(slide["image"])
            if os.path.exists("test.pptx"):
                os.remove("test.pptx")


# Основная функция для запуска бота
def main():
    application = Application.builder().token("7347320832:AAEotxBYem5EF8FmDzKxM_TH6olmnF5h45g").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create", create))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()