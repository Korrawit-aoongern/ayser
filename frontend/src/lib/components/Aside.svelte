<script lang="ts">
	import { page } from '$app/stores';
    import AyserIcon from '../assets/Ayser-Icon.png';
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
			<a
				href="/services/details"
				class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page.url
					.pathname === '/services/details'
					? 'bg-gray-400 font-bold'
					: ''}"
			>
				Service 1
			</a>
			<a
				href="/services/details"
				class="block w-full rounded-xl px-4 py-3 text-sm text-center bg-gray-300 hover:bg-gray-400 {$page.url
					.pathname === '/services/details'
					? 'bg-gray-400 font-bold'
					: ''}"
			>
				Service 2
			</a>
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
					Username
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
