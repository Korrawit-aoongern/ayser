<script>
  let service = {
    name: "Example Service",
    status: "Running",
    health: "96.45%",
    url: "https://example.com",
    lastCheck: "12 minutes ago",
    warnings: "3",
  };

  let narratives = [
    { type: 'INFO', time: '00:00', message: 'Service Started' },
    { type: 'WARNING', time: '01:20', message: 'Latency exceeded 500ms => "Users may experience slowness. Check upstream dependency or recent deploys"' },
    { type: 'ERROR', time: 'ERROR', message: '"Recommend to do something to fix the issue"' },
  ];

  let healthDetails = {
    availability: 'Up, Down',
    responsiveness: 'Fast / Slow',
    reliability: 'Stable / Flaky',
    cpu: '-',
    memory: '-',
    disk: '-',
    network: '-',
    errorRate: '-',
    requestCount: '1000',
    httpStatus: '200 OK',
    latency: '24ms',
  };
</script>

<main class="flex-1 p-12 overflow-auto">
  <div class="mb-8">
    <div class="flex justify-between items-start mb-6">
      <h1 class="text-4xl font-bold">[{service.name}] Health</h1>
      <div class="flex gap-4">
        <button class="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded">Check</button>
        <button class="text-gray-500 hover:text-gray-700">⋮</button>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-8">
      <!-- Left Column -->
      <div>
        <!-- Health Status -->
        <div class="mb-8">
          <p class="text-lg font-semibold mb-2">● {service.status}</p>
          <p class="text-lg font-bold">+ {service.health}</p>
          <p class="text-sm text-gray-600">Last Check: {service.lastCheck}</p>
          <p class="text-sm text-gray-600">Warnings in last 24h: {service.warnings}</p>
          <input type="text" placeholder="URL: {service.url}" class="mt-4 w-full px-4 py-2 bg-gray-300 rounded" disabled />
          <p class="text-sm text-gray-600 mt-2">Monitoring Method: URL-based</p>
        </div>

        <!-- Health Narrative -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold mb-4">Health Narrative</h2>
          <div class="bg-gray-200 p-6 rounded space-y-4">
            {#each narratives as narrative}
              <div>
                <p class="text-sm font-semibold">[{narrative.type}] {narrative.time}</p>
                <p class="text-sm text-gray-700">{narrative.message}</p>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div>
        <!-- Health Summary -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold mb-4">Health Summary</h2>
          <div class="bg-gray-100 p-4 space-y-2">
            <p class="text-sm"><strong>Availability:</strong> {healthDetails.availability}</p>
            <p class="text-sm"><strong>Responsiveness:</strong> {healthDetails.responsiveness}</p>
            <p class="text-sm"><strong>Reliability:</strong> {healthDetails.reliability}</p>
          </div>
        </div>

        <!-- Details -->
        <div>
          <h2 class="text-2xl font-bold mb-4">Details</h2>
          <div class="bg-gray-100 p-4 space-y-2 text-sm">
            <p><strong>CPU:</strong> {healthDetails.cpu}</p>
            <p><strong>Memory:</strong> {healthDetails.memory}</p>
            <p><strong>Disk:</strong> {healthDetails.disk}</p>
            <p><strong>Network:</strong> {healthDetails.network}</p>
            <p><strong>Error rate:</strong> {healthDetails.errorRate}</p>
            <p><strong>Request count:</strong> {healthDetails.requestCount}</p>
            <p><strong>HTTP status code:</strong> {healthDetails.httpStatus}</p>
            <p><strong>Latency:</strong> {healthDetails.latency}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</main>
