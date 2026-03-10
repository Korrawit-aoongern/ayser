import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: './tests/e2e',
	timeout: 30_000,
	expect: {
		timeout: 5_000
	},
	use: {
		baseURL: process.env.E2E_BASE_URL ?? 'http://127.0.0.1:4173',
		trace: 'retain-on-failure'
	},
	webServer: {
		command: 'npm run preview -- --host 0.0.0.0 --port 4173',
		port: 4173,
		reuseExistingServer: !process.env.CI,
		timeout: 120_000
	}
});
