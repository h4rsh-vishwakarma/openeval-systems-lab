import request from 'supertest';
import { createApp } from '../src/app';
import { OpenEvalClient } from '../src/client';

const client = {
  createTask: jest.fn().mockResolvedValue({ id: 't1', state: 'created' }),
  getTask: jest.fn().mockResolvedValue({ id: 't1', state: 'created' }),
  submit: jest.fn().mockResolvedValue({ id: 't1', state: 'queued' }),
  result: jest.fn().mockResolvedValue({ task_id: 't1', state: 'completed' }),
} as unknown as OpenEvalClient;
const app = createApp(client);

test('rejects missing idempotency key', async () => {
  const result = await request(app).post('/tasks').send({ scenario: 'webhook_once' });
  expect(result.status).toBe(400);
});
test('creates a typed task', async () => {
  const result = await request(app).post('/tasks').set('Idempotency-Key', 'demo').send({ scenario: 'webhook_once', input: {} });
  expect(result.status).toBe(201);
  expect(result.body.id).toBe('t1');
});
test('rejects invalid submission', async () => {
  const result = await request(app).post('/tasks/t1/submit').send({ implementation: 'unknown' });
  expect(result.status).toBe(400);
});
test('accepts the C++ golden evaluator implementation', async () => {
  const result = await request(app).post('/tasks/t1/submit').send({ implementation: 'cpp_golden' });
  expect(result.status).toBe(200);
  expect(client.submit).toHaveBeenCalledWith('t1', { implementation: 'cpp_golden', inject_failure: 'none' });
});
