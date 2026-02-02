import type { RequestHandler } from '@sveltejs/kit';
import { json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, cookies }) => {
  try {
    const body = await request.json();
    const email = String(body.email || '').trim();
    const password = String(body.password || '');

    // Basic hardcoded check (change as needed)
    const VALID_EMAIL = 'test@example.com';
    const VALID_PASSWORD = 'password';

    if (email === VALID_EMAIL && password === VALID_PASSWORD) {
      // Set a simple cookie to represent a session / JWT
      cookies.set('jwt', 'dummy-token-for-dev', {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: false,
        maxAge: 60 * 60 * 24 * 7 // 7 days
      });

      return json({ success: true });
    }

    return json({ success: false, error: 'Invalid email or password' }, { status: 401 });
  } catch (err) {
    return json({ success: false, error: 'Invalid request' }, { status: 400 });
  }
};
