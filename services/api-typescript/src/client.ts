import type { Submission, Task, TaskCreate } from './types';

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export class OpenEvalClient {
  constructor(private baseUrl: string, private token: string) {}

  private async request<T>(path: string, method = 'GET', body?: object, key?: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: { Authorization: `Bearer ${this.token}`, 'Content-Type': 'application/json', ...(key ? { 'Idempotency-Key': key } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
      signal: AbortSignal.timeout(10000),
    });
    const json: unknown = await response.json();
    if (!response.ok) {
      const detail = typeof json === 'object' && json !== null && 'error' in json ? JSON.stringify(json.error) : response.statusText;
      throw new ApiError(response.status, detail);
    }
    return json as T;
  }

  createTask(input: TaskCreate, key: string): Promise<Task> { return this.request('/tasks', 'POST', input, key); }
  getTask(id: string): Promise<Task> { return this.request(`/tasks/${encodeURIComponent(id)}`); }
  submit(id: string, input: Submission): Promise<Task> { return this.request(`/tasks/${encodeURIComponent(id)}/submit`, 'POST', input); }
  result(id: string): Promise<{ task_id: string; state: string; result: Task['result']; error: string | null }> { return this.request(`/tasks/${encodeURIComponent(id)}/result`); }
}
