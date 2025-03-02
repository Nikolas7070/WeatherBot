import requests
import telebot
import os
import cods


class WeatherBot:
    __api_key = cods.api_key  # Напишите ваш ключ
    __telegram_token = cods.telegram_token  # Напишите ваш токен
    __user_file = "users.txt"

    def __init__(self):
        self.__bot = telebot.TeleBot(self.__telegram_token)
        self.__setup_handlers()

    def __save_user(self, user_id, username):
        if not os.path.exists(self.__user_file):
            open(self.__user_file, "w").close()

        with open(self.__user_file, "r") as file:
            users = file.readlines()

        user_info = f"{user_id} {username}\n"

        if user_info not in users:
            with open(self.__user_file, "a") as file:
                file.write(user_info)

    def __get_weather(self, city: str, forecast: bool = False):
        url_type = "forecast" if forecast else "weather"
        url = f"https://api.openweathermap.org/data/2.5/{url_type}?q={city}&appid={self.__api_key}&units=metric&lang=uk"

        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    def __setup_handlers(self):

        @self.__bot.message_handler(commands=["start", "help"])
        def start(message):
            self.__save_user(message.from_user.id, message.from_user.first_name)
            self.__bot.send_message(
                message.chat.id,
                "Привіт! Я бот прогнозу погоди. Надішліть мені назву міста, і я повідомлю, яка там зараз погода.\n"
                "Також можна використати команду /forecast, щоб дізнатися прогноз на 5 днів."
            )

        @self.__bot.message_handler(commands=["forecast"])
        def forecast(message):
            self.__save_user(message.from_user.id, message.from_user.first_name)
            msg = self.__bot.send_message(message.chat.id, "Введіть назву міста для прогнозу на 5 днів: ")
            self.__bot.register_next_step_handler(msg, send_forecast)

        def send_forecast(message):
            city = message.text.strip()
            data = self.__get_weather(city, forecast=True)

            if data:
                forecast_msg = f"🌤 Прогноз погоди для {city} на 5 днів:\n"
                for entry in data["list"][::8]:
                    date = entry["dt_txt"].split()[0]
                    temp = round(entry["main"]["temp"], 1)
                    desc = entry["weather"][0]["description"].capitalize()
                    wind = entry["wind"]["speed"]
                    forecast_msg += f"\n📅 {date}:\n🌡 Температура: {temp}°C\n☁ {desc}\n💨 Вітер: {wind} м/с\n"

                self.__bot.send_message(message.chat.id, forecast_msg)
            else:
                self.__bot.send_message(message.chat.id, "Помилка! Місто не знайдено. Спробуйте ще раз.")

        @self.__bot.message_handler(content_types=["text"])
        def send_weather(message):
            self.__save_user(message.from_user.id, message.from_user.first_name)
            city = message.text.strip()
            data = self.__get_weather(city)

            if data:
                name = data["name"]
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"].capitalize()
                wind = data["wind"]["speed"]

                response_text = (
                    f"🌍 Погода в {name}:\n"
                    f"🌡 Температура: {temp}°C\n"
                    f"☁ {desc}\n"
                    f"💨 Вітер: {wind} м/с"
                )
                self.__bot.send_message(message.chat.id, response_text)
            else:
                self.__bot.send_message(message.chat.id, "Помилка! Місто не знайдено. Спробуйте ще раз.")

    def run(self):
        self.__bot.polling(none_stop=True)


if __name__ == "__main__":
    bot_instance = WeatherBot()
    bot_instance.run()
