<script lang="ts">
	let username = '';
	let email = '';
	let password = '';
	let error = '';
	const apiBase = import.meta.env.VITE_API_BASE_URL;

	async function handleRegister(e: Event) {
		e.preventDefault();

		const res = await fetch(`${apiBase}/api/auth/register`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include',
			body: JSON.stringify({ username, email, password })
		});

		const data = await res.json();

		if (res.ok) {
			window.location.href = '/services/auth/login';
		} else {
			error = data.detail || 'Register failed';
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-gray-100">
	<div class="w-full max-w-md rounded-lg bg-white p-12 shadow-lg">
		<div class="mb-8 text-center">
			<h1 class="mb-2 text-4xl font-bold">Ayser</h1>
			<p class="text-gray-600">Website & Service Health Advisor</p>
		</div>

		{#if error}
			<div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
		{/if}

		<form on:submit={handleRegister}>
			<div class="mb-6">
				<label for="username" class="mb-2 block text-sm font-semibold">Username</label>
				<input
					type="text"
					class="w-full rounded border border-gray-300 bg-gray-200 px-4 py-2"
					bind:value={username}
					required
				/>
			</div>

			<div class="mb-6">
				<label for="email" class="mb-2 block text-sm font-semibold">Email</label>
				<input
					type="email"
					class="w-full rounded border border-gray-300 bg-gray-200 px-4 py-2"
					bind:value={email}
					required
				/>
			</div>

			<div class="mb-6">
				<label for="password" class="mb-2 block text-sm font-semibold">Password</label>
				<input
					type="password"
					class="w-full rounded border border-gray-300 bg-gray-200 px-4 py-2"
					bind:value={password}
					required
				/>
			</div>

			<button
				type="submit"
				class="mb-4 w-full rounded border border-gray-400 bg-white px-6 py-2 text-sm font-semibold hover:bg-gray-100"
			>
				Register
			</button>
		</form>

		<a
			href="/services/auth/login"
			class="block w-full rounded bg-gray-300 px-6 py-2 text-center text-sm font-semibold hover:bg-gray-400"
		>
			To Login
		</a>
	</div>
</div>
