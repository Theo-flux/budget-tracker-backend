auth_prefix = "/api/v1/auth"


class TestAuthService:
    def test_create_user(self, fake_user_service, fake_session, test_client):
        json = {
            "first_name": "string",
            "last_name": "string",
            "email": "user@example.com",
            "phone_number": "string",
            "password": "string",
        }
        test_client.post(
            url=f"{auth_prefix}/register",
            json=json,
        )

        assert fake_user_service.get_user_by_email_called_once()
        assert fake_user_service.get_user_by_phone_called_once()
