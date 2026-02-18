<script lang="ts">
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';

  let serviceId: number | null = null;
  let loading = false;
  let error = '';

  let formData = {
    serviceName: '',
    url: '',
    advancedMethod: 'None',
    metricsEndpoint: '',
  };

  const advancedMethods = ['None', 'Metrics endpoint'];

  function toAdvancedMethod(checkType: string | null | undefined) {
    return checkType === 'url_metrics' ? 'Metrics endpoint' : 'None';
  }

  function toCheckType(method: string) {
    return method === 'Metrics endpoint' ? 'url_metrics' : 'url';
  }

  // Load service data based on ID
  $: if (browser) {
    const rawId = $page.url.searchParams.get('id');
    if (!rawId) {
      error = 'Missing service id';
    } else {
      const parsedId = Number.parseInt(rawId, 10);
      if (Number.isNaN(parsedId)) {
        error = 'Invalid service id';
      } else if (parsedId !== serviceId) {
        serviceId = parsedId;
        error = '';
        loadService(parsedId);
      }
    }
  }

  async function loadService(id: number) {
    loading = true;
    try {
      const res = await fetch(`/api/services/${id}`, {
        credentials: 'include'
      });

      if (!res.ok) throw new Error(`Failed to load service (${res.status})`);

      const data = await res.json();
      formData = {
        serviceName: data.service_name ?? '',
        url: data.service_url ?? '',
        advancedMethod: toAdvancedMethod(data.check_type),
        metricsEndpoint: ''
      };
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }

  async function handleSave() {
    if (!serviceId) return;
    loading = true;
    error = '';
    try {
      const res = await fetch(`/api/services/${serviceId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_name: formData.serviceName,
          service_url: formData.url,
          check_type: toCheckType(formData.advancedMethod)
        })
      });

      if (!res.ok) throw new Error(`Failed to save service (${res.status})`);
      await res.json();
      window.dispatchEvent(new Event('services:changed'));
      await goto(`/services/details?id=${serviceId}`);
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">Edit Service</h1>
  
  {#if error}
    <div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
  {/if}

  <form class="max-w-2xl" on:submit|preventDefault={handleSave}>
    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Service Name</label>
      <input 
        type="text" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={formData.serviceName}
        disabled={loading}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">URL</label>
      <input 
        type="text" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={formData.url}
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
    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">/metrics endpoint</label>
      <input 
        type="text" 
        placeholder="Enter your /metrics endpoint URL (ex. /metrics)" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
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
      {#if loading}Saving...{:else}Save{/if}
    </button>
  </form>
</main>
