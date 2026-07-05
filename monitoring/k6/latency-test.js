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

    let response = http.get('http://localhost:8000/network/status');

    check(response, {
        'Status is 200': (r) => r.status === 200,
    });

    sleep(1);
}