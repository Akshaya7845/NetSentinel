import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 5,
    iterations: 25,

    thresholds: {
        http_req_duration: ['p(95)<200'],
    },
};

export default function () {

    let login = http.get('http://localhost:8000/login');
    check(login, {
        'Login API Status 200': (r) => r.status === 200,
    });

    let products = http.get('http://localhost:8000/products');
    check(products, {
        'Product API Status 200': (r) => r.status === 200,
    });

    let payment = http.get('http://localhost:8000/payment');
    check(payment, {
        'Payment API Status 200': (r) => r.status === 200,
    });

    sleep(1);
}