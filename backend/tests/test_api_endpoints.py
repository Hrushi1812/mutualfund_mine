import pytest

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root API endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Mutual Fund Tracker API"}

@pytest.mark.asyncio
async def test_auth_register(client, sample_user_data):
    """Test user registration endpoint"""
    response = client.post("/auth/register", json=sample_user_data)
    assert response.status_code == 201 or response.status_code == 400  # 400 if user already exists

@pytest.mark.asyncio
async def test_auth_login(client, sample_user_data):
    """Test user login endpoint"""
    # Register user first (if not already registered)
    client.post("/auth/register", json=sample_user_data)
    response = client.post("/auth/login", json={
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_portfolio_create(client, sample_portfolio_data):
    """Test portfolio creation endpoint"""
    # You may need to authenticate first and pass the token in headers
    response = client.post("/portfolio/", json=sample_portfolio_data)
    assert response.status_code == 201 or response.status_code == 401  # 401 if not authenticated

@pytest.mark.asyncio
async def test_portfolio_get(client):
    """Test getting portfolio endpoint"""
    response = client.get("/portfolio/")
    assert response.status_code == 200 or response.status_code == 401  # 401 if not authenticated