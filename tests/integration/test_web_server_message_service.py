from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from web_server import WebServer
from adapters.mobile_app_adapters import MobileAppInboundAdapter
from domain.chat_context import ChatContext


class TestWebServerMessageService:
    def setup_method(self):
        self.mock_message_service = AsyncMock()

        self.mock_photo_service = MagicMock()
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

    def test_receive_message_calls_message_service_correctly(self):
        # Arrange
        message_data = {
            "content": "Hello, world!",
            "user_id": 12345,
            "user_name": "test_user",
            "chat_id": 67890
        }

        # Act
        response = self.client.post("/message", json=message_data)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Message received"}

        self.mock_message_service.assert_called_once_with(
            content="Hello, world!",
            user_id=12345,
            user_name="test_user",
            chat_context=ChatContext(67890)
        )

    def test_receive_message_invalid_request(self):
        # Arrange
        invalid_data = {
            "content": "Incomplete message"
        }

        # Act
        response = self.client.post("/message", json=invalid_data)

        # Assert
        assert response.status_code == 422

        self.mock_message_service.assert_not_called()