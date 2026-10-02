import { createApp } from './app';
import { OpenEvalClient } from './client';

const port = Number(process.env.PORT || 3000);
const client = new OpenEvalClient(process.env.API_BASE_URL || 'http://localhost:8000', process.env.API_TOKEN || '');
createApp(client).listen(port, () => console.log(JSON.stringify({ event: 'gateway_started', port })));
