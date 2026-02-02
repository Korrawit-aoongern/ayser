<script lang="ts">
  import { page } from '$app/stores';
</script>

<!-- Left Sidebar -->
<aside class="w-64 bg-gray-200 flex flex-col">
  <!-- Service Section -->
  <div class="flex-1">
    <div class="bg-green-300 p-4">
      <h2 class="text-sm font-medium text-gray-700">Service</h2>
    </div>
    
    <nav class="p-4 space-y-2">
      <a href="/services" class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-300 rounded {$page.url.pathname === '/services' ? 'bg-gray-300 font-bold' : ''}">
        All Services
      </a>
      <a href="/services/details" class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-300 rounded {$page.url.pathname === '/services/details' ? 'bg-gray-300 font-bold' : ''}">
        Service 1
      </a>
      <a href="/services/details" class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-300 rounded {$page.url.pathname === '/services/details' ? 'bg-gray-300 font-bold' : ''}">
        Service 2
      </a>
      <a href="/services/new" class="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-300 rounded {$page.url.pathname === '/services/new' ? 'bg-gray-300 font-bold' : ''}">
        + New Service
      </a>
    </nav>
  </div>

  <!-- Account Section (Bottom) -->
  <div class="border-t border-gray-300">
    <div class="p-4">
      <h3 class="text-xs text-gray-600 mb-3">Account</h3>
      <div class="space-y-2">
        <a href="/user" class="block w-full text-left px-4 py-2 text-sm bg-gray-300 rounded flex items-center {$page.url.pathname === '/user' ? 'font-bold' : ''}">
          <span class="w-6 h-6 bg-gray-400 rounded-full mr-2"></span>
          Username
        </a>
        <a href="/doc" class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-300 rounded {$page.url.pathname === '/doc' ? 'bg-gray-300 font-bold' : ''}">
          Document
        </a>
        <a href="/services/auth/login" class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-300 rounded">
          Logout
        </a>
      </div>
    </div>
  </div>
</aside>

<style>
  /* Additional custom styles if needed */
</style>