import requests
import time


BASE_URL = "http://localhost:8000"

ENDPOINTS = {
    "Login API": "/login",
    "Product API": "/products",
    "Payment API": "/payment",
}


def check_endpoint(endpoint):
    start = time.time()

    response = requests.get(BASE_URL + endpoint)

    latency = (time.time() - start) * 1000

    return response.status_code, latency


def test_login_api():
    status, latency = check_endpoint("/login")

    assert status == 200
    assert latency < 1000


def test_product_api():
    status, latency = check_endpoint("/products")

    assert status == 200
    assert latency < 1000


def test_payment_api():
    status, latency = check_endpoint("/payment")

    assert status == 200
    assert latency < 1000