<script>
  let registerData = {
    username: '',
    email: '',
    password: '',
  };

  function handleRegister() {
    console.log('Registering:', registerData);
    // Add registration logic here
  }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
  <div class="bg-white p-12 rounded-lg shadow-lg max-w-md w-full">
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold mb-2">Ayser</h1>
      <p class="text-gray-600">Website & Service Health Advisor</p>
    </div>

    <form on:submit|preventDefault={handleRegister}>
      <div class="mb-6">
        <label class="block text-sm font-semibold mb-2">Username</label>
        <input 
          type="text" 
          placeholder="Choose a username"
          class="w-full px-4 py-2 border border-gray-300 rounded bg-gray-200"
          bind:value={registerData.username}
          required
        />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-semibold mb-2">Email</label>
        <input 
          type="email" 
          placeholder="Enter your email"
          class="w-full px-4 py-2 border border-gray-300 rounded bg-gray-200"
          bind:value={registerData.email}
          required
        />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-semibold mb-2">Password</label>
        <input 
          type="password" 
          placeholder="Create a password"
          class="w-full px-4 py-2 border border-gray-300 rounded bg-gray-200"
          bind:value={registerData.password}
          required
        />
      </div>

      <button 
        type="submit"
        class="w-full px-6 py-2 bg-white border border-gray-400 hover:bg-gray-100 rounded text-sm font-semibold mb-4"
      >
        Register
      </button>
    </form>

    <a href="/services/auth/login" class="block w-full px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold text-center">
      To Login
    </a>
  </div>
</div>
