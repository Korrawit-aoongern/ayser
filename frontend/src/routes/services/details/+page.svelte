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
		metrics_endpoint: null as string | null,
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
		cpu: number | null;
		memory: number | null;
		p50: number | null;
		p90: number | null;
		p99: number | null;
		cpu_unit: string | null;
		memory_unit: string | null;
		p50_unit: string | null;
		p90_unit: string | null;
		p99_unit: string | null;
	} = {
		health_id: null,
		service_id: 0,
		availability: 'Loading...',
		responsiveness: 'Loading...',
		reliability: 'Loading...',
		overall_score: null,
		latency_ms: null,
		http_status: null,
		checked_at: 'Loading...',
		cpu: null,
		memory: null,
		p50: null,
		p90: null,
		p99: null,
		cpu_unit: null,
		memory_unit: null,
		p50_unit: null,
		p90_unit: null,
		p99_unit: null
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
				metrics_endpoint: servicePayload.metrics_endpoint ?? null,
				created_at: servicePayload.created_at ?? new Date().toISOString()
			};

			const selectedMetrics = healthPayload.metrics ?? {};
			healthData = {
				health_id: healthPayload.health_id ?? null,
				service_id: healthPayload.service_id ?? id,
				availability: healthPayload.availability ?? 'Unknown',
				responsiveness: healthPayload.responsiveness ?? null,
				reliability: healthPayload.reliability ?? null,
				overall_score: healthPayload.overall_score ?? null,
				latency_ms: healthPayload.latency_ms ?? null,
				http_status: healthPayload.http_status ?? null,
				checked_at: healthPayload.checked_at ?? null,
				cpu: selectedMetrics.cpu ?? null,
				memory: selectedMetrics.memory ?? null,
				p50: selectedMetrics.p50 ?? null,
				p90: selectedMetrics.p90 ?? null,
				p99: selectedMetrics.p99 ?? null,
				cpu_unit: selectedMetrics.cpu_unit ?? null,
				memory_unit: selectedMetrics.memory_unit ?? null,
				p50_unit: selectedMetrics.p50_unit ?? null,
				p90_unit: selectedMetrics.p90_unit ?? null,
				p99_unit: selectedMetrics.p99_unit ?? null
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
			const res = await fetch(`/api/monitor/services/${serviceId}/check`, {
				method: 'POST',
				credentials: 'include'
			});

			if (!res.ok) throw new Error('Monitoring check failed');

			const monitorResult = await res.json();
			const checkResult = monitorResult?.blackbox ?? null;
			if (!checkResult) throw new Error('Monitoring check returned invalid response');

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
				checked_at: checkResult.checked_at,
				cpu: healthData.cpu,
				memory: healthData.memory,
				p50: healthData.p50,
				p90: healthData.p90,
				p99: healthData.p99,
				cpu_unit: healthData.cpu_unit,
				memory_unit: healthData.memory_unit,
				p50_unit: healthData.p50_unit,
				p90_unit: healthData.p90_unit,
				p99_unit: healthData.p99_unit
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

	function formatBytes(value: number | null): string {
		if (typeof value !== 'number') return '-';
		const units = ['B', 'KB', 'MB', 'GB', 'TB'];
		let size = value;
		let unitIndex = 0;
		while (size >= 1024 && unitIndex < units.length - 1) {
			size /= 1024;
			unitIndex++;
		}
		return `${size.toFixed(2)} ${units[unitIndex]}`;
	}

	function formatDurationSeconds(value: number | null): string {
		if (typeof value !== 'number') return '-';
		const totalSeconds = Math.floor(value);
		const days = Math.floor(totalSeconds / 86400);
		const hours = Math.floor((totalSeconds % 86400) / 3600);
		const minutes = Math.floor((totalSeconds % 3600) / 60);
		const seconds = totalSeconds % 60;
		if (days > 0) return `${days}d ${hours}h ${minutes}m`;
		if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
		if (minutes > 0) return `${minutes}m ${seconds}s`;
		return `${seconds}s`;
	}

	function formatMetric(value: number | null, unit: string | null): string {
		if (typeof value !== 'number') return '-';
		if (unit === 'bytes') return formatBytes(value);
		if (unit === 'seconds') return formatDurationSeconds(value);
		if (unit === 'ms') return `${value.toFixed(2)} ms`;
		if (unit === 'count') return `${Math.round(value).toLocaleString()}`;
		if (unit === '%') return `${value.toFixed(2)}%`;
		return `${value.toFixed(2)}${unit ? ` ${unit}` : ''}`;
	}

	const detailTooltips = {
		availability: 'Current reachability status from the latest health check.',
		responsiveness: 'Speed category based on response time thresholds.',
		reliability: 'Stability based on recent check history and uptime trend.',
		overallScore: 'Combined health score from availability, latency, and reliability.',
		httpStatus: 'Latest HTTP status returned by the monitored URL.',
		latency: 'Latest measured response time for the service URL.',
		serviceUrl: 'Base URL used for black-box health checks.',
		metricsEndpoint: 'Path or URL used to scrape Prometheus-style metrics.',
		checkType: 'Monitoring mode: URL-only or URL with metrics scraping.',
		cpuTime: 'Cumulative process CPU time exposed by metrics exporter.',
		memory: 'Latest memory metric value from exporter (formatted).',
		p50: '50th percentile latency from scraped metrics (typical latency).',
		p90: '90th percentile latency from scraped metrics (high latency bound).',
		p99: '99th percentile latency from scraped metrics (tail latency).',
		created: 'Timestamp when this service was created in Ayser.'
	};

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
							<strong
								title={detailTooltips.availability}
								class="cursor-help underline decoration-transparent">Availability:</strong
							>
							<span class={getStatusColor(healthData.availability)}>{healthData.availability}</span>
						</p>
						<p class="text-sm">
							<strong
								title={detailTooltips.responsiveness}
								class="cursor-help underline decoration-transparent">Responsiveness:</strong
							>
							{healthData.responsiveness || '-'}
						</p>
						<p class="text-sm">
							<strong
								title={detailTooltips.reliability}
								class="cursor-help underline decoration-transparent">Reliability:</strong
							>
							{healthData.reliability || '-'}
						</p>
						<p class="text-sm">
							<strong
								title={detailTooltips.overallScore}
								class="cursor-help underline decoration-transparent">Overall Score:</strong
							>
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
						<p>
							<strong
								title={detailTooltips.httpStatus}
								class="cursor-help underline decoration-transparent">HTTP Status:</strong
							>
							{healthData.http_status || '-'}
						</p>
						<p>
							<strong
								title={detailTooltips.latency}
								class="cursor-help underline decoration-transparent">Latency:</strong
							>
							{typeof healthData.latency_ms === 'number' ? healthData.latency_ms.toFixed(2) : '-'} ms
						</p>
						<p>
							<strong
								title={detailTooltips.serviceUrl}
								class="cursor-help underline decoration-transparent">Service URL:</strong
							>
							<span class="break-all text-blue-600">{service.service_url}</span>
						</p>
						<p>
							<strong
								title={detailTooltips.metricsEndpoint}
								class="cursor-help underline decoration-transparent">Metrics Endpoint:</strong
							>
							{service.metrics_endpoint && service.check_type === 'url_metrics'
								? service.metrics_endpoint
								: '-'}
						</p>
						<p>
							<strong
								title={detailTooltips.checkType}
								class="cursor-help underline decoration-transparent">Check Type:</strong
							>
							{service.check_type}
						</p>
						<p>
							<strong
								title={detailTooltips.cpuTime}
								class="cursor-help underline decoration-transparent">CPU Time:</strong
							>
							{formatMetric(healthData.cpu, healthData.cpu_unit)}
						</p>
						<p>
							<strong
								title={detailTooltips.memory}
								class="cursor-help underline decoration-transparent">Memory:</strong
							>
							{formatMetric(healthData.memory, healthData.memory_unit)}
						</p>
						<p>
							<strong
								title={detailTooltips.p50}
								class="cursor-help underline decoration-transparent">Latency p50:</strong
							>
							{formatMetric(healthData.p50, healthData.p50_unit)}
						</p>
						<p>
							<strong
								title={detailTooltips.p90}
								class="cursor-help underline decoration-transparent">Latency p90:</strong
							>
							{formatMetric(healthData.p90, healthData.p90_unit)}
						</p>
						<p>
							<strong
								title={detailTooltips.p99}
								class="cursor-help underline decoration-transparent">Latency p99:</strong
							>
							{formatMetric(healthData.p99, healthData.p99_unit)}
						</p>
						<p>
							<strong
								title={detailTooltips.created}
								class="cursor-help underline decoration-transparent">Created:</strong
							>
							{new Date(service.created_at).toLocaleString() || 'Loading...'}
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</main>
