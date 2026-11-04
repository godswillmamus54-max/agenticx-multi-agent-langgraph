
import {
  createHmac,
  createHash,
  timingSafeEqual,
} from "node:crypto";

import type { NextRequest } from "next/server";

export const SESSION_COOKIE = "agenticx_session";
const SESSION_DURATION = 8 * 60 * 60 * 1000; // 8 hours

function getSessionSecret(): string {
  const secret = process.env.AGENTICX_SESSION_SECRET;

  if (!secret || secret.length < 32) {
    throw new Error("Session secret is missing or too short.");
  }

  return secret;
}

export function verifyAccessPassword(password: string): boolean {
  const configuredPassword = process.env.AGENTICX_ACCESS_PASSWORD;

  if (!configuredPassword || !password) {
    return false;
  }

  const suppliedHash = createHash("sha256")
    .update(password)
    .digest();

  const configuredHash = createHash("sha256")
    .update(configuredPassword)
    .digest();

  return timingSafeEqual(suppliedHash, configuredHash);
}

export function createSessionToken(): string {
  const payload = {
    exp: Date.now() + SESSION_DURATION,
  };

  const encodedPayload = Buffer
    .from(JSON.stringify(payload))
    .toString("base64url");

  const signature = createHmac("sha256", getSessionSecret())
    .update(encodedPayload)
    .digest("base64url");

  return `${encodedPayload}.${signature}`;
}

export function isAuthenticated(request: NextRequest): boolean {
  try {
    const token = request.cookies.get(SESSION_COOKIE)?.value;

    if (!token) return false;

    const parts = token.split(".");
    if (parts.length !== 2) return false;

    const [encodedPayload, suppliedSignature] = parts;

    const expectedSignature = createHmac(
      "sha256",
      getSessionSecret()
    )
      .update(encodedPayload)
      .digest();

    const actualSignature = Buffer.from(
      suppliedSignature,
      "base64url"
    );

    if (actualSignature.length !== expectedSignature.length) {
      return false;
    }

    if (!timingSafeEqual(actualSignature, expectedSignature)) {
      return false;
    }

    const payload = JSON.parse(
      Buffer.from(encodedPayload, "base64url").toString("utf8")
    );

    return (
      typeof payload.exp === "number" &&
      payload.exp > Date.now()
    );
  } catch {
    return false;
  }
}

export function sessionCookieOptions(secure: boolean) {
  return {
    httpOnly: true,
    secure,
    sameSite: "strict" as const,
    path: "/",
    maxAge: SESSION_DURATION / 1000,
  };
}
