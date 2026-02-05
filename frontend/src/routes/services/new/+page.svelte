<script>
  let formData = {
    serviceName: '',
    url: '',
    advancedMethod: 'None',
  };

  let advancedMethods = [
    'None',
    'Metrics endpoint',
  ];

  function handleCreate() {
    console.log('Creating service:', formData);
    // Add service creation logic here
  }
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">New Service</h1>
  
  <form class="max-w-2xl" on:submit|preventDefault={handleCreate}>
    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Service Name</label>
      <input 
        type="text" 
        placeholder="Enter service name" 
        class="w-full px-4 py-2 border border-gray-300 rounded "
        bind:value={formData.serviceName}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">URL</label>
      <input 
        type="text" 
        placeholder="Enter service URL" 
        class="w-full px-4 py-2 border border-gray-300 rounded "
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
    <div class="mb-6" >
      <label class="block text-sm font-semibold mb-2">/metrics endpoint</label>
      <input 
        type="text" 
        placeholder="Enter your /metrics endpoint URL (ex. /metrics)" 
        class="w-full px-4 py-2 border border-gray-300 rounded "
      />
    </div>
    {/if}

    <button 
      type="submit"
      class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold"
    >
      Create
    </button>
  </form>
</main>
