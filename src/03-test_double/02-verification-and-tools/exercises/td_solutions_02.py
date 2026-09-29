from unittest.mock import Mock

from mock_tools import AlertService


def send_with_mock(message: str) -> tuple[str, Mock]:
    sender = Mock(spec=["send"])
    sender.send.return_value = "accepted"
    result = AlertService(sender).alert(message)
    return result, sender
