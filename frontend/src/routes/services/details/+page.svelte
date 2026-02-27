<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';

	let serviceId: number = 1;
	let service = {
		service_id: 0,
		service_name: 'Loading...',
		service_url: 'Loading...',
		check_type: 'Loading...',
		created_at: 'Loading...'
	};

	let healthData: {
		health_id: number | null;
		service_id: number;
		availability: string;
		responsiveness: string | null;
		reliability: string | null;
		overall_score: number | null;
		latency_ms: number | null;
		http_status: number | null;
		checked_at: string | null;
	} = {
		health_id: null,
		service_id: 0,
		availability: 'Loading...',
		responsiveness: 'Loading...',
		reliability: 'Loading...',
		overall_score: null,
		latency_ms: null,
		http_status: null,
		checked_at: 'Loading...'
	};

	let events: Array<{
		event_id?: number;
		service_id: number;
		event_level: string;
		event_message: string;
		detected_at?: string;
	}> = [];

	let isLoading = false;
	let isPageLoading = false;
	let error = '';
	let lastLoadedServiceId: number | null = null;
	let showLastCheckRelative = true;

	$: if (browser) {
		const rawId = $page.url.searchParams.get('id');
		if (!rawId) {
			error = 'Missing service id';
		} else {
			const parsedId = Number.parseInt(rawId, 10);
			if (Number.isNaN(parsedId)) {
				error = 'Invalid service id';
			} else if (parsedId !== lastLoadedServiceId) {
				serviceId = parsedId;
				lastLoadedServiceId = parsedId;
				error = '';
				loadService(serviceId, true);
			}
		}
	}

	async function loadService(id: number, showOverlay = false) {
		if (showOverlay) isPageLoading = true;
		try {
			const res = await fetch(`/api/health/services/${id}`, {
				credentials: 'include'
			});

			if (!res.ok) throw new Error('Failed to load service');

			const data = await res.json();
			const servicePayload = data?.service ?? {};
			const healthPayload = data?.health ?? {};

			service = {
				service_id: servicePayload.service_id ?? id,
				service_name: servicePayload.service_name ?? 'Unknown Service',
				service_url: servicePayload.service_url ?? '',
				check_type: servicePayload.check_type ?? 'url',
				created_at: servicePayload.created_at ?? new Date().toISOString()
			};

			healthData = {
				health_id: healthPayload.health_id ?? null,
				service_id: healthPayload.service_id ?? id,
				availability: healthPayload.availability ?? 'Unknown',
				responsiveness: healthPayload.responsiveness ?? null,
				reliability: healthPayload.reliability ?? null,
				overall_score: healthPayload.overall_score ?? null,
				latency_ms: healthPayload.latency_ms ?? null,
				http_status: healthPayload.http_status ?? null,
				checked_at: healthPayload.checked_at ?? null
			};

			events = (data?.events ?? []).map((event: any) => ({
				event_id: event.event_id,
				service_id: event.service_id ?? id,
				event_level: event.event_level ?? event.type ?? 'INFO',
				event_message: event.event_message ?? event.message ?? '',
				detected_at: event.detected_at
			}));
		} catch (e) {
			error = (e as Error).message;
		} finally {
			if (showOverlay) isPageLoading = false;
		}
	}

	// UI state for menu + modal
	let showMenu = false;
	let showConfirm = false;
	let menuRef: HTMLElement | null = null;
	let menuButtonRef: HTMLElement | null = null;

	function toggleMenu() {
		showMenu = !showMenu;
	}

	function openEdit() {
		showMenu = false;
		goto(`/services/details/edit?id=${serviceId}`);
	}

	function confirmDelete() {
		showMenu = false;
		setTimeout(() => (showConfirm = true), 100);
	}

	function cancelDelete() {
		showConfirm = false;
	}

	async function doDelete() {
		showConfirm = false;

		try {
			await fetch(`/api/services/${serviceId}`, {
				method: 'DELETE',
				credentials: 'include'
			});
			window.dispatchEvent(new Event('services:changed'));
			goto('/services');
		} catch (e) {
			error = (e as Error).message;
		}
	}

	let _handler = (e: MouseEvent) => {
		const target = e.target as Node | null;
		if (
			showMenu &&
			menuRef &&
			menuButtonRef &&
			target &&
			!menuRef.contains(target) &&
			!menuButtonRef.contains(target)
		) {
			showMenu = false;
		}
	};

	async function runCheck() {
		isLoading = true;
		error = '';

		try {
			const res = await fetch(`/api/health/services/${serviceId}/check`, {
				method: 'POST',
				credentials: 'include'
			});

			if (!res.ok) throw new Error('Health check failed');

			const checkResult = await res.json();

			// Update health data with check result
			healthData = {
				health_id: checkResult.health_id,
				service_id: checkResult.service_id,
				availability: checkResult.availability,
				responsiveness: checkResult.responsiveness,
				reliability: checkResult.reliability,
				overall_score: checkResult.overall_score,
				latency_ms: checkResult.latency_ms,
				http_status: checkResult.http_status,
				checked_at: checkResult.checked_at
			};

			// Reload service data to get new events
			await loadService(serviceId, false);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			isLoading = false;
		}
	}

	function formatTime(timestamp: string | null | undefined): string {
		if (!timestamp) return 'Never';
		const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(timestamp);
		const normalized = hasTimezone ? timestamp : `${timestamp}Z`;
		const date = new Date(normalized);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMins / 60);
		const diffDays = Math.floor(diffHours / 24);

		if (diffMins < 1) return 'Just now';
		if (diffMins < 60) return `${diffMins}m ago`;
		if (diffHours < 24) return `${diffHours}h ago`;
		return `${diffDays}d ago`;
	}

	function formatTimeAbsolute(timestamp: string | null | undefined): string {
		if (!timestamp) return 'Never';
		const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(timestamp);
		const normalized = hasTimezone ? timestamp : `${timestamp}Z`;
		return new Date(normalized).toLocaleString();
	}

	function getStatusColor(availability: string): string {
		return availability === 'Up' ? 'text-green-600' : 'text-red-600';
	}

	onMount(() => {
		if (!browser) return;
		window.addEventListener('click', _handler);
		return () => {
			window.removeEventListener('click', _handler);
		};
	});
