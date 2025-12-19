"""Integration tests for authentication endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestAuthRegistration:
    """Test user registration."""
    
    async def test_register_customer_success(self, client: AsyncClient):
        """Test successful customer registration."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "newcustomer@test.com",
                "password": "SecurePass@123",
                "phone": "+923004444444",
                "full_name": "New Customer",
                "address": "789 New St",
                "latitude": 24.8607,
                "longitude": 67.0011
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newcustomer@test.com"
        assert data["role"] == "customer"
        assert "id" in data
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_customer):
        """Test registration with duplicate email."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": test_customer.email,
                "password": "SecurePass@123",
                "phone": "+923005555555",
                "full_name": "Another Customer",
                "address": "123 Duplicate St",
                "latitude": 24.8607,
                "longitude": 67.0011
            }
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "invalid-email",
                "password": "SecurePass@123",
                "phone": "+923006666666",
                "full_name": "Invalid Email User",
                "address": "123 Invalid St",
                "latitude": 24.8607,
                "longitude": 67.0011
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "weakpass@test.com",
                "password": "weak",
                "phone": "+923007777777",
                "full_name": "Weak Password User",
                "address": "123 Weak St",
                "latitude": 24.8607,
                "longitude": 67.0011
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_invalid_coordinates(self, client: AsyncClient):
        """Test registration with invalid coordinates."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "badcoords@test.com",
                "password": "SecurePass@123",
                "phone": "+923008888888",
                "full_name": "Bad Coords User",
                "address": "123 Bad St",
                "latitude": 91.0,  # Invalid: > 90
                "longitude": 67.0011
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_provider_success(self, client: AsyncClient):
        """Test successful provider registration."""
        response = await client.post(
            "/auth/register/provider",
            json={
                "email": "newprovider@test.com",
                "password": "ProviderPass@123",
                "phone": "+923009999999",
                "business_name": "New Provider Services",
                "business_type": "individual",
                "description": "Professional services",
                "address": "101 Provider Ave",
                "latitude": 24.8707,
                "longitude": 67.0111
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newprovider@test.com"
        assert data["role"] == "provider"


@pytest.mark.asyncio
class TestAuthLogin:
    """Test user login."""
    
    async def test_login_success(self, client: AsyncClient, test_customer):
        """Test successful login."""
        response = await client.post(
            "/auth/login",
            json={
                "email": test_customer.email,
                "password": "Test@123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_customer):
        """Test login with wrong password."""
        response = await client.post(
            "/auth/login",
            json={
                "email": test_customer.email,
                "password": "WrongPassword@123"
            }
        )
        
        assert response.status_code == 401
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent email."""
        response = await client.post(
            "/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "SomePass@123"
            }
        )
        
        assert response.status_code == 401
    
    async def test_login_sql_injection(self, client: AsyncClient):
        """Test SQL injection attempt in login."""
        response = await client.post(
            "/auth/login",
            json={
                "email": "admin@test.com' OR '1'='1",
                "password": "anything"
            }
        )
        
        assert response.status_code in [401, 422]  # Should be rejected


@pytest.mark.asyncio
class TestAuthTokenRefresh:
    """Test token refresh functionality."""
    
    async def test_refresh_token_success(self, client: AsyncClient, test_customer):
        """Test successful token refresh."""
        # First login
        login_response = await client.post(
            "/auth/login",
            json={
                "email": test_customer.email,
                "password": "Test@123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthEdgeCases:
    """Test edge cases and error handling."""
    
    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Test registration with missing fields."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "incomplete@test.com"
                # Missing required fields
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_with_special_characters_in_name(self, client: AsyncClient):
        """Test registration with special characters."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "special@test.com",
                "password": "SecurePass@123",
                "phone": "+923001010101",
                "full_name": "Test User <script>alert('xss')</script>",
                "address": "123 Test St",
                "latitude": 24.8607,
                "longitude": 67.0011
            }
        )
        
        # Should either sanitize or reject
        assert response.status_code in [201, 422]
    
    async def test_register_extremely_long_email(self, client: AsyncClient):
        """Test registration with extremely long email."""
        long_email = "a" * 300 + "@test.com"
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": long_email,
                "password": "SecurePass@123",
                "phone": "+923002020202",
                "full_name": "Long Email User",
                "address": "123 Test St",
                "latitude": 24.8607,
                "longitude": 67.0011
            }
        )
        
        assert response.status_code == 422
    
    async def test_register_coordinates_at_poles(self, client: AsyncClient):
        """Test registration with coordinates at poles."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "northpole@test.com",
                "password": "SecurePass@123",
                "phone": "+923003030303",
                "full_name": "North Pole User",
                "address": "North Pole",
                "latitude": 90.0,  # Valid: exactly at pole
                "longitude": 0.0
            }
        )
        
        assert response.status_code == 201
    
    async def test_register_coordinates_crossing_dateline(self, client: AsyncClient):
        """Test registration with coordinates near dateline."""
        response = await client.post(
            "/auth/register/customer",
            json={
                "email": "dateline@test.com",
                "password": "SecurePass@123",
                "phone": "+923004040404",
                "full_name": "Dateline User",
                "address": "Near Dateline",
                "latitude": 0.0,
                "longitude": 179.9  # Valid: near dateline
            }
        )
        
        assert response.status_code == 201
