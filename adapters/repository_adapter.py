import sqlite3
import io
import os
from typing import Optional

from PIL import Image
from datetime import datetime

from domain.command import Command
from domain.photo import Photo
from application.ports import RepositoryPort
from domain.message import Message
from config import Config

class DbAdapter(RepositoryPort):
    def __init__(self, images_path: str):
        self.images_storage_path = images_path

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = True, return_last_row_id: bool = False):
        try:
            with sqlite3.connect(Config.MESSAGES_DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                elif return_last_row_id:
                    connection.commit()
                    return cursor.lastrowid
                else:
                    connection.commit()
                    return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return [] if fetch else False

    def get_all_messages(self) -> list[Message]:
        rows = self._execute_query("SELECT ID, Content, User_id FROM Messages")
        return [Message(message_id=row[0], content=row[1], user_id=row[2], user_name=None) for row in rows]

    def save_message(self, message: Message) -> bool:
        self.save_user(message.user_id, message.user_name)

        if self._execute_query(
                "INSERT INTO Messages (Content, User_id) VALUES (?,?)",
                (message.content, message.user_id),
                fetch=False
            ):
            return True
        else:
            return False

    def save_user(self, user_id: int, user_name: str) -> bool:
        count = self._execute_query("SELECT COUNT(*) FROM Users WHERE User_id = ?",
                                    (user_id,),
                                    fetch=True)

        if not count or count[0][0] == 0:
            if self._execute_query(
                "INSERT INTO Users (User_id, User_name) VALUES (?,?)",
                (user_id, user_name),
                fetch=False
            ):
                return True
            else:
                return False
        return True

    def save_photo(self, photo: Photo) -> Optional[int]:
        self.save_user(photo.user_id, photo.user_name)

        path = self.save_photo_on_disk(photo)
        if path is not None:
            payment_id = self._execute_query(
            "INSERT INTO Payments (User_id, Image_path, Sum) VALUES (?,?,?)",
            (photo.user_id, path, photo.sum,),
            fetch=False,
            return_last_row_id=True
            )
            return payment_id
        else:
            return None

    def save_photo_on_disk(self, photo: Photo) -> Optional[str]:
        try:
            image_stream = io.BytesIO(photo.photo)
            image = Image.open(image_stream)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"{self.images_storage_path}user_{photo.user_id}_{timestamp}.png"

            os.makedirs(self.images_storage_path, exist_ok=True)
            image.save(image_path)
            print(f"Image saved successfully: {image_path}")
            return image_path
        except Exception as e:
            print(f"Error while saving image: {e}")
            return None

    def get_sums_of_deposits(self) -> list:
        query = """
            SELECT u.User_id, u.User_name, COALESCE(SUM(i.Sum), 0) AS TotalSum 
            FROM Users u 
            LEFT JOIN Payments i ON u.User_id = i.User_id 
            GROUP BY u.User_id, u.User_name 
            ORDER BY u.User_id
        """
        results = self._execute_query(query, params=(), fetch=True)
        deposits = list()

        for result in results:
            deposits.append((result[1], result[2]))
        return deposits

    def delete_payment(self, command: Command) -> bool:
        content_split = command.content.split()
        payment_id = content_split[0][1:]

        if len(content_split) > 1:
            comment = "User comment: " + " ".join(content_split[1:]) + "\n"
        else:
            comment = ""

        payment = self._execute_query("""
            SELECT Sum
            From Payments
            Where Payment_id = (?)
            """,
            (payment_id,)
        )

        error_message = self._execute_query("""
            SELECT Error
            FROM Payments
            WHERE Payment_id = (?)
            """,
            (payment_id,)
        )

        if error_message[0][0] is None:
            error_message = [("",)]

        error_message = error_message[0][0] + f" Payment deleted by User: {payment[0][0]}€\n{comment}"

        if payment[0][0] is None:
            print("No payment returned.")
            return False
        elif payment[0][0] == "":
            print("Payment already empty.")
            return False
        else:
            if self._execute_query("""
                        UPDATE Payments
                        SET Error = ?, Sum = NULL
                        Where Payment_id = (?)
                        """,
                        (error_message, payment_id),
                        fetch=False, return_last_row_id=False
                                ):
                return True
            else:
                return False

    def add_payment(self, command: Command) -> Optional[int]:
        command_parts = command.content.split()

        try:
            amount = float(command_parts[1])
        except ValueError as e:
            print(f"Value error: {e}")
            return None

        if len(command_parts) > 2:
            comment = " ".join(command_parts[2:]) + "\n"
        else:
            comment = "No comment by User.\n"

        payment_id = self._execute_query(
            "INSERT INTO Payments (User_id, Sum, Error) VALUES (?,?,?)",
            (command.user_id, amount, "Payment added manually by user: " + comment),
            fetch=False,
            return_last_row_id=True
        )
        return payment_id

    def change_payment(self, command: Command) -> bool:
        content_split = command.content.split()
        payment_id = content_split[0][1:]
        amount = content_split[1]

        try:
            amount = float(amount)
        except ValueError as e:
            print(f"Value error: {e}")
            return False

        if len(content_split) > 2:
            comment = " ".join(content_split[2:]) + "\n"
        else:
            comment = "No comment by User.\n"
            
        error = self._execute_query("""
            SELECT Error
            FROM Payments
            WHERE Payment_id = ?
            """,
                                    (payment_id,),
            fetch=True, return_last_row_id=False)

        if error[0][0] is None:
            error = [[""]]

        if self._execute_query("""
                        UPDATE Payments
                        SET Sum = ?, Error = ?
                        WHERE Payment_id = ?
                        """,
            (amount, error[0][0] + "Payment changed by user: " + comment, payment_id),
            fetch=False,
            return_last_row_id=False
        ):
            return True
        else:
            return False