<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let loading = true;
  let savingProfile = false;
  let changingPassword = false;
  let deletingServices = false;
  let showDeleteServicesModal = false;
  let deletingUser = false;
  let showDeleteUserModal = false;

  let profileMessage = '';
  let passwordMessage = '';
  let serviceMessage = '';
  let userDeleteMessage = '';
  let error = '';

  let userData = {
    username: '',
    email: '',
    oldPassword: '',
    newPassword: '',
    retypePassword: ''
  };

  async function loadUser() {
    loading = true;
    error = '';
    try {
      const res = await fetch('/api/user', {
        method: 'GET',
        credentials: 'include'
      });

      if (res.status === 401) {
        await goto('/services/auth/login');
        return;
      }

      if (!res.ok) throw new Error(`Failed to load user (${res.status})`);

      const data = await res.json();
      userData.username = data.username ?? '';
      userData.email = data.email ?? '';
    } catch (e) {
      error = (e as Error).message;
    } finally {
      loading = false;
    }
  }

  async function handleSaveProfile() {
    savingProfile = true;
    profileMessage = '';
    error = '';
    try {
      const res = await fetch('/api/user', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: userData.username,
          email: userData.email
        })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Failed to save profile (${res.status})`);

      profileMessage = 'Profile updated successfully.';
      window.dispatchEvent(new Event('user:changed'));
    } catch (e) {
      error = (e as Error).message;
    } finally {
      savingProfile = false;
    }
  }

  async function handleChangePassword() {
    passwordMessage = '';
    error = '';

    if (!userData.oldPassword || !userData.newPassword || !userData.retypePassword) {
      error = 'Please fill all password fields.';
      return;
    }

    if (userData.newPassword !== userData.retypePassword) {
      error = 'New password and retype password do not match.';
      return;
    }

    changingPassword = true;
    try {
      const res = await fetch('/api/user/password', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          old_password: userData.oldPassword,
          new_password: userData.newPassword
        })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Failed to change password (${res.status})`);

      passwordMessage = 'Password changed successfully. You will be logged out.';
      userData.oldPassword = '';
      userData.newPassword = '';
      userData.retypePassword = '';

      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      alert('Password changed successfully. Please login again.');
      await goto('/services/auth/login');
    } catch (e) {
      error = (e as Error).message;
    } finally {
      changingPassword = false;
    }
  }

  function openDeleteServicesModal() {
    serviceMessage = '';
    showDeleteServicesModal = true;
  }

  function cancelDeleteServices() {
    showDeleteServicesModal = false;
  }

  async function handleDeleteAllServices() {
    deletingServices = true;
    serviceMessage = '';
    error = '';
    try {
      const res = await fetch('/api/services', {
        method: 'DELETE',
        credentials: 'include'
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Failed to delete all services (${res.status})`);

      showDeleteServicesModal = false;
      serviceMessage = `Deleted ${data.deleted_count ?? 0} service(s).`;
      window.dispatchEvent(new Event('services:changed'));
    } catch (e) {
      error = (e as Error).message;
    } finally {
      deletingServices = false;
    }
  }

  function openDeleteUserModal() {
    userDeleteMessage = '';
    showDeleteUserModal = true;
  }

  function cancelDeleteUser() {
    showDeleteUserModal = false;
  }

  async function handleDeleteUser() {
    deletingUser = true;
    error = '';
    try {
      const res = await fetch('/api/user', {
        method: 'DELETE',
        credentials: 'include'
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Failed to delete user (${res.status})`);

      showDeleteUserModal = false;
      userDeleteMessage = 'User deleted successfully. Redirecting to login...';
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      await goto('/services/auth/login');
    } catch (e) {
      error = (e as Error).message;
    } finally {
      deletingUser = false;
    }
  }

  onMount(loadUser);
</script>

<main class="flex-1 p-12">
  <h1 class="text-4xl font-bold mb-8">User</h1>

  {#if error}
    <div class="mb-4 rounded bg-red-100 p-3 text-red-700">{error}</div>
  {/if}
  
  <form class="max-w-2xl" on:submit|preventDefault={handleSaveProfile}>
    <div class="flex items-center gap-8 mb-8">
      <div class="w-24 h-24 bg-gray-400 rounded-full"></div>
      <div class="flex-1">
        <div class="mb-6">
          <label class="block text-sm font-semibold mb-2">Username</label>
          <input 
            type="text" 
            class="w-full px-4 py-2 border border-gray-300 rounded"
            bind:value={userData.username}
            disabled={loading || savingProfile}
          />
        </div>

        <div class="mb-6">
          <label class="block text-sm font-semibold mb-2">Email</label>
          <input 
            type="email" 
            class="w-full px-4 py-2 border border-gray-300 rounded"
            bind:value={userData.email}
            disabled={loading || savingProfile}
          />
        </div>
      </div>
    </div>

    {#if profileMessage}
      <p class="mb-4 text-sm text-green-700">{profileMessage}</p>
    {/if}

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Old Password</label>
      <input 
        type="password" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={userData.oldPassword}
        disabled={loading || changingPassword}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">New Password</label>
      <input 
        type="password" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={userData.newPassword}
        disabled={loading || changingPassword}
      />
    </div>

    <div class="mb-6">
      <label class="block text-sm font-semibold mb-2">Retype New Password</label>
      <input 
        type="password" 
        class="w-full px-4 py-2 border border-gray-300 rounded"
        bind:value={userData.retypePassword}
        disabled={loading || changingPassword}
      />
    </div>

    <div class="mb-8 flex gap-3">
      <button
        type="submit"
        class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold disabled:opacity-50"
        disabled={loading || savingProfile}
      >
        {savingProfile ? 'Saving...' : 'Save Profile'}
      </button>
      <button
        type="button"
        class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded text-sm font-semibold disabled:opacity-50"
        on:click={handleChangePassword}
        disabled={loading || changingPassword}
      >
        {changingPassword ? 'Changing...' : 'Change Password'}
      </button>
    </div>

    {#if passwordMessage}
      <p class="mb-4 text-sm text-green-700">{passwordMessage}</p>
    {/if}

    <div class="mt-8">
      <h2 class="text-2xl font-bold mb-4">Services</h2>
      {#if serviceMessage}
        <p class="mb-3 text-sm text-green-700">{serviceMessage}</p>
      {/if}
      <button
        type="button"
        class="px-6 py-2 text-red-500 border-red-500 border-2 hover:bg-red-500 hover:text-white rounded text-sm font-semibold inline-block disabled:opacity-50"
        on:click={openDeleteServicesModal}
        disabled={loading || deletingServices}
      >
        {deletingServices ? 'Deleting...' : 'Delete All Services'}
      </button>
    </div>

    <div class="mt-8">
      <h2 class="text-2xl font-bold mb-4">User</h2>
      {#if userDeleteMessage}
        <p class="mb-3 text-sm text-green-700">{userDeleteMessage}</p>
      {/if}
      <button
        type="button"
        class="px-6 py-2 text-red-500 border-red-500 border-2 hover:bg-red-500 hover:text-white rounded text-sm font-semibold inline-block disabled:opacity-50"
        on:click={openDeleteUserModal}
        disabled={deletingUser}
      >
        {deletingUser ? 'Deleting...' : 'Delete User'}
      </button>
    </div>
  </form>

  {#if showDeleteServicesModal}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-sm rounded bg-white p-8 shadow-lg">
        <h2 class="mb-4 text-xl font-bold">Delete all services?</h2>
        <p class="mb-6 text-sm text-gray-600">Are you sure? This action cannot be undone.</p>
        <div class="flex justify-end gap-4">
          <button
            type="button"
            class="rounded bg-gray-200 px-4 py-2"
            on:click={cancelDeleteServices}
            disabled={deletingServices}
          >
            Cancel
          </button>
          <button
            type="button"
            class="rounded bg-red-500 px-4 py-2 text-white disabled:opacity-50"
            on:click={handleDeleteAllServices}
            disabled={deletingServices}
          >
            {deletingServices ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  {/if}

  {#if showDeleteUserModal}
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="w-full max-w-sm rounded bg-white p-8 shadow-lg">
        <h2 class="mb-4 text-xl font-bold">Delete user?</h2>
        <p class="mb-6 text-sm text-gray-600">Are you sure? This action cannot be undone.</p>
        <div class="flex justify-end gap-4">
          <button
            type="button"
            class="rounded bg-gray-200 px-4 py-2"
            on:click={cancelDeleteUser}
            disabled={deletingUser}
          >
            Cancel
          </button>
          <button
            type="button"
            class="rounded bg-red-500 px-4 py-2 text-white disabled:opacity-50"
            on:click={handleDeleteUser}
            disabled={deletingUser}
          >
            {deletingUser ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  {/if}
</main>
