import pytest
from flask import url_for
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_signup(client):
    # Testing with a strong password that meets the criteria
    response = client.post('/signup', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'Test@1234'})
    assert response.status_code == 302  # Expecting redirect after successful signup
    assert response.headers['Location'].endswith('/home')  # Assert that the URL ends with '/home'

    # Testing with a weak password that does not meet the criteria
    response = client.post('/signup', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'weak'})
    assert response.status_code == 200  # Expecting status code indicating no redirect
    assert b'Please enter a password.' in response.data  # Assert that error message is displayed
    assert 'Location' not in response.headers  # Assert that there is no redirect header present

def test_signin(client):
    # Testing signin with valid credentials
    response = client.post('/signin', data={'email': 'test@example.com', 'password': 'Test@1234'})
    assert response.status_code == 302  # Expecting redirect after successful signin
    assert response.headers['Location'].endswith('/home')  # Assert that the URL ends with '/home'

    # Testing signin with invalid credentials
    response = client.post('/signin', data={'email': 'invalid@example.com', 'password': 'invalid_password'})
    assert response.status_code == 200  # Expecting status code indicating no redirect
    assert b'Invalid email or password.' in response.data  # Assert that error message is displayed
    assert 'Location' not in response.headers  # Assert that there is no redirect header present

def test_signup_form_render(client):
    response = client.get('/signup')
    assert b'Create Account' in response.data  # Expecting signup form to be rendered

def test_signin_form_render(client):
    response = client.get('/signin')
    assert b'Sign in' in response.data  # Expecting signin form to be rendered
