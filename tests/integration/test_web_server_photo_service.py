from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import base64

from web_server import WebServer
from adapters.mobile_app_adapters import MobileAppInboundAdapter
from domain.chat_context import ChatContext


class TestWebServerPhotoService:
    def setup_method(self):
        self.mock_photo_service = AsyncMock()

        self.mock_message_service = MagicMock()
        self.mock_command_service = MagicMock()
        self.mock_user_verification_service = MagicMock()

        self.mobile_inbound_adapter = MobileAppInboundAdapter(
            message_service=self.mock_message_service,
            photo_service=self.mock_photo_service,
            command_service=self.mock_command_service,
            user_verification_service=self.mock_user_verification_service
        )

        self.web_server = WebServer(self.mobile_inbound_adapter)
        self.client = TestClient(self.web_server.app)

    def test_receive_photo_calls_photo_service_correctly(self):
        # Arrange
        test_image_bytes = b"test_image_data"
        test_image_base64 = base64.b64encode(test_image_bytes).decode('utf-8')
        
        photo_data = {
            "photo_data": test_image_base64,
            "user_id": 12345,
            "user_name": "test_user",
            "chat_id": 67890
        }

        # Act
        response = self.client.post("/photo", json=photo_data)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Photo received"}

        self.mock_photo_service.receive_photo.assert_called_once_with(
            photo=bytearray(test_image_bytes),
            user_id=12345,
            user_name="test_user",
            chat_context=ChatContext(chat_id=67890)
        )

    def test_receive_photo_invalid_request(self):
        # Arrange
        invalid_data = {
            "photo_data": "invalid_base64_data",
            "user_id": 12345
        }

        # Act
        response = self.client.post("/photo", json=invalid_data)

        # Assert
        assert response.status_code == 422

        self.mock_photo_service.assert_not_called()

    def test_receive_photo_with_empty_image(self):
        # Arrange
        empty_image_base64 = base64.b64encode(b"").decode('utf-8')
        
        photo_data = {
            "photo_data": empty_image_base64,
            "user_id": 12345,
            "user_name": "test_user",
            "chat_id": 67890
        }

        # Act
        response = self.client.post("/photo", json=photo_data)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Photo received"}

        self.mock_photo_service.receive_photo.assert_called_once_with(
            photo=bytearray(b""),
            user_id=12345,
            user_name="test_user",
            chat_context=ChatContext(chat_id=67890)
        )

    def test_receive_photo_with_invalid_base64(self):
        # Arrange
        photo_data = {
            "photo_data": "this_is_nöt_välid_bäse64!!!",
            "user_id": 12345,
            "user_name": "test_user",
            "chat_id": 67890
        }

        # Act
        response = self.client.post("/photo", json=photo_data)

        # Assert
        assert response.status_code == 400  # Base64 decoding error

        self.mock_photo_service.assert_not_called()
