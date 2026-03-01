<script lang="ts">
	import { page } from '$app/stores';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';

	let serviceId: number | null = null;
	let loading = false;
	let error = '';

	let formData = {
		serviceName: '',
		url: '',
		advancedMethod: 'None',
		metricsEndpoint: ''
	};

	const advancedMethods = ['None', 'Metrics endpoint'];

	function toAdvancedMethod(checkType: string | null | undefined) {
		return checkType === 'url_metrics' ? 'Metrics endpoint' : 'None';
	}

	function toCheckType(method: string) {
		return method === 'Metrics endpoint' ? 'url_metrics' : 'url';
	}

	function validateForm() {
		const serviceName = formData.serviceName.trim();
		const url = formData.url.trim();
		const useMetricsEndpoint = formData.advancedMethod === 'Metrics endpoint';
		const metricsEndpoint =
			(useMetricsEndpoint ? formData.metricsEndpoint : '/metrics').trim() || '/metrics';

		if (!serviceName) return 'Service name is required.';
		if (serviceName.length > 30) return 'Service name must be at most 30 characters.';
		if (!url) return 'URL is required.';
		if (url.length > 50) return 'URL must be at most 50 characters.';
		if (useMetricsEndpoint) {
			if (metricsEndpoint.length > 50) return '/metrics endpoint must be at most 50 characters.';
			if (!metricsEndpoint.startsWith('/')) return '/metrics endpoint must start with "/".';
		}

		return null;
	}

	// Load service data based on ID
	$: if (browser) {
		const rawId = $page.url.searchParams.get('id');
		if (!rawId) {
			error = 'Missing service id';
		} else {
			const parsedId = Number.parseInt(rawId, 10);
			if (Number.isNaN(parsedId)) {
				error = 'Invalid service id';
			} else if (parsedId !== serviceId) {
				serviceId = parsedId;
				error = '';
				loadService(parsedId);
			}
		}
	}

	async function loadService(id: number) {
		loading = true;
		try {
			const res = await fetch(`/api/services/${id}`, {
				credentials: 'include'
			});

			if (!res.ok) throw new Error(`Failed to load service (${res.status})`);

			const data = await res.json();
			formData = {
				serviceName: data.service_name ?? '',
				url: data.service_url ?? '',
				advancedMethod: toAdvancedMethod(data.check_type),
				metricsEndpoint: data.metrics_endpoint ?? '/metrics'
			};
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function handleSave() {
		if (!serviceId) return;
		loading = true;
		error = '';
		try {
			const validationError = validateForm();
			if (validationError) throw new Error(validationError);

			const serviceName = formData.serviceName.trim();
			const url = formData.url.trim();
			const metricsEndpoint =
				(formData.advancedMethod === 'Metrics endpoint'
					? formData.metricsEndpoint
					: '/metrics'
				).trim() || '/metrics';

			const res = await fetch(`/api/services/${serviceId}`, {
				method: 'PUT',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					service_name: serviceName,
					service_url: url,
					check_type: toCheckType(formData.advancedMethod),
					metrics_endpoint: metricsEndpoint
				})
			});

			if (!res.ok) throw new Error(`Failed to save service (${res.status})`);
			await res.json();
			window.dispatchEvent(new Event('services:changed'));
			await goto(`/services/details?id=${serviceId}`);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}
</script>

<main class="flex-1 p-12">
	<h1 class="mb-8 text-4xl font-bold">Edit Service</h1>

	{#if error}
		<div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
	{/if}

	<form class="max-w-2xl" on:submit|preventDefault={handleSave}>
		<div class="mb-6">
			<label for="service-name" class="mb-2 block text-sm font-semibold">Service Name</label>
			<input
				type="text"
				class="w-full rounded border border-gray-300 px-4 py-2"
				bind:value={formData.serviceName}
				maxlength="30"
				disabled={loading}
			/>
		</div>

		<div class="mb-6">
			<label for="url" class="mb-2 block text-sm font-semibold">URL</label>
			<input
				type="text"
				class="w-full rounded border border-gray-300 px-4 py-2"
				bind:value={formData.url}
				maxlength="50"
				disabled={loading}
			/>
		</div>

		<div class="mb-6">
			<label for="advanced-methods" class="mb-2 block text-sm font-semibold">Advanced Methods</label
			>
			<select
				class="w-full rounded border border-gray-300 bg-white px-4 py-2"
				bind:value={formData.advancedMethod}
				disabled={loading}
			>
				{#each advancedMethods as method}
					<option value={method}>{method}</option>
				{/each}
			</select>
		</div>

		{#if formData.advancedMethod === 'Metrics endpoint'}
			<div class="mb-6">
				<label for="metrics-endpoint" class="mb-2 block text-sm font-semibold"
					>/metrics endpoint</label
				>
				<input
					type="text"
					placeholder="Enter your /metrics endpoint URL (ex. /metrics)"
					class="w-full rounded border border-gray-300 px-4 py-2"
					bind:value={formData.metricsEndpoint}
					maxlength="50"
					pattern="\/.*"
					disabled={loading}
				/>
			</div>
		{/if}

		<button
			type="submit"
			class="rounded bg-gray-300 px-6 py-2 text-sm font-semibold hover:bg-gray-400 disabled:opacity-50"
			disabled={loading}
		>
			{#if loading}Saving...{:else}Save{/if}
		</button>
	</form>
</main>
