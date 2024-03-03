# Импортируем необходимые модули: requests для отправки HTTP-запросов, BeautifulSoup для анализа HTML-кода, sqlite3 для работы с базой данных
import requests
from bs4 import BeautifulSoup
import sqlite3

# Создаем класс Database, который будет отвечать за хранение и обработку данных о сайтах
class Database:
    # Определяем конструктор класса, который принимает имя базы данных (по умолчанию 'websites.db') и создает соединение и курсор для работы с ней
    def __init__(self, db_name='websites.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    # Определяем метод create_table, который создает таблицу websites в базе данных, если она еще не существует
    # Таблица имеет два столбца: id (целочисленный первичный ключ) и url (текстовый)
    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS websites
                            (id INTEGER PRIMARY KEY, url TEXT)''')
        self.conn.commit()

    # Определяем метод add_website, который принимает url сайта и добавляет его в таблицу websites
    def add_website(self, url):
        self.cursor.execute("INSERT INTO websites (url) VALUES (?)", (url,))
        self.conn.commit()

    # Определяем метод get_websites, который возвращает все записи из таблицы websites в виде списка кортежей
    def get_websites(self):
        self.cursor.execute("SELECT * FROM websites")
        return self.cursor.fetchall()

    # Определяем метод clear_history, который удаляет все записи из таблицы websites и выводит сообщение об этом
    def clear_history(self):
        self.cursor.execute("DELETE FROM websites")
        self.conn.commit()
        print("История удалена.")

# Создаем класс WebsiteParser, который будет отвечать за анализ содержимого сайтов
class WebsiteParser:
    # Определяем конструктор класса, который принимает url сайта и сохраняет его в атрибуте self.url
    def __init__(self, url):
        self.url = url

    # Определяем метод parse, который отправляет GET-запрос по self.url, получает HTML-код сайта, создает объект BeautifulSoup из него и возвращает список всех тегов <p> на сайте
    def parse(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find_all("p")

# Создаем класс UserInterface, который будет отвечать за взаимодействие с пользователем
class UserInterface:
    # Определяем конструктор класса, который создает объект Database и сохраняет его в атрибуте self.db
    def __init__(self):
        self.db = Database()

    # Определяем метод run, который запускает бесконечный цикл, в котором предлагает пользователю выбрать одно из пяти действий:
    # 1. Добавить сайт
    # 2. Поиск информации
    # 3. Просмотр истории
    # 4. Удалить историю
    # 5. Выход
    def run(self):
        while True:
            choice = input("Выберите действие:\n1. Добавить сайт\n2. Поиск информации\n3. Просмотр истории\n4. Удалить историю\n5. Выход\n")
            # Если пользователь выбрал 1, то запрашиваем у него URL сайта и добавляем его в базу данных с помощью метода self.db.add_website
            if choice == '1':
                url = input("Введите URL сайта: ")
                self.db.add_website(url)
                print("Сайт добавлен.")
            # Если пользователь выбрал 2, то запрашиваем у него ключевое слово для поиска и получаем список всех сайтов из базы данных с помощью метода self.db.get_websites
            elif choice == '2':
                keyword = input("Введите ключевое слово для поиска: ")
                websites = self.db.get_websites()
                # Для каждого сайта в списке создаем объект WebsiteParser и получаем список всех параграфов на сайте с помощью метода parse
                for website in websites:
                    parser = WebsiteParser(website[1])
                    paragraphs = parser.parse()
                    # Инициализируем счетчик найденных параграфов с ключевым словом
                    count = 0
                    # Для каждого параграфа в списке проверяем, содержит ли он ключевое слово в тексте
                    for paragraph in paragraphs:
                        if keyword in paragraph.get_text():
                            # Если содержит, то выводим сообщение с URL сайта и текстом параграфа
                            print(f"На сайте {website[1]} найдено '{keyword}' в параграфе:")
                            print(paragraph.get_text())
                            # Увеличиваем счетчик на единицу
                            count += 1
                            # Если счетчик достиг трех, то прерываем цикл по параграфам
                            if count == 3:
                                break
                    # Если счетчик достиг трех, то прерываем цикл по сайтам
                    if count == 3:
                        break
            # Если пользователь выбрал 3, то получаем список всех сайтов из базы данных с помощью метода self.db.get_websites
            elif choice == '3':
                history = self.db.get_websites()
                # Если список пуст, то выводим сообщение об этом
                if not history:
                    print("История пуста.")
                # Иначе выводим список всех сайтов с номерами
                else:
                    print("История запросов:")
                    for i, website in enumerate(history, 1):
                        print(f"{i}. {website[1]}")
                    # Запрашиваем у пользователя номер запроса для просмотра деталей (или 0 для возврата)
                    choice_history = input("Введите номер запроса для просмотра деталей (или '0' для возврата): ")
                    # Если введенный номер корректен и находится в диапазоне от 0 до длины списка
                    if choice_history.isdigit() and 0 <= int(choice_history) <= len(history):
                        # Если номер равен 0, то продолжаем цикл
                        if int(choice_history) == 0:
                            continue
                        # Иначе получаем выбранный сайт из списка по индексу
                        selected_website = history[int(choice_history) - 1]
                        # Создаем объект WebsiteParser и получаем список всех параграфов на сайте с помощью метода parse
                        parser = WebsiteParser(selected_website[1])
                        paragraphs = parser.parse()
                        # Выводим текст всех параграфов на сайте
                        for paragraph in paragraphs:
                            print(paragraph.get_text())
                    # Если введенный номер некорректен, то выводим сообщение об ошибке
                    else:
                        print("Неверный ввод.")
            # Если пользователь выбрал 4, то удаляем все записи из базы данных с помощью метода self.db.clear_history и выводим сообщение об этом
            elif choice == '4':
                self.db.clear_history()
                print("История удалена.")
            # Если пользователь выбрал 5, то выводим сообщение о завершении программы и прерываем цикл
            elif choice == '5':
                print("Программа завершена.")
                break
            # Если пользователь выбрал что-то другое, то выводим сообщение о неверном вводе и повторяем цикл
            else:
                print("Неверный ввод. Попробуйте еще раз.")

# Если этот файл запускается как основная программа, то создаем объект UserInterface и вызываем его метод run
if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
