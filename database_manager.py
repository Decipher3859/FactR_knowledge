import mysql.connector
from mysql.connector import Error
from PyQt5.QtCore import pyqtSignal

class DatabaseManager:
    def __init__(self, host, user, password, database):
        print("DBManager wird initialisiert.")
        self.connection = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.prompt_added = pyqtSignal()

    def create_database(self):
        print("DBManager.crete_database() wird aufgerufen.")
        connection = self.connect(include_database=False)
        if not connection:
            print("[DB] Verbindung fehlgeschlagen -keine DB erstellt.")
            return
        
        cursor = connection.cursor()

        print("CREATE DATABASE: ", self.database)
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"[DB] Datenbank wurde erstellt oder exisiterte bereits.")
        except mysql.connector.Error as err:
            print(f"[DB] Fehler beim Erstellen der DB: {err}")
        finally:
            cursor.close()
            connection.close()

    def connect(self, include_database=True):
        print("connect() wird aufgerufen.")
        try:
            config = {
                "host": self.host,
                "user": self.user,
                "password": self.password
            }
            if include_database:
                config["database"] = self.database
            print(f"[DB] Verbindungsdaten: {config}")    
            connection = mysql.connector.connect(**config)
            print("[DB] Verbindung erfolgreich")
            return connection
        except mysql.connector.Error as err:
            print(f"[DB] Fehler beim Verbinden: {err}")
            return None
        
    def get_connection(self):
        return self.connection

    def create_tables(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources(
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            title VARCHAR(255),
            author VARCHAR(255),
            origin VARCHAR(255),
            type VARCHAR(255),
            date DATE,
            note TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content TEXT NOT NULL,
                tag VARCHAR(50) NOT NULL,
                source_id INT,
                local_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts_relations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                parent_id INT NOT NULL,
                child_id INT NOT NULL,
                relation_type VARCHAR(50) NOT NULL
            )
        ''')

        connection.commit()

        cursor.close()
        connection.close()

    def add_source(self, file_name, title='', author='Unbekannt', date=None, note=''):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO sources(filename, title, author, date, note)
            VALUES (%s, %s, %s, %s, %s)
        ''', (file_name, title, author, date, note))
        connection.commit()

        cursor.close()
        connection.close()
    
    def get_all_sources(self):
        try:
            connection = self.connect()
            cursor = connection.cursor()

            cursor.execute("SELECT id, filename, title, author, date, note FROM sources")
            sources = cursor.fetchall()

            cursor.close()
            connection.close()

            return sources
        except mysql.connector.Error as err:
            print(f"[DB] Fehler beim Abrufen der Quellen: {err}")
            return []

    def create_prompt(self, content, tag, source_id, local_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO prompts (content, tag, source_id, local_id)
            VALUES (%s, %s, %s, %s)
        ''', (content, tag, source_id, local_id))
        connection.commit()

        cursor.close()
        connection.close()

        self.prompt_added.emit()

    def get_all_prompts(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT id, content, tag, source_id, local_id, created_at FROM prompts ORDER BY source_id DESC")
        prompts = cursor.fetchall()

        cursor.close()
        connection.close()

        return prompts

    def create_relation(self, parent_id, child_id, relation_type):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO prompts_relations (parent_id, child_id, relation_type)
            VALUES (%s, %s, %s)
        ''')
        connection.commit()

        cursor.close()
        connection.close()
