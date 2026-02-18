<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';

  let formData = {
    serviceName: '',
    url: '',
    advancedMethod: 'None',
    metricsEndpoint: ''
  };

  const advancedMethods = ['None', 'Metrics endpoint'];
  let loading = false;
  let error = '';

  function toCheckType(method: string) {
    return method === 'Metrics endpoint' ? 'url_metrics' : 'url';
  }

  async function handleCreate() {
    if (!browser) return;
    loading = true;
    error = '';
    try {
      const res = await fetch('/api/services', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_name: formData.serviceName,
          service_url: formData.url,
          check_type: toCheckType(formData.advancedMethod)
        })
      });

      if (res.status === 401) {
        await goto('/services/auth/login');
        return;
      }

      if (!res.ok) throw new Error(`Failed to create service (${res.status})`);

      const created = await res.json();
      window.dispatchEvent(new Event('services:changed'));
      await goto(`/services/details?id=${created.service_id}`);
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">New Service</h1>
  
  {#if error}
    <div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
  {/if}

  <form class="max-w-2xl" on:submit|preventDefault={handleCreate}>
    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Service Name</label>
      <input 
        type="text" 
        placeholder="Enter service name" 
        class="w-full px-4 py-2 border border-gray-300 rounded "
        bind:value={formData.serviceName}
        required
        disabled={loading}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">URL</label>
      <input 
        type="text" 
        placeholder="Enter service URL" 
        class="w-full px-4 py-2 border border-gray-300 rounded "
        bind:value={formData.url}
        required
        disabled={loading}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Advanced Methods</label>
      <select class="w-full px-4 py-2 border border-gray-300 rounded bg-white" bind:value={formData.advancedMethod} disabled={loading}>
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
        bind:value={formData.metricsEndpoint}
        disabled={loading}
      />
    </div>
    {/if}

    <button 
      type="submit"
      class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold disabled:opacity-50"
      disabled={loading}
    >
      {#if loading}Creating...{:else}Create{/if}
    </button>
  </form>
</main>
