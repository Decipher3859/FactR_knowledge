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
        connection = self.connect(include_database=False)
        if not connection:
            return
        
        cursor = connection.cursor()

        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
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
                tag VARCHAR(50) NULL,
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
                relation_type_id INT NOT NULL,
                FOREIGN KEY (parent_id) REFERENCES prompts(id),
                FOREIGN KEY (child_id) REFERENCES prompts(id),
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

    def ensure_default_relation_types(self):
        default_types = [
            ["Argument", 1],
            ["Gegenargument", 1],
            ["Indiz", 1],
            ["Frage", 1],
            ["Antwort", 1],
            ["Folge", 1]
        ]

        connection = self.connect()
        cursor = connection.cursor()

        for name, id in default_types:
            cursor.execute('''
                SELECT id FROM relation_types WHERE name = %s
            ''', (name,))
            exists = cursor.fetchone()

            if not exists:
                cursor.execute('''
                    INSERT INTO relation_types (name, hierarchy_level)
                    VALUES (%s, %s)
                ''', (name, id))
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

    def create_prompt(self, content, source_id):
        print("CREATE_PROMPT IN DB MANAGER")
        try:
            connection = self.connect()
            cursor = connection.cursor()

            local_id = self.get_next_local_id(source_id)

            cursor.execute('''
                INSERT INTO prompts (content, source_id, local_id)
                VALUES (%s, %s, %s)
            ''', (content, source_id, local_id))

            prompt_id = cursor.lastrowid
            print("LASTROWID: ", prompt_id)
            connection.commit()

            cursor.close()
            connection.close()

            return prompt_id
        
        except mysql.connector.Error as err:
            print(f"[DB] Fehler beim Erstellen des Prompts: {err}")

    def add_prompt_relation(self, prompt_a_id, prompt_b_id, relation_type_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id, hierarchy_level
            FROM relation_types
            WHERE id = %s
        ''', (relation_type_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            connection.close()

            raise ValueError(f"Relation type '{relation_type_id}' not found in the database.")
        
        relation_type_id, hierarchy_level = result

        if hierarchy_level == 1:
            source_id, target_id = prompt_a_id, prompt_b_id
        else:
            source_id, target_id = sorted((prompt_b_id, prompt_a_id))
        cursor.execute('''
            INSERT INTO prompts_relations (parent_id, child_id, relation_type_id)
            VALUES (%s, %s, %s)
        ''', (source_id, target_id, relation_type_id))

        connection.commit()
        cursor.close()
        connection.close()

    def get_prompt_relations(self, prompt_id, direction='both'):
        query = '''
            SELECT parent_id, child_id, relation_type, hierarchy_level
            FROM prompts_relations
            WHERE {condition}
        '''

        if direction == 'parent':
            condition = 'parent_id = %s'
            params = (prompt_id,)
        elif direction == 'child':
            condition = 'child_id = %s'
            params = (prompt_id,)
        else:
            condition = 'parent_id = %s OR child_id = %s'
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
    
    def get_root_prompts(self):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
            SELECT * FROM prompts
            WHERE id NOT IN (
                SELECT child_id
                FROM prompts_relations
                JOIN relation_types ON prompts_relations.relation_type_id = relation_types.id
                WHERE relation_types.hierarchy_level = 1
            )
        ''')

        prompts = cursor.fetchall()
        cursor.close()
        connection.close()

        return prompts

    def get_prompt_tree(self, root_ids=None, visited=None):
        if visited is None:
            visited = set()
        if root_ids is None:
            root_prompts = self.get_top_level_prompts()
            root_ids = [prompt['id'] for prompt in root_prompts]
        
        tree = []
        for prompt_id in root_ids:
            if prompt_id in visited:
                continue
            visited.add(prompt_id)

            prompt = self.get_prompt_by_id(prompt_id)
            children = self.get_direct_children(prompt_id)
            subtree = self.get_prompt_tree(children, visited)
            tree.append({'prompt': prompt, 'children': subtree})
    
        return tree

    def get_direct_children(self, parent_id):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = '''
            SELECT p.*,
                   t.name AS relation_name 
            FROM prompts_relations r
            JOIN prompts p ON p.id = r.child_id
            JOIN relation_types t ON r.relation_type_id = t.id
            WHERE r.parent_id = %s
            AND t.hierarchy_level = 1
        '''
        cursor.execute(query, (parent_id,))
        results = cursor.fetchall()

        cursor.close()
        connection.close()
        print("Query: ", results)
        return results
    
    def get_prompt_by_id(self, prompt_id):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('SELECT * FROM prompts WHERE id = %s', (prompt_id,))
        prompt = cursor.fetchone()

        cursor.close()
        connection.close()

        return prompt
    
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
