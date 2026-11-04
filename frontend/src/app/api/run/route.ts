
import { NextRequest, NextResponse } from "next/server";
import { isAuthenticated } from "@/lib/auth";

const BACKEND_URL = "http://127.0.0.1:8000";

// Basic in-memory rate limit: 5 executions per session per minute.
const requestLog = new Map<string, number[]>();

function isRateLimited(session: string): boolean {
  const now = Date.now();
  const windowMs = 60_000;
  const maxRequests = 5;

  const recentRequests = (requestLog.get(session) || [])
    .filter((timestamp) => now - timestamp < windowMs);

  if (recentRequests.length >= maxRequests) {
    requestLog.set(session, recentRequests);
    return true;
  }

  recentRequests.push(now);
  requestLog.set(session, recentRequests);

  return false;
}

export async function POST(request: NextRequest) {
  // Reject requests without a valid signed session.
  if (!isAuthenticated(request)) {
    return NextResponse.json(
      { error: "Authentication required. Please log in." },
      { status: 401 }
    );
  }

  const session = request.cookies.get("agenticx_session")?.value;

  if (!session) {
    return NextResponse.json(
      { error: "Authentication required." },
      { status: 401 }
    );
  }

  if (isRateLimited(session)) {
    return NextResponse.json(
      { error: "Execution limit reached. Please wait one minute." },
      { status: 429 }
    );
  }

  try {
    const body = await request.json();

    const backendResponse = await fetch(`${BACKEND_URL}/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(180_000),
    });

    const result = await backendResponse.json();

    return NextResponse.json(result, {
      status: backendResponse.status,
    });
  } catch (error) {
    console.error("Research API proxy error:", error);

    return NextResponse.json(
      { error: "Unable to reach the research engine. Please try again." },
      { status: 502 }
    );
  }
}
