import mysql.connector
from mysql.connector import Error
from PyQt5.QtCore import QObject, pyqtSignal

class DatabaseManager(QObject):
    prompt_added = pyqtSignal()
    
    def __init__(self, host, user, password, database):
        super().__init__()
        self.connection = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database

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
                source_prompt_id INT NOT NULL,
                target_prompt_id INT NOT NULL,
                relation_type_id INT NOT NULL,
                FOREIGN KEY (source_prompt_id) REFERENCES prompts(id),
                FOREIGN KEY (target_prompt_id) REFERENCES prompts(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relation_types (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                hierarchy_level INT NOT NULL DEFAULT 0,
                description TEXT
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

    def create_prompt(self, content, tag, source_id):
        try:
            connection = self.connect()
            cursor = connection.cursor()

            local_id = self.get_next_local_id(source_id)

            cursor.execute('''
                INSERT INTO prompts (content, tag, source_id, local_id)
                VALUES (%s, %s, %s, %s)
            ''', (content, tag, source_id, local_id))

            prompt_id = cursor.lastrowid

            connection.commit()

            cursor.close()
            connection.close()

            self.prompt_added.emit()

            return prompt_id
        
        except mysql.connector.Error as err:
            print(f"[DB] Fehler beim Erstellen des Prompts: {err}")

    def add_prompt_relation(self, prompt_a_id, prompt_b_id, relation_type_id):
        connection = self.connect()
        cursor = connection.cursor()


        print("IDS: ", prompt_a_id, prompt_b_id, relation_type_id)
        cursor.execute('''
            SELECT id, hierarchy_level
            FROM relation_types
            WHERE id = %s
        ''', (relation_type_id,))
        print("Beziehungstyp wurde ausgewählt: ", relation_type_id)
        result = cursor.fetchone()

        if not result:
            cursor.close()
            connection.close()

            raise ValueError(f"Relation type '{relation_type_id}' not found in the database.")
        
        relation_type_id, hierarchy_level = result
        print("Ergebnis: ", result)

        if hierarchy_level == 1:
            print("Hierarchie-Level 1: ", prompt_a_id, prompt_b_id)
            source_id, target_id = prompt_a_id, prompt_b_id
        else:
            print("Hierarchie-Level 2: ", prompt_a_id, prompt_b_id)
            source_id, target_id = sorted((prompt_b_id, prompt_a_id))
        cursor.execute('''
            INSERT INTO prompts_relations (source_prompt_id, target_prompt_id, relation_type_id)
            VALUES (%s, %s, %s)
        ''', (source_id, target_id, relation_type_id))

        connection.commit()
        print("Beziehung wurde in Datenbank eingetragen.")
        cursor.close()
        connection.close()

    def get_prompt_relations(self, prompt_id, direction='both'):
        query = '''
            SELECT source_prompt_id, target_prompt_id, relation_type, hierarchy_level
            FROM prompts_relations
            WHERE {condition}
        '''

        if direction == 'source':
            condition = 'source_prompt_id = %s'
            params = (prompt_id,)
        elif direction == 'target':
            condition = 'target_prompt_id = %s'
            params = (prompt_id,)
        else:
            condition = 'source_prompt_id = %s OR target_prompt_id = %s'
            params = (prompt_id, prompt_id)
        
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(query.format(condition=condition), params)
        relations = cursor.fetchall()

        cursor.close()
        connection.close()

        return relations

    def get_all_prompts(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT id, content, tag, source_id, local_id, created_at FROM prompts ORDER BY source_id DESC")
        prompts = cursor.fetchall()

        cursor.close()
        connection.close()

        return prompts
    
    def get_next_local_id(self, source_id):
        result = self.fetchone(
            "SELECT MAX(local_id) FROM prompts WHERE source_id = %s",
            (source_id,)         
        )
        return result[0] + 1 if result[0] is not None else 1

    def add_relation_type(self, name, description, hierarchy_level):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO relation_types (name, description, hierarchy_level)
            VALUES (%s, %s, %s)
        ''', (name, description, hierarchy_level))
        connection.commit()

        cursor.close()
        connection.close()

    def get_relation_types(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM relation_types''')

        relation_types = cursor.fetchall()

        row = [{'id': r[0], 'name': r[1], 'description': r[2], 'hierarchy_level': r[3]} for r in relation_types]

        cursor.close()
        connection.close()

        return row

    def fetchone(self, query, params=None):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(query, params or ())
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result
