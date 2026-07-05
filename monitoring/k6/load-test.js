import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {

    stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 20 },
        { duration: '30s', target: 0 },
    ],

    thresholds: {
        http_req_duration: ['p(95)<300'],
        http_req_failed: ['rate<0.01'],
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