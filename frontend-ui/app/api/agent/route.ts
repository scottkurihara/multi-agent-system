import { NextRequest, NextResponse } from 'next/server';

const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://localhost:8080';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { task } = body;

    if (!task) {
      return NextResponse.json(
        { error: { code: 'INVALID_REQUEST', message: 'Task is required' } },
        { status: 400 }
      );
    }

    // Call the agent service
    const response = await fetch(`${AGENT_SERVICE_URL}/v1/agent/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input: {
          task: task,
        },
        options: {
          stream: false,
        },
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Error calling agent service:', error);
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: error.message || 'Failed to process request',
        },
      },
      { status: 500 }
    );
  }
}
