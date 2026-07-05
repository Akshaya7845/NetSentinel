import requests
import time

BASE_URL = "http://localhost:8000"


def test_login_api_returns_200():
    response = requests.get(f"{BASE_URL}/login")
    assert response.status_code == 200


def test_product_api_returns_200():
    response = requests.get(f"{BASE_URL}/products")
    assert response.status_code == 200


def test_payment_api_returns_200():
    response = requests.get(f"{BASE_URL}/payment")
    assert response.status_code == 200


def test_login_latency():
    start = time.time()
    requests.get(f"{BASE_URL}/login")
    latency = (time.time() - start) * 1000
    assert latency < 500


def test_product_latency():
    start = time.time()
    requests.get(f"{BASE_URL}/products")
    latency = (time.time() - start) * 1000
    assert latency < 500


def test_payment_latency():
    start = time.time()
    requests.get(f"{BASE_URL}/payment")
    latency = (time.time() - start) * 1000
    assert latency < 500


def test_login_response_not_empty():
    response = requests.get(f"{BASE_URL}/login")
    assert len(response.text) > 0


def test_product_response_not_empty():
    response = requests.get(f"{BASE_URL}/products")
    assert len(response.text) > 0


def test_payment_response_not_empty():
    response = requests.get(f"{BASE_URL}/payment")
    assert len(response.text) > 0