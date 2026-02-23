<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
    import AyserIcon from '../assets/Ayser-Icon.png';

	let services: Array<{ id: number; name: string }> = [];
	let loading = true;
	let error = '';
	let username = 'Username';
	let userLoading = false;

	async function logout(e : Event) {
		e.preventDefault();
		
		try {
			const res = await fetch('/api/auth/logout', {
				method: 'POST',
				credentials: 'include',
			});

			if (res.ok) {
				await goto('/services/auth/login');
				alert('Logged out successfully');
			} else {
				alert('Logout failed');
			}
		} catch (error) {
			console.error('Logout error:', error);
			alert('Logout error');
		}
	}

	async function loadServices() {
		try {
			const res = await fetch('/api/services', {
				method: 'GET',
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (res.status === 401) {
				await goto('/services/auth/login');
				return;
			}

			if (!res.ok) throw new Error(`HTTP error: ${res.status}`);

			const data = await res.json();
			services = data.map((s: any) => ({
				id: s.service_id,
				name: s.service_name || `Service ${s.service_id}`
			}));
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	async function loadUser() {
		userLoading = true;
		try {
			const res = await fetch('/api/user', {
				method: 'GET',
				credentials: 'include'
			});

			if (!res.ok) return;
			const data = await res.json();
			username = data.username || 'Username';
		} catch {
			username = 'Username';
		} finally {
			userLoading = false;
		}
	}

	onMount(() => {
		if (!browser) return;
		loadUser();
		loadServices();
		const handler = () => {
			loading = true;
			loadServices();
		};
		const userHandler = () => {
			loadUser();
		};
		window.addEventListener('services:changed', handler);
		window.addEventListener('user:changed', userHandler);
		return () => {
			window.removeEventListener('services:changed', handler);
			window.removeEventListener('user:changed', userHandler);
		};
	});
</script>

<!-- Left Sidebar -->
<aside class="flex w-48 flex-col bg-gray-200">
	<!-- Service Section -->
	<div class="flex-1">
		<div class= "p-1">
			<a href="/" >
            <img src={AyserIcon} alt="Ayser Logo" class="h-max w-max mx-auto"/>
            </a>
		</div>

		<nav class="space-y-2 p-4">
			<div class="mb-3 text-sm text-gray-600">Service</div>
			<a
				href="/services"
				class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page.url
					.pathname === '/services'
					? 'bg-gray-400 font-bold'
					: ''}"
			>
				All Services
			</a>
			{#if loading}
				<div class="px-4 py-2 text-sm text-gray-500">Loading...</div>
			{:else if error}
				<div class="px-4 py-2 text-sm text-red-600">Failed to load</div>
			{:else}
				{#each services as service}
					<a
						href={`/services/details?id=${service.id}`}
						class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page.url
							.pathname === '/services/details' && $page.url.searchParams.get('id') === String(service.id)
							? 'bg-gray-400 font-bold'
							: ''}"
					>
						{service.name}
					</a>
				{/each}
			{/if}
			<a
				href="/services/new"
				class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page
					.url.pathname === '/services/new'
					? 'bg-gray-400 font-bold'
					: ''}"
			>
				+ New Service
			</a>
		</nav>
	</div>

	<!-- Account Section (Bottom) -->
	<div class="border-t border-gray-300">
		<div class="p-4">
			<h3 class="mb-3 text-sm text-gray-600">Account</h3>
			<div class="space-y-2">
				<a
					href="/user"
					class="flex w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page
						.url.pathname === '/user'
						? 'font-bold bg-gray-400'
						: ''}"
				>
					<span class="mr-2 h-6 w-6 rounded-full bg-gray-500"></span>
					{userLoading ? 'Loading...' : username}
				</a>
				<a
					href="/doc"
					class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page.url
						.pathname === '/doc'
						? 'bg-gray-400 font-bold'
						: ''}"
				>
					Document
				</a>
				<a
					href="/services/auth/login"
					on:click={logout}
					class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400"
				>
					Logout
				</a>
			</div>
		</div>
	</div>
</aside>

<style>
	/* Additional custom styles if needed */
</style>
