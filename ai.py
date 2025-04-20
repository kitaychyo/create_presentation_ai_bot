from openai import OpenAI
import configparser
import sys
def get_api_keys(config_file):

    config = configparser.ConfigParser()
    config.read(config_file)
    print(config)

    result = {}
    for service in config.sections():
        result[service] = {
            'key': config[service]['Api_key'],
            'url': config[service]['Url'],
            'model': config[service]['model']
        }
    return result

class AIConsultant:
    def __init__(self, conf):
        self.conf = conf
        self.client = OpenAI(
            api_key= self.conf['key'],
            base_url=self.conf['url']
        )

    def get_ai_response(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model= self.conf['model'],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка: {str(e)}"

def main():
    print("=== Консультант пользователя (ИИ-помощник) ===")
    print("Для выхода введите 'exit' или 'quit'\n")

    # Чтение файла конфигурации

    res = get_api_keys("api.ini")
    flag = input('1 - Google  or 2 - deepseek ')

    if flag == 1:
        consultant = AIConsultant(res['Google Gemini'])
    else: consultant = AIConsultant(res['DeepSeek'])

    while True:
        user_input = input("Вы: ")

        if user_input.lower() in ('exit', 'quit'):
            print("До свидания!")
            break

        response = consultant.get_ai_response(user_input)
        print("\nКонсультант:", response, "\n")


if __name__ == "__main__":
    main()