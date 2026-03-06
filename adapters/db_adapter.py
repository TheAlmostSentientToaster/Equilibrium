import sqlite3

from application.ports import RepositoryPort
from Domain.Message import Message
from config import Config

class DbAdapter(RepositoryPort):
    def _execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        try:
            with sqlite3.connect(Config.MESSAGES_DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return [] if fetch else False

    def get_all_messages(self) -> list[Message]:
        rows = self._execute_query("SELECT ID, Content, User FROM Messages")
        return [Message(id=row[0], content=row[1], user=row[2]) for row in rows]

    def save_message(self, message: Message) -> bool:
        return self._execute_query(
            "INSERT INTO Messages (Content, User) VALUES (?,?)",
            (message.content, message.user),
            fetch=False
        )