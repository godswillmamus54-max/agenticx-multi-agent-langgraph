
import { NextRequest, NextResponse } from "next/server";

import {
  createSessionToken,
  SESSION_COOKIE,
  sessionCookieOptions,
  verifyAccessPassword,
} from "@/lib/auth";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (
      typeof body.password !== "string" ||
      body.password.length === 0 ||
      body.password.length > 256
    ) {
      return NextResponse.json(
        { error: "Enter a valid access password." },
        { status: 400 }
      );
    }

    if (!process.env.AGENTICX_ACCESS_PASSWORD) {
      console.error("AGENTICX_ACCESS_PASSWORD is not configured.");

      return NextResponse.json(
        { error: "Authentication is not configured." },
        { status: 500 }
      );
    }

    if (!verifyAccessPassword(body.password)) {
      return NextResponse.json(
        { error: "Incorrect access password." },
        { status: 401 }
      );
    }

    const token = createSessionToken();

    const response = NextResponse.json({
      success: true,
      message: "Authentication successful.",
    });

    const secure =
      process.env.NODE_ENV === "production" ||
      request.headers.get("x-forwarded-proto") === "https";

    response.cookies.set(
      SESSION_COOKIE,
      token,
      sessionCookieOptions(secure)
    );

    return response;
  } catch (error) {
    console.error("Login error:", error);

    return NextResponse.json(
      { error: "Unable to process login." },
      { status: 400 }
    );
  }
}
