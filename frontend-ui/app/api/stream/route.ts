import { NextRequest } from 'next/server';

const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://localhost:8080';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { task } = body;

  if (!task) {
    return new Response(
      JSON.stringify({ error: 'Task is required' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  try {
    const response = await fetch(`${AGENT_SERVICE_URL}/v1/agent/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input: {
          task: task,
        },
      }),
    });

    if (!response.ok) {
      return new Response(
        JSON.stringify({ error: 'Failed to connect to agent service' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Forward the streaming response
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error: any) {
    console.error('Streaming error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
