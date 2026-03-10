import { expect, test } from '@playwright/test';

test('login page renders basic form fields', async ({ page }) => {
	await page.goto('/services/auth/login');

	await expect(page.getByRole('heading', { name: 'Ayser' })).toBeVisible();
	await expect(page.getByPlaceholder('Enter your email')).toBeVisible();
	await expect(page.getByPlaceholder('Enter your password')).toBeVisible();
	await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
	await expect(page.getByRole('link', { name: 'To Register' })).toBeVisible();
});
