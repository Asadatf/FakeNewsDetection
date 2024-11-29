import pytest
from flask import url_for
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_prediction_form_render(client):
    response = client.get('/prediction')
    assert b'Enter news headlines' in response.data  # Expecting the prediction form to be rendered

def test_prediction(client):
    # Testing prediction with a news headline
    response = client.post('/prediction', data={'news': 'Dean Obeidallah, a former attorney, is the hos...'})
    assert response.status_code == 200  # Expecting status code indicating successful prediction
    assert b'FAKE' in response.data  # Assert that the prediction result is displayed

    # Testing prediction with another news headline
    response = client.post('/prediction', data={'news': 'Some of the biggest issues facing America this...'})
    assert response.status_code == 200  # Expecting status code indicating successful prediction
    assert b'REAL' in response.data  # Assert that the prediction result is displayed
