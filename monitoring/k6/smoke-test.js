import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 1,
    iterations: 1,
};

export default function () {

    let response = http.get('http://localhost:8080');

    check(response, {
        'Status is 200': (r) => r.status === 200,
    });

    sleep(1);
}