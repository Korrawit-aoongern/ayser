<script>
  let userData = {
    username: 'John Doe',
    email: 'john@example.com',
    oldPassword: '',
    newPassword: '',
    retypePassword: '',
  };

  function handleSave() {
    console.log('Saving user data:', userData);
    // Add save logic here
  }
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">User</h1>
  
  <form class="max-w-2xl" on:submit|preventDefault={handleSave}>
    <div class="flex items-center gap-8 mb-8">
      <div class="w-24 h-24 bg-gray-400 rounded-full"></div>
      <div class="flex-1">
        <div class="mb-6">
          <label class="block text-sm font-semibold mb-2">Username</label>
          <input 
            type="text" 
            class="w-full px-4 py-2 border border-gray-300 rounded"
            bind:value={userData.username}
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-semibold mb-2">Email</label>
          <input 
            type="email" 
            class="w-full px-4 py-2 border border-gray-300 rounded"
            bind:value={userData.email}
          />
        </div>
      </div>
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Old Password</label>
      <input 
        type="password" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={userData.oldPassword}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">New Password</label>
      <input 
        type="password" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={userData.newPassword}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Retype New Password</label>
      <input 
        type="password" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={userData.retypePassword}
      />
    </div>

    <button 
      type="submit"
      class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold mb-8"
    >
      Save
    </button>

    <div class="mt-8">
      <h2 class="text-2xl font-bold mb-4">Services</h2>
      <a href="/services" class="px-6 py-2 text-red-500 border-red-500 border-2 hover:bg-red-500 hover:text-white rounded text-sm font-semibold inline-block">
        Delete All Services
      </a>
    </div>
  </form>
</main>
