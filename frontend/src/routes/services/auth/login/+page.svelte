<script lang="ts">
  let email = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin(e: Event) {
    e.preventDefault();
    loading = true;
    error = '';

    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok) {
      window.location.href = '/';
    } else {
      error = data.detail || 'Login failed';
    }

    loading = false;
  }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
  <div class="bg-white p-12 rounded-lg shadow-lg max-w-md w-full">
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold mb-2">Ayser</h1>
      <p class="text-gray-600">Website & Service Health Advisor</p>
    </div>

    {#if error}
      <div class="mb-4 text-red-700 bg-red-100 p-3 rounded">{error}</div>
    {/if}

    <form on:submit={handleLogin}>
      <div class="mb-6">
        <label class="block text-sm font-semibold mb-2">Email</label>
        <input 
          name="email"
          type="email" 
          placeholder="Enter your email"
          class="w-full px-4 py-2 border border-gray-300 rounded bg-gray-200"
          bind:value={email}
          required
        />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-semibold mb-2">Password</label>
        <input 
          name="password"
          type="password" 
          placeholder="Enter your password"
          class="w-full px-4 py-2 border border-gray-300 rounded bg-gray-200"
          bind:value={password}
          required
        />
      </div>

      <button 
        type="submit"
        class="w-full px-6 py-2 bg-white border border-gray-400 hover:bg-gray-100 rounded text-sm font-semibold mb-4"
        disabled={loading}
      >
        {#if loading}Logging in...{:else}Login{/if}
      </button>
    </form>

    <a href="/services/auth/register" class="block w-full px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold text-center">
      To Register
    </a>
  </div>
</div>
