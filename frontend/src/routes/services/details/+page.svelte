<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount, onDestroy } from 'svelte';

  let service = {
    name: "Example Service",
    status: "Running",
    health: "96.45%",
    url: "https://example.com",
    lastCheck: "12 minutes ago",
    warnings: "3",
  };

  let narratives = [
    { type: 'INFO', time: '00:00', message: 'Service Started' },
    { type: 'WARNING', time: '01:20', message: 'Latency exceeded 500ms => "Users may experience slowness. Check upstream dependency or recent deploys"' },
    { type: 'ERROR', time: 'ERROR', message: '"Recommend to do something to fix the issue"' },
  ];

  let healthDetails = {
    availability: 'Up, Down',
    responsiveness: 'Fast / Slow',
    reliability: 'Stable / Flaky',
    cpu: '-',
    memory: '-',
    disk: '-',
    network: '-',
    errorRate: '-',
    requestCount: '1000',
    httpStatus: '200 OK',
    latency: '24ms',
  };

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
    goto('/services/details/edit');
  }

  function confirmDelete() {
    showMenu = false;
    // small delay to allow menu to close visually if needed
    setTimeout(() => (showConfirm = true), 100);
  }

  function cancelDelete() {
    showConfirm = false;
  }

  function doDelete() {
    showConfirm = false;
    // simulate deletion then go back to list
    goto('/services');
  }

  // click outside to close menu
  let _handler = (e: MouseEvent) => {
    const target = e.target as Node | null;
    if (showMenu && menuRef && menuButtonRef && target && !menuRef.contains(target) && !menuButtonRef.contains(target)) {
      showMenu = false;
    }
  };

  onMount(() => window.addEventListener('click', _handler));
  onDestroy(() => window.removeEventListener('click', _handler));
</script>

<main class="flex-1 p-12 overflow-auto">
  <div class="mb-8">
    <div class="flex justify-between items-start mb-6">
      <h1 class="text-4xl font-bold">[{service.name}] Health</h1>
      <div class="flex gap-4 items-start relative">
        <button class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded">Check</button>

        <!-- three-dot menu container -->
        <div class="relative">
          <button bind:this={menuButtonRef} on:click|stopPropagation={toggleMenu} class="text-gray-500 hover:text-gray-700 px-2 py-1">⋮</button>

          {#if showMenu}
            <div bind:this={menuRef} class="absolute right-0 mt-2 w-40 bg-white border rounded shadow z-50">
              <button on:click={openEdit} class="block w-full text-left px-4 py-2 hover:bg-gray-100">Edit</button>
              <button on:click={confirmDelete} class="block w-full text-left px-4 py-2 hover:bg-gray-100">Delete</button>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-8">
      <!-- Left Column -->
      <div>
        <!-- Health Status -->
      {#if showConfirm}
        <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div class="bg-white p-8 rounded shadow-lg max-w-sm w-full">
            <h2 class="text-xl font-bold mb-4">Confirm to Delete?</h2>
            <p class="text-sm text-gray-600 mb-6">This action cannot be undone.</p>
            <div class="flex justify-end gap-4">
              <button class="px-4 py-2 bg-gray-200 rounded" on:click={cancelDelete}>Cancel</button>
              <button class="px-4 py-2 bg-red-500 text-white rounded" on:click={doDelete}>Delete</button>
            </div>
          </div>
        </div>
      {/if}

        <div class="mb-8">
          <p class="text-2xl font-semibold mb-2">● {service.status}</p>
          <p class="text-lg font-bold">+ {service.health}</p>
          <p class="text-sm text-gray-600">Last Check: {service.lastCheck}</p>
          <p class="text-sm text-gray-600">Warnings in last 24h: {service.warnings}</p>
          <input type="text" placeholder="URL: {service.url}" class="mt-4 w-full px-4 py-2 bg-gray-300 rounded" disabled />
          <p class="text-sm text-gray-600 mt-2">Monitoring Method: URL-based</p>
        </div>

        <!-- Health Narrative -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold mb-4">Health Narrative</h2>
          <div class="bg-gray-200 p-6 rounded space-y-4">
            {#each narratives as narrative}
              <div>
                <p class="text-sm font-semibold">[{narrative.type}] {narrative.time}</p>
                <p class="text-sm text-gray-700">{narrative.message}</p>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div>
        <!-- Health Summary -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold mb-4">Health Summary</h2>
          <div class="bg-gray-100 p-4 space-y-2">
            <p class="text-sm"><strong>Availability:</strong> {healthDetails.availability}</p>
            <p class="text-sm"><strong>Responsiveness:</strong> {healthDetails.responsiveness}</p>
            <p class="text-sm"><strong>Reliability:</strong> {healthDetails.reliability}</p>
          </div>
        </div>

        <!-- Details -->
        <div>
          <h2 class="text-2xl font-bold mb-4">Details</h2>
          <div class="bg-gray-100 p-4 space-y-2 text-sm">
            <p><strong>CPU:</strong> {healthDetails.cpu}</p>
            <p><strong>Memory:</strong> {healthDetails.memory}</p>
            <p><strong>Disk:</strong> {healthDetails.disk}</p>
            <p><strong>Network:</strong> {healthDetails.network}</p>
            <p><strong>Error rate:</strong> {healthDetails.errorRate}</p>
            <p><strong>Request count:</strong> {healthDetails.requestCount}</p>
            <p><strong>HTTP status code:</strong> {healthDetails.httpStatus}</p>
            <p><strong>Latency:</strong> {healthDetails.latency}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</main>
