from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError

client = TestClient(app)

# ======================================================
#                  TEST POST /user
# ======================================================
def test_create_user_success():
    user_data = {
        "username": "operador_test",
        "role": "operador",
        "password": "klimb123*",
    }

    with patch("app.database.crud.create_user") as mock_create:
        mock_create.return_value = {
            "id": "fffbc1d8-e0b2-4789-950e-844f9aa9f623",
            **user_data,
            "created_at": "2024-10-22T23:23:54.013Z",
        }

        response = client.post("/user", json=user_data)
        assert response.status_code == 201
        assert response.json() == {
            "username": "operador_test",
            "role": "operador",
            "id": "fffbc1d8-e0b2-4789-950e-844f9aa9f623",
            "created_at": "2024-10-22T23:23:54.013000Z",
        }


def test_create_user_username_taken():
    user_data = {
        "username": "operador_test",
        "role": "operador",
        "password": "klimb123*",
    }

    with patch("app.database.crud.get_user_by_username", return_value=True):
        response = client.post("/user", json=user_data)
        assert response.status_code == 400
        assert response.json() == {"detail": "This username is already registered."}


def test_create_user_db_error():
    user_data = {
        "username": "operador_test",
        "role": "operador",
        "password": "klimb123*",
    }

    with patch("app.database.crud.get_user_by_username", return_value=None):
        with patch("app.database.crud.create_user", side_effect=SQLAlchemyError):
            response = client.post("/user", json=user_data)
            assert response.status_code == 500
            assert response.json() == {"detail": "Database error."}


# ======================================================
#               TEST GET /user/{user_id}
# ======================================================
def test_get_user_success():
    user_id = "fffbc1d8-e0b2-4789-950e-844f9aa9f623"

    with patch("app.database.crud.get_user_by_id") as mock_get:
        mock_get.return_value = {
            "username": "operador_test",
            "role": "operador",
            "id": user_id,
            "created_at": "2024-10-22T23:23:54.013000Z",
        }

        response = client.get(f"/user/{user_id}")
        assert response.status_code == 200
        assert response.json() == {
            "username": "operador_test",
            "role": "operador",
            "id": user_id,
            "created_at": "2024-10-22T23:23:54.013000Z",
        }


def test_get_user_not_found():
    user_id = "invalid_user_id"

    with patch("app.database.crud.get_user_by_id", return_value=None):
        response = client.get(f"/user/{user_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found."}

# ======================================================
#             TEST DELETE /user/{user_id}
# ======================================================
def test_delete_user_success():
    user_id = "fffbc1d8-e0b2-4789-950e-844f9aa9f623"

    with patch("app.database.crud.get_user_by_id") as mock_get:
        mock_get.return_value = {
            "username": "operador_test",
            "role": "operador",
            "id": user_id,
            "created_at": "2024-10-22T23:23:54.013000Z",
        }

        response = client.delete(f"/user/{user_id}")
        assert response.status_code == 204


def test_delete_user_not_found():
    user_id = "invalid_user_id"

    with patch("app.database.crud.get_user_by_id", return_value=None):
        response = client.delete(f"/user/{user_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found."}


def test_delete_user_db_error():
    user_id = "fffbc1d8-e0b2-4789-950e-844f9aa9f623"

    with patch("app.database.crud.get_user_by_id", return_value={"id": user_id}):
        with patch("app.database.crud.delete_user_by_id", side_effect=SQLAlchemyError):
            response = client.delete(f"/user/{user_id}")
            assert response.status_code == 500
            assert response.json() == {"detail": "Database error."}


# ======================================================
#                  TEST POST /login
# ======================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def test_login_success():
    user_data = {
        "username": "operador_test",
        "password": "klimb123*",
    }

    password_hash = pwd_context.hash(user_data["password"])

    mock_user = MagicMock()
    mock_user.username = "operador_test"
    mock_user.password_hash = password_hash
    mock_user.role = "operador"

    with patch("app.database.crud.get_user_by_username", return_value=mock_user):
        with patch("app.routers.users.create_access_token") as mock_create_access_token:
            mock_create_access_token.return_value = "mocked_jwt_token"

            response = client.post(
                "/login",
                data={
                    "username": user_data["username"],
                    "password": user_data["password"],
                },
            )

            assert response.status_code == 200
            assert response.json() == {
                "access_token": "mocked_jwt_token",
                "token_type": "bearer",
            }


def test_login_invalid_credentials():
    user_data = {
        "username": "operador_test",
        "password": "wrong_password",
    }

    mock_user = MagicMock()
    mock_user.username = "operador_test"
    mock_user.password_hash = pwd_context.hash("klimb123*")  # Contraseña correcta

    with patch("app.database.crud.get_user_by_username", return_value=mock_user):
        response = client.post(
            "/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"],
            },
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid username or password."}


def test_login_user_not_found():
    user_data = {
        "username": "nonexistent_user",
        "password": "klimb123*",
    }

    with patch("app.database.crud.get_user_by_username", return_value=None):
        response = client.post(
            "/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"],
            },
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid username or password."}
