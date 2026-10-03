import { z } from 'zod';

export const taskCreateSchema = z.object({
  scenario: z.literal('webhook_once').default('webhook_once'),
  input: z.object({ events: z.array(z.record(z.unknown())).optional() }).default({}),
});
export const submissionSchema = z.object({
  implementation: z.enum(['golden', 'defective_duplicate', 'defective_validation', 'cpp_golden']),
  inject_failure: z.enum(['none', 'timeout', 'invalid_output', 'transient']).default('none'),
});
export type TaskCreate = z.infer<typeof taskCreateSchema>;
export type Submission = z.infer<typeof submissionSchema>;
export type TaskState = 'created' | 'queued' | 'running' | 'retry_wait' | 'completed' | 'dead_letter';
export interface Task {
  id: string;
  tenant_id: string;
  state: TaskState;
  attempts: number;
  spec: TaskCreate;
  result: { score: number; passed: number; total: number; checks: Array<{ name: string; passed: boolean; reason: string }>; review: Array<{ check: string; suggestion: string; source: string; provider: 'local_mock' }> } | null;
  error: string | null;
}
