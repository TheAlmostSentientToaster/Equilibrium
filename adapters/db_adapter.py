import sqlite3
import os
from sys import exception

from application.ports import RepositoryPort
from dotenv import load_dotenv
from Domain.Message import Message

class DbAdapter(RepositoryPort):
    def get_all_messages(self) -> list[Message]:
        load_dotenv()
        db_path = os.getenv('Messages_DB_PATH')
        connection = sqlite3.connect(db_path)

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT ID, Content, User FROM Messages")
            rows = cursor.fetchall()
            messages = []

            for row in rows:
                message = Message(id= row[0], content= row[1], user=row[2])
                messages.append(message)

            return messages
        except Exception:
            return []
        finally:
            connection.close()

    def save_message(self, message: Message) -> bool:
        load_dotenv()
        db_path = os.getenv('Messages_DB_PATH')
        connection = sqlite3.connect(db_path)

        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO Messages (Content, User) VALUES (?,?)", (message.content, message.user))
            connection.commit()
            return True
        except Exception:
            return False
        finally:
            connection.close()