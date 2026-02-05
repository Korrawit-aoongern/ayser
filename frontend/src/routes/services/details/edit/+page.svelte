<script lang="ts">
  import { page } from '$app/stores';

  let formData = {
    serviceName: '',
    url: '',
    advancedMethod: 'None',
    metricsEndpoint: '',
  };

  let advancedMethods = [
    'None',
    'Metrics endpoint'
  ];

  // Load service data based on ID
  $: if ($page.url.searchParams.get('id')) {
    const serviceId = parseInt($page.url.searchParams.get('id') || '1');
    loadService(serviceId);
  }

  function loadService(id: number) {
    // Mock data - in real app, fetch from API
    const serviceData: Record<number, any> = {
      1: {
        serviceName: 'Service 1',
        url: 'https://example.com',
        advancedMethod: 'None',
        metricsEndpoint: '',
      },
      2: {
        serviceName: 'Service 2 Healths',
        url: 'https://service2.example.com',
        advancedMethod: 'Metrics endpoint',
        metricsEndpoint: '/metrics',
      },
    };

    const data = serviceData[id];
    if (data) {
      formData = { ...data };
    }
  }

  function handleSave() {
    console.log('Saving service:', formData);
    // Add save logic here
  }
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">Edit Service</h1>
  
  <form class="max-w-2xl" on:submit|preventDefault={handleSave}>
    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Service Name</label>
      <input 
        type="text" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={formData.serviceName}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">URL</label>
      <input 
        type="text" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={formData.url}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Advanced Methods</label>
      <select class="w-full px-4 py-2 border border-gray-300 rounded bg-white" bind:value={formData.advancedMethod}>
        {#each advancedMethods as method}
          <option value={method}>{method}</option>
        {/each}
      </select>
    </div>

    {#if formData.advancedMethod === 'Metrics endpoint'}
    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">/metrics endpoint</label>
      <input 
        type="text" 
        placeholder="Enter your /metrics endpoint URL (ex. /metrics)" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={formData.metricsEndpoint}
      />
    </div>
    {/if}

    <button 
      type="submit"
      class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold"
    >
      Save
    </button>
  </form>
</main>
