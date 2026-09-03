
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('large_scale_errors');
const latency = new Trend('large_scale_latency');

export const options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '20s', target: 25 },
    { duration: '20s', target: 10 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(99)<2000'],
    large_scale_errors: ['rate<0.1'],
  },
};

const BASE_URL = 'http://localhost:8000';

const ENDPOINTS = [
  '/health',
  '/metrics',
  '/performance/summary',
  '/network/status',
];

export default function () {
  const endpoint =
    ENDPOINTS[
      Math.floor(Math.random() * ENDPOINTS.length)
    ];

  const response = http.get(
    `${BASE_URL}${endpoint}`
  );

  latency.add(
    response.timings.duration
  );

  errorRate.add(
    response.status !== 200
  );

  check(response, {
    'status OK': (r) => r.status === 200,
    'latency < 2s':
      (r) => r.timings.duration < 2000,
  });

  sleep(0.5);
}

export function handleSummary(data) {
  return {
    'monitoring/reports/scale_tests/k6_large_scale.json':
      JSON.stringify(data, null, 2),
  };
}
