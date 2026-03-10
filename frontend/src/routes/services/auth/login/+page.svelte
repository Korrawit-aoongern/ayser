<script lang="ts">
	let email = '';
	let password = '';
	let error = '';
	let loading = false;

	async function handleLogin(e: Event) {
		e.preventDefault();
		loading = true;
		error = '';

		const res = await fetch('/api/auth/login', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include',
			body: JSON.stringify({ email, password })
		});

		const data = await res.json();

		if (res.ok) {
			window.location.href = '/';
		} else {
			error = data.detail || 'Login failed';
		}

		loading = false;
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

		<form on:submit={handleLogin}>
			<div class="mb-6">
				<label for="email" class="mb-2 block text-sm font-semibold">Email</label>
				<input
					name="email"
					type="email"
					placeholder="Enter your email"
					class="w-full rounded border border-gray-300 bg-gray-200 px-4 py-2"
					bind:value={email}
					required
				/>
			</div>

			<div class="mb-6">
				<label for="password" class="mb-2 block text-sm font-semibold">Password</label>
				<input
					name="password"
					type="password"
					placeholder="Enter your password"
					class="w-full rounded border border-gray-300 bg-gray-200 px-4 py-2"
					bind:value={password}
					required
				/>
			</div>

			<button
				type="submit"
				class="mb-4 w-full rounded border border-gray-400 bg-white px-6 py-2 text-sm font-semibold hover:bg-gray-100"
				disabled={loading}
			>
				{#if loading}Logging in...{:else}Login{/if}
			</button>
		</form>

		<a
			href="/services/auth/register"
			class="block w-full rounded bg-gray-300 px-6 py-2 text-center text-sm font-semibold hover:bg-gray-400"
		>
			To Register
		</a>
	</div>
</div>
