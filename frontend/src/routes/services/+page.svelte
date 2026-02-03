<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  let services = [
    { id: 1, name: 'Service 1', url: 'https://example.com', status: 'Running', lastCheck: '12 minutes ago' },
    { id: 2, name: 'Service 2', url: 'https://example.com', status: 'Running', lastCheck: '12 minutes ago' },
    { id: 3, name: 'Service 3', url: 'https://example.com', status: 'Running', lastCheck: '5 minutes ago' },
    { id: 4, name: 'Service 4', url: 'https://example.com', status: 'Starting', lastCheck: '12 minutes ago' },
    { id: 5, name: 'Service 5', url: 'https://example.com', status: 'Unknown', lastCheck: '12 minutes ago' },
  ];

  let openMenuId: number | null = null;
  let confirmDeleteId: number | null = null;
  let menuRefs: Record<number, HTMLElement | null> = {};
  let menuButtonRefs: Record<number, HTMLElement | null> = {};

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
    services = services.filter(s => s.id !== confirmDeleteId);
    confirmDeleteId = null;
  }

  let _handler: ((e: MouseEvent) => void) | null = null;

  if (browser) {
    _handler = (e: MouseEvent) => {
      const target = e.target as Node | null;
      if (openMenuId !== null) {
        const menuRef = menuRefs[openMenuId];
        const menuButtonRef = menuButtonRefs[openMenuId];
        if (menuRef && menuButtonRef && target && !menuRef.contains(target) && !menuButtonRef.contains(target)) {
          openMenuId = null;
        }
      }
    };
  }

  onMount(() => {
    if (_handler && browser) {
      window.addEventListener('click', _handler);
      return () => window.removeEventListener('click', _handler);
    }
  });
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">ALL Services</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each services as service}
      <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
        <div class="flex justify-between items-start mb-4 relative">
          <a href={`/services/details?id=${service.id}`}>
            <h3 class="text-lg font-bold">{service.name}</h3>
          </a>
          
          <div class="relative">
            <button 
              bind:this={menuButtonRefs[service.id]} 
              on:click|stopPropagation={() => toggleMenu(service.id)} 
              class="text-gray-500 hover:text-gray-700 px-2 py-1"
            >
              ⋮
            </button>
            {#if openMenuId === service.id}
              <div 
                bind:this={menuRefs[service.id]} 
                class="absolute right-0 mt-2 w-40 bg-white border rounded shadow z-50"
              >
                <button 
                  on:click={() => openEdit(service.id)} 
                  class="block w-full text-left px-4 py-2 hover:bg-gray-100"
                >
                  Edit
                </button>
                <button 
                  on:click={() => confirmDelete(service.id)} 
                  class="block w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600"
                >
                  Delete
                </button>
              </div>
            {/if}
          </div>
        </div>

        <p class="text-sm text-gray-600 mb-2">● {service.status}</p>
        <a href="{service.url}">
          <p class="text-sm text-gray-600 mb-4">{service.url}</p>
        </a>
        <p class="text-xs text-gray-500">Last Check: {service.lastCheck}</p>
        <button class="px-6 py-2 mt-4 w-full bg-gray-300 hover:bg-gray-400 rounded-xl">Check</button>
      </div>
    {/each}
  </div>

  {#if confirmDeleteId !== null}
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
</main>
