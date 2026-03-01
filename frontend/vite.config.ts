import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		proxy: {
			// เมื่อเรียก /api ใน frontend จะถูกส่งไปหา backend โดยอัตโนมัติ
			'/api': {
				target: 'http://backend:8000',
				changeOrigin: true
			}
		}
	}
});
