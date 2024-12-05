import smtplib
from unittest.mock import MagicMock, Mock, patch

import pytest

from email_sender import EmailSender


class TestEmailSender:
    @pytest.fixture
    def sender(self):
        return EmailSender(
            smtp_server="smtp.test.com",
            smtp_port=587,
            username="test@test.com",
            password="password123",
        )

    def test_init(self):
        sender = EmailSender("smtp.gmail.com", 587, "user@gmail.com", "pass")
        assert sender.smtp_server == "smtp.gmail.com"
        assert sender.smtp_port == 587
        assert sender.username == "user@gmail.com"
        assert sender.password == "pass"

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp, sender):
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = sender.send_email(
            to_email="recipient@test.com", subject="Test Subject", body="Test Body"
        )

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "password123")
        mock_server.send_message.assert_called_once()

    def test_send_email_missing_parameters(self, sender):
        with pytest.raises(
            ValueError, match="to_email, subject, and body are required"
        ):
            sender.send_email("", "Subject", "Body")

        with pytest.raises(
            ValueError, match="to_email, subject, and body are required"
        ):
            sender.send_email("test@test.com", "", "Body")

        with pytest.raises(
            ValueError, match="to_email, subject, and body are required"
        ):
            sender.send_email("test@test.com", "Subject", "")

    def test_send_email_invalid_email_format(self, sender):
        with pytest.raises(ValueError, match="Invalid recipient email address"):
            sender.send_email("invalid-email", "Subject", "Body")

    @patch("smtplib.SMTP")
    def test_send_email_smtp_exception(self, mock_smtp, sender):
        mock_smtp.side_effect = smtplib.SMTPException("SMTP error")

        with pytest.raises(smtplib.SMTPException):
            sender.send_email("test@test.com", "Subject", "Body")

    @patch("smtplib.SMTP")
    def test_send_bulk_emails_success(self, mock_smtp, sender):
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        email_list = ["test1@test.com", "test2@test.com", "test3@test.com"]
        result = sender.send_bulk_emails(email_list, "Subject", "Body")

        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert len(result["errors"]) == 0

    @patch("smtplib.SMTP")
    def test_send_bulk_emails_partial_failure(self, mock_smtp, sender):
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Make the second email fail
        mock_server.send_message.side_effect = [
            None,
            smtplib.SMTPException("Failed"),
            None,
        ]

        email_list = ["test1@test.com", "test2@test.com", "test3@test.com"]
        result = sender.send_bulk_emails(email_list, "Subject", "Body")

        assert result["total"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    @patch("smtplib.SMTP")
    def test_test_connection_success(self, mock_smtp, sender):
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = sender.test_connection()

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "password123")

    @patch("smtplib.SMTP")
    def test_test_connection_failure(self, mock_smtp, sender):
        mock_smtp.side_effect = Exception("Connection failed")

        result = sender.test_connection()

        assert result is False

    def test_get_server_info(self, sender):
        info = sender.get_server_info()

        assert info["server"] == "smtp.test.com"
        assert info["port"] == 587
        assert info["username"] == "test@test.com"
        assert info["encryption"] == "TLS"
