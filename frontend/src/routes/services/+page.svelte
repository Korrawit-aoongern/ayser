<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import type { PageData } from './$types';

	let services: any[] = [
		{
			name: 'Loading...',
			url: 'Loading...',
			status: 'Loading...',
			lastCheck: 'Loading...'
		}
	]; // start empty
	let showLastCheckRelative = true;
	let loading = true;
	let error = '';

	let openMenuId: number | null = null;
	let confirmDeleteId: number | null = null;
	let menuRefs: Record<number, HTMLElement | null> = {};
	let menuButtonRefs: Record<number, HTMLElement | null> = {};
	let checkingIds = new Set<number>();

	function getStatusColor(status: string): string {
    	return status === 'Running' ? 'text-green-600' : status === 'Down' ? 'text-red-600' : 'text-gray-600';
  	}

	function toggleMenu(serviceId: number) {
		openMenuId = openMenuId === serviceId ? null : serviceId;
	}

	function openEdit(serviceId: number) {
		openMenuId = null;
		goto(`/services/details/edit?id=${serviceId}`);
	}

	function confirmDelete(serviceId: number) {
		openMenuId = null;
		setTimeout(() => (confirmDeleteId = serviceId), 100);
	}

	function cancelDelete() {
		confirmDeleteId = null;
	}

	function doDelete() {
		services = services.filter((s: any) => s.id !== confirmDeleteId);
		confirmDeleteId = null;
	}

	function formatLastCheck(checkedAt: string | null | undefined) {
		if (!checkedAt) return 'Never';
		const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(checkedAt);
		const normalized = hasTimezone ? checkedAt : `${checkedAt}Z`;
		return new Date(normalized).toLocaleString();
	}

	function recomputeLastChecks() {
		services = services.map((s: any) => ({
			...s,
			lastCheck: showLastCheckRelative
				? formatLastCheckRelative(s.checked_at)
				: formatLastCheck(s.checked_at)
		}));
	}

	function formatLastCheckRelative(checkedAt: string | null | undefined) {
		if (!checkedAt) return 'Never';
		const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(checkedAt);
		const normalized = hasTimezone ? checkedAt : `${checkedAt}Z`;
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

	function availabilityToStatus(availability: string | null | undefined) {
		return availability === 'Up' ? 'Running' : availability === 'Down' ? 'Down' : 'Unknown';
	}

	async function runCheck(serviceId: number) {
		if (checkingIds.has(serviceId)) return;
		checkingIds = new Set(checkingIds).add(serviceId);
		try {
			const res = await fetch(`/api/health/services/${serviceId}/check`, {
				method: 'POST',
				credentials: 'include'
			});

			if (!res.ok) throw new Error(`Health check failed (${res.status})`);

			const checkResult = await res.json();
			services = services.map((s: any) =>
				s.id === serviceId
					? {
							...s,
							checked_at: checkResult.checked_at,
							status: availabilityToStatus(checkResult.availability),
							lastCheck: showLastCheckRelative
								? formatLastCheckRelative(checkResult.checked_at)
								: formatLastCheck(checkResult.checked_at)
						}
					: s
			);
		} catch (e: any) {
			error = e.message;
		} finally {
			const next = new Set(checkingIds);
			next.delete(serviceId);
			checkingIds = next;
		}
	}

	let _handler: ((e: MouseEvent) => void) | null = null;

	if (browser) {
		_handler = (e: MouseEvent) => {
			const target = e.target as Node | null;
			if (openMenuId !== null) {
				const menuRef = menuRefs[openMenuId];
				const menuButtonRef = menuButtonRefs[openMenuId];
				if (
					menuRef &&
					menuButtonRef &&
					target &&
					!menuRef.contains(target) &&
					!menuButtonRef.contains(target)
				) {
					openMenuId = null;
				}
			}
		};
	}

	onMount(() => {
		(async () => {
			try {
				const res = await fetch('/api/services', {
					method: 'GET',
					credentials: 'include',
					headers: {
						'Content-Type': 'application/json'
					}
				});

				if (res.status === 401) {
					alert('Session expired. Please log in again.');
					return;
				}

				if (!res.ok) throw new Error(`HTTP error: ${res.status}`);

				const data = await res.json();

				services = data.map((s: any) => ({
					id: s.service_id,
					name: s.service_name || '',
					url: s.service_url || '',
					checked_at: s.checked_at,
					status: availabilityToStatus(s.availability),
					lastCheck: showLastCheckRelative
						? formatLastCheckRelative(s.checked_at)
						: formatLastCheck(s.checked_at)
				}));
			} catch (e: any) {
				error = e.message;
			} finally {
				loading = false;
			}
		})();

		return () => {
			if (_handler) window.removeEventListener('click', _handler);
		};
	});
</script>

<main class="flex-1 p-12">
	<h1 class="mb-8 text-4xl font-bold">ALL Services</h1>

	<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each services as service}
			<div class="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-lg">
				<div class="relative mb-4 flex items-start justify-between">
					<a href={`/services/details?id=${service.id}`}>
						<h3 class="text-lg font-bold">{service.name}</h3>
					</a>

					<div class="relative">
						<button
							bind:this={menuButtonRefs[service.id]}
							on:click|stopPropagation={() => toggleMenu(service.id)}
							class="px-2 py-1 text-gray-500 hover:text-gray-700"
						>
							⋮
						</button>
						{#if openMenuId === service.id}
							<div
								bind:this={menuRefs[service.id]}
								class="absolute right-0 z-50 mt-2 w-40 rounded border bg-white shadow"
							>
								<button
									on:click={() => openEdit(service.id)}
									class="block w-full px-4 py-2 text-left hover:bg-gray-100"
								>
									Edit
								</button>
								<button
									on:click={() => confirmDelete(service.id)}
									class="block w-full px-4 py-2 text-left text-red-600 hover:bg-gray-100"
								>
									Delete
								</button>
							</div>
						{/if}
					</div>
				</div>

				<p class={`mb-2 text-sm ${getStatusColor(service.status)}`}>● {service.status}</p>
				<a href={service.url}>
					<p class="mb-4 text-sm text-gray-600">{service.url}</p>
				</a>
				<button
					type="button"
					class="text-left text-xs text-gray-500 hover:text-gray-700"
					on:click={() => {
						showLastCheckRelative = !showLastCheckRelative;
						recomputeLastChecks();
					}}
					title="Toggle last check format"
				>
					Last Check: {service.lastCheck}
				</button>
				<button
					class="mt-4 w-full rounded-xl bg-gray-300 px-6 py-2 hover:bg-gray-400 disabled:opacity-50"
					on:click={() => runCheck(service.id)}
					disabled={checkingIds.has(service.id)}
				>
					{checkingIds.has(service.id) ? 'Checking...' : 'Check'}
				</button>
			</div>
		{/each}
	</div>

	{#if confirmDeleteId !== null}
		<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
			<div class="w-full max-w-sm rounded bg-white p-8 shadow-lg">
				<h2 class="mb-4 text-xl font-bold">Confirm to Delete?</h2>
				<p class="mb-6 text-sm text-gray-600">This action cannot be undone.</p>
				<div class="flex justify-end gap-4">
					<button class="rounded bg-gray-200 px-4 py-2" on:click={cancelDelete}>Cancel</button>
					<button class="rounded bg-red-500 px-4 py-2 text-white" on:click={doDelete}>Delete</button
					>
				</div>
			</div>
		</div>
	{/if}
</main>
