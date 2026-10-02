import express, { type Request, type Response, type NextFunction } from 'express';
import { ZodError } from 'zod';
import { ApiError, OpenEvalClient } from './client';
import { submissionSchema, taskCreateSchema } from './types';

export function createApp(client: OpenEvalClient) {
  const app = express();
  app.use(express.json({ limit: '64kb' }));
  app.get('/health', (_request, response) => response.json({ status: 'ok' }));
  app.post('/tasks', async (request, response, next) => {
    try {
      const key = request.header('Idempotency-Key');
      if (!key) return response.status(400).json({ error: { code: 'validation', message: 'Idempotency-Key required' } });
      response.status(201).json(await client.createTask(taskCreateSchema.parse(request.body), key));
    } catch (error) { next(error); }
  });
  app.get('/tasks/:id', async (request, response, next) => {
    try { response.json(await client.getTask(request.params.id)); } catch (error) { next(error); }
  });
  app.post('/tasks/:id/submit', async (request, response, next) => {
    try { response.json(await client.submit(request.params.id, submissionSchema.parse(request.body))); } catch (error) { next(error); }
  });
  app.get('/tasks/:id/result', async (request, response, next) => {
    try { response.json(await client.result(request.params.id)); } catch (error) { next(error); }
  });
  app.use((error: unknown, _request: Request, response: Response, _next: NextFunction) => {
    if (error instanceof ZodError) return response.status(400).json({ error: { code: 'validation', message: error.message } });
    if (error instanceof ApiError) return response.status(error.status).json({ error: { code: String(error.status), message: error.message } });
    return response.status(502).json({ error: { code: 'upstream', message: 'Upstream service unavailable' } });
  });
  return app;
}
