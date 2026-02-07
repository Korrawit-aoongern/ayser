import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit';


export const handle: Handle = async ({ event, resolve }) => {
	const pathname = event.url.pathname;

	// Allow auth routes without authentication
	if (pathname.startsWith('/services/auth')) {
		return resolve(event);
	}

	// Check for JWT token in cookies
	const token = event.cookies.get('access_token');

	// If no token and not on auth page, redirect to login
	if (!token && !pathname.startsWith('/services/auth')) {
		throw redirect(303, '/services/auth/login');
	}

	return resolve(event);
};
