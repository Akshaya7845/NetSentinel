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

    let response = http.get('http://localhost:8000/performance/summary');

    check(response, {
        'Status is 200': (r) => r.status === 200,
    });

    sleep(1);
}