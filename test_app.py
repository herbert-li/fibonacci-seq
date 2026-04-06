import pytest
from app import app, fibonacci


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFibonacci:
    """Test the fibonacci function."""

    def test_base_cases(self):
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1

    def test_small_values(self):
        assert fibonacci(2) == 1
        assert fibonacci(3) == 2
        assert fibonacci(4) == 3
        assert fibonacci(5) == 5
        assert fibonacci(10) == 55

    def test_larger_values(self):
        assert fibonacci(20) == 6765
        assert fibonacci(30) == 832040

    def test_negative_input(self):
        with pytest.raises(ValueError):
            fibonacci(-1)


class TestAPI:
    """Test the API endpoints."""

    def test_health_endpoint(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'

    def test_fibonacci_endpoint_success(self, client):
        response = client.get('/fibonacci?n=2')
        assert response.status_code == 200
        assert response.json['n'] == 2
        assert response.json['result'] == 1

    def test_fibonacci_endpoint_n_10(self, client):
        response = client.get('/fibonacci?n=10')
        assert response.status_code == 200
        assert response.json['n'] == 10
        assert response.json['result'] == 55

    def test_fibonacci_endpoint_n_0(self, client):
        response = client.get('/fibonacci?n=0')
        assert response.status_code == 200
        assert response.json['result'] == 0

    def test_missing_parameter(self, client):
        response = client.get('/fibonacci')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_invalid_parameter_type(self, client):
        response = client.get('/fibonacci?n=abc')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_negative_parameter(self, client):
        response = client.get('/fibonacci?n=-5')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_parameter_too_large(self, client):
        response = client.get('/fibonacci?n=100000')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_not_found(self, client):
        response = client.get('/nonexistent')
        assert response.status_code == 404
