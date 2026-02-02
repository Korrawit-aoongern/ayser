<script>
  let services = [
    { id: 1, name: 'Service 1', url: 'https://example.com', status: 'Running', lastCheck: '12 minutes ago' },
    { id: 2, name: 'Service 2', url: 'https://example.com', status: 'Running', lastCheck: '12 minutes ago' },
    { id: 3, name: 'Service 3', url: 'https://example.com', status: 'Running', lastCheck: '5 minutes ago' },
    { id: 4, name: 'Service 4', url: 'https://example.com', status: 'Starting', lastCheck: '12 minutes ago' },
    { id: 5, name: 'Service 5', url: 'https://example.com', status: 'Unknown', lastCheck: '12 minutes ago' },
  ];
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">ALL Services</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {#each services as service}
      <a href={`/services/details?id=${service.id}`} class="block">
        <div class="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-lg font-bold">{service.name}</h3>
            <button class="text-gray-500 hover:text-gray-700">⋮</button>
          </div>
          <p class="text-sm text-gray-600 mb-2">● {service.status}</p>
          <p class="text-sm text-gray-600 mb-4">{service.url}</p>
          <p class="text-xs text-gray-500">Last Check: {service.lastCheck}</p>
        </div>
      </a>
    {/each}
  </div>
</main>
