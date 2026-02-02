<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import Aside from '$lib/components/Aside.svelte';
	import { page } from '$app/stores';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

{#if $page.url.pathname.startsWith('/services/auth')}
	<!-- No sidebar for auth pages -->
	<div class="min-h-screen bg-gray-100">
		{@render children()}
	</div>
{:else}
	<!-- Sidebar for authenticated pages -->
	<div class="flex h-screen bg-gray-100">
		<Aside />

		<main class="flex-1 overflow-auto">
			{@render children()}
		</main>
	</div>
{/if}
