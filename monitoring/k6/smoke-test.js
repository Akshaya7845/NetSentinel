import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 1,
    iterations: 1,
};

export default function () {

    // Login API
    let loginResponse = http.get('http://localhost:8000/login');

    check(loginResponse, {
        'Login API is reachable': (r) => r.status === 200,
    });

    // Product API
    let productResponse = http.get('http://localhost:8000/products');

    check(productResponse, {
        'Product API is reachable': (r) => r.status === 200,
    });

    // Payment API
    let paymentResponse = http.get('http://localhost:8000/payment');

    check(paymentResponse, {
        'Payment API is reachable': (r) => r.status === 200,
    });

    sleep(1);
}