</script>

<main class="flex-1 overflow-auto p-12">
	<div class="mb-8">
		<div class="mb-6 flex items-start justify-between">
			<h1 class="text-4xl font-bold">{service.service_name}</h1>
			<div class="relative flex items-start gap-4">
				<button
					class="rounded-xl bg-blue-500 px-6 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
					on:click={runCheck}
					disabled={isLoading || isPageLoading}
				>
					{isLoading ? 'Checking...' : 'Check'}
				</button>

				<!-- three-dot menu container -->
				<div class="relative">
					<button
						bind:this={menuButtonRef}
						on:click|stopPropagation={toggleMenu}
						disabled={isLoading || isPageLoading}
						class="px-2 py-1 text-gray-500 hover:text-gray-700">⋮</button
					>

					{#if showMenu}
						<div
							bind:this={menuRef}
							class="absolute right-0 z-50 mt-2 w-40 rounded border bg-white shadow"
						>
							<button on:click={openEdit} class="block w-full px-4 py-2 text-left hover:bg-gray-100"
								>Edit</button
							>
							<button
								on:click={confirmDelete}
								class="block w-full px-4 py-2 text-left text-red-600 hover:bg-gray-100"
								>Delete</button
							>
						</div>
					{/if}
				</div>
			</div>
		</div>

		{#if error}
			<div class="mb-4 rounded bg-red-100 p-4 text-red-700">
				{error}
			</div>
		{/if}

		<div class={`relative grid grid-cols-2 gap-8 ${isPageLoading ? 'opacity-60' : ''}`}>
			<!-- Left Column -->
			<div>
				<!-- Health Status -->
				{#if showConfirm}
					<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
						<div class="w-full max-w-sm rounded bg-white p-8 shadow-lg">
							<h2 class="mb-4 text-xl font-bold">Confirm to Delete?</h2>
							<p class="mb-6 text-sm text-gray-600">This action cannot be undone.</p>
							<div class="flex justify-end gap-4">
								<button class="rounded bg-gray-200 px-4 py-2" on:click={cancelDelete}>Cancel</button
								>
								<button class="rounded bg-red-500 px-4 py-2 text-white" on:click={doDelete}
									>Delete</button
								>
							</div>
						</div>
					</div>
				{/if}

				<div class="mb-8">
					<p class="mb-2 text-2xl font-semibold">
						<span class={getStatusColor(healthData.availability)}>●</span>
						{healthData.availability}
					</p>
					<p class="text-lg font-bold">
						{typeof healthData.overall_score === 'number'
							? healthData.overall_score.toFixed(2)
							: 'N/A'}%
					</p>
					<button
						type="button"
						class="text-left text-sm text-gray-600 hover:text-gray-800"
						on:click={() => (showLastCheckRelative = !showLastCheckRelative)}
						disabled={isLoading || isPageLoading}
						title="Toggle last check format"
					>
						Last Check: {showLastCheckRelative
							? formatTime(healthData.checked_at)
							: formatTimeAbsolute(healthData.checked_at)}
					</button>
					<p class="text-sm text-gray-600">Events: {events.length}</p>
					<input
						type="text"
						placeholder={service.service_url}
						class="mt-4 w-full rounded bg-gray-300 px-4 py-2"
						disabled
					/>
					<p class="mt-2 text-sm text-gray-600">
						Monitoring Method: {service.check_type === 'url'
							? 'URL-based'
							: service.check_type === 'url_metrics'
								? 'URL with Metrics'
								: 'Loading...'}
					</p>
				</div>

				<!-- Health Narrative (Events) -->
				<div class="mb-8">
					<h2 class="mb-4 text-2xl font-bold">Health Events</h2>
					<div class="max-h-96 space-y-4 overflow-y-auto rounded bg-gray-200 p-6">
						{#if events.length === 0}
							<p class="text-sm text-gray-600">No events recorded yet.</p>
						{:else}
							{#each events as event}
								<div>
									<p class="text-sm font-semibold">
										[{event.event_level}] {formatTime(event.detected_at)}
									</p>
									<p class="text-sm text-gray-700">{event.event_message}</p>
								</div>
							{/each}
						{/if}
					</div>
				</div>
			</div>

			<!-- Right Column -->
			<div>
				<!-- Health Summary -->
				<div class="mb-8">
					<h2 class="mb-4 text-2xl font-bold">Health Summary</h2>
					<div class="space-y-2 bg-gray-100 p-4">
						<p class="text-sm">
							<strong>Availability:</strong>
							<span class={getStatusColor(healthData.availability)}>{healthData.availability}</span>
						</p>
						<p class="text-sm">
							<strong>Responsiveness:</strong>
							{healthData.responsiveness || '-'}
						</p>
						<p class="text-sm"><strong>Reliability:</strong> {healthData.reliability || '-'}</p>
						<p class="text-sm">
							<strong>Overall Score:</strong>
							{typeof healthData.overall_score === 'number'
								? healthData.overall_score.toFixed(2)
								: '-'}%
						</p>
					</div>
				</div>

				<!-- Details -->
				<div>
					<h2 class="mb-4 text-2xl font-bold">Monitoring Details</h2>
					<div class="space-y-2 bg-gray-100 p-4 text-sm">
						<p><strong>HTTP Status:</strong> {healthData.http_status || '-'}</p>
						<p>
							<strong>Latency:</strong>
							{typeof healthData.latency_ms === 'number' ? healthData.latency_ms.toFixed(2) : '-'} ms
						</p>
						<p>
							<strong>Service URL:</strong>
							<span class="break-all text-blue-600">{service.service_url}</span>
						</p>
						<p><strong>Check Type:</strong> {service.check_type}</p>
						<p>
							<strong>Created:</strong>
							{new Date(service.created_at).toLocaleString() || 'Loading...'}
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</main>
