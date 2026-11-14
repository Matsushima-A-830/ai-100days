// Minimal mock of Ollama's OpenAI-compatible /v1/chat/completions endpoint.
// Used because the Routine's cloud network policy does not allow downloading
// the real Ollama binary (see results.md). Logs every incoming request body
// so we can inspect exactly what opencodex forwarded.
const http = require('http');

const PORT = 11434;

http.createServer((req, res) => {
  let body = '';
  req.on('data', (chunk) => (body += chunk));
  req.on('end', () => {
    console.log(`[mock-ollama] ${req.method} ${req.url}`);
    console.log(`[mock-ollama] headers: ${JSON.stringify(req.headers)}`);
    console.log(`[mock-ollama] body: ${body}`);

    if (req.url.startsWith('/v1/chat/completions')) {
      const parsed = JSON.parse(body || '{}');
      const replyText =
        'Hello from the mock Ollama backend. opencodex proxied this correctly.';

      if (parsed.stream) {
        // opencodex requests stream:true by default against OpenAI-compatible
        // backends, and expects Server-Sent-Events chunks back.
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          Connection: 'keep-alive',
        });
        const chunk = {
          id: 'chatcmpl-mock-001',
          object: 'chat.completion.chunk',
          created: Math.floor(Date.now() / 1000),
          model: parsed.model || 'mock-model',
          choices: [
            { index: 0, delta: { role: 'assistant', content: replyText }, finish_reason: null },
          ],
        };
        const finalChunk = {
          ...chunk,
          choices: [{ index: 0, delta: {}, finish_reason: 'stop' }],
        };
        res.write(`data: ${JSON.stringify(chunk)}\n\n`);
        res.write(`data: ${JSON.stringify(finalChunk)}\n\n`);
        res.write('data: [DONE]\n\n');
        res.end();
        return;
      }

      const reply = {
        id: 'chatcmpl-mock-001',
        object: 'chat.completion',
        created: Math.floor(Date.now() / 1000),
        model: parsed.model || 'mock-model',
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: replyText,
            },
            finish_reason: 'stop',
          },
        ],
        usage: { prompt_tokens: 10, completion_tokens: 12, total_tokens: 22 },
      };
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(reply));
      return;
    }

    if (req.url.startsWith('/v1/models')) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(
        JSON.stringify({
          object: 'list',
          data: [{ id: 'mock-model', object: 'model' }],
        })
      );
      return;
    }

    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found', url: req.url }));
  });
}).listen(PORT, () => {
  console.log(`[mock-ollama] listening on http://localhost:${PORT}`);
});
