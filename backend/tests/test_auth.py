import pytest

@pytest.mark.asyncio
async def test_register_new_user(client, sample_user_data):
    """Test registering a new user"""
    response = client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 201 or response.status_code == 400  # 400 if user already exists

@pytest.mark.asyncio
async def test_login_user(client, sample_user_data):
    """Test logging in with registered user"""
    # Ensure user is registered
    client.post("/auth/register", json=sample_user_data)
    response = client.post("/auth/login", json={
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_password(client, sample_user_data):
    """Test login with invalid password"""
    client.post("/auth/register", json=sample_user_data)
    response = client.post("/auth/login", json={
        "email": sample_user_data["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post("/auth/login", json={
        "email": "nouser@example.com",
        "password": "doesnotmatter"
    })
    assert response.status_code == 401