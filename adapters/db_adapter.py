import sqlite3
import os
from application.ports import RepositoryPort
from dotenv import load_dotenv

class DbAdapter(RepositoryPort):
    def get_all_messages(self) -> list[str]:
        load_dotenv()
        db_path = os.getenv('Messages_DB_PATH')
        connection = sqlite3.connect(db_path)

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT Content FROM Messages")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception:
            return []
        finally:
            connection.close()

    def save_message(self, message: str) -> bool:
        load_dotenv()
        db_path = os.getenv('Messages_DB_PATH')
        connection = sqlite3.connect(db_path)

        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Messages (Content) VALUES (?)", (message,))
            connection.commit()
            return True
        except Exception:
            return False
        finally:
            connection.close()