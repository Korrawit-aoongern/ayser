<main class="flex-1 overflow-auto p-12">
	<div class="mx-auto max-w-5xl">
		<h1 class="mb-2 text-4xl font-bold">How to Use Ayser</h1>
		<p class="mb-8 text-gray-700">
			Ayser monitors service health, scrapes metrics, and logs human-readable events for operations.
		</p>

		<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-2xl font-bold">1. Create a Service</h2>
			<ol class="list-inside list-decimal space-y-2 text-gray-700">
				<li>Open <strong>+ New Service</strong>.</li>
				<li>Enter <strong>Service Name</strong> and <strong>URL</strong>.</li>
				<li>
					Choose monitoring mode:
					<ul class="mt-1 list-inside list-disc">
						<li><strong>None</strong>: URL-only blackbox checks.</li>
						<li><strong>Metrics endpoint</strong>: URL check + metrics scrape.</li>
					</ul>
				</li>
				<li>If using metrics mode, set endpoint like <code>/metrics</code>.</li>
			</ol>
		</div>

		<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-2xl font-bold">2. Run Monitoring Checks</h2>
			<ol class="list-inside list-decimal space-y-2 text-gray-700">
				<li>Open a service from the sidebar.</li>
				<li>Click <strong>Check</strong>.</li>
				<li>Ayser runs blackbox health check and optional metrics scrape.</li>
				<li>Health score, latency, and event list update automatically.</li>
			</ol>
		</div>

		<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-2xl font-bold">3. Read Service Status</h2>
			<ul class="list-inside list-disc space-y-2 text-gray-700">
				<li><strong>Availability</strong>: Up/Down reachability.</li>
				<li><strong>Responsiveness</strong>: latency category from health check.</li>
				<li><strong>Reliability</strong>: stability from recent checks.</li>
				<li><strong>Overall Score</strong>: combined health score.</li>
				<li>
					<strong>Metrics</strong>: CPU, memory, p50/p90/p99 latency, and error rate (if available from
					exporter).
				</li>
			</ul>
		</div>

		<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-2xl font-bold">4. Understand Events</h2>
			<p class="mb-3 text-gray-700">Event levels are color-coded in service details:</p>
			<ul class="list-inside list-disc space-y-2 text-gray-700">
				<li><strong>INFO</strong>: normal or low-confidence variation.</li>
				<li><strong>WARNING</strong>: moderate issue or degraded behavior.</li>
				<li><strong>ERROR</strong>: clear abnormal behavior or service degradation.</li>
			</ul>
			<p class="mt-4 text-gray-700">
				Some events are rule-based (threshold checks). Some are ML-driven and may include LLM-generated
				explanations.
			</p>
		</div>

		<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-2xl font-bold">5. ML + LLM Behavior</h2>
			<ul class="list-inside list-disc space-y-2 text-gray-700">
				<li>ML runs per service on numeric metrics only.</li>
				<li>Low data points produce low-confidence outcomes (level may be downgraded).</li>
				<li>Gemini is used to generate short operational explanation messages on anomaly events.</li>
				<li>If LLM is unavailable, Ayser falls back to a deterministic message template.</li>
			</ul>
		</div>

		<div class="mb-8 rounded-lg border border-gray-200 bg-white p-6">
			<h2 class="mb-4 text-2xl font-bold">6. Quick Troubleshooting</h2>
			<ul class="list-inside list-disc space-y-2 text-gray-700">
				<li>
					<strong>Metrics show "-"</strong>: exporter may not expose recognized metric names yet. Run more
					checks and verify endpoint output.
				</li>
				<li><strong>No ML events yet</strong>: collect more metric points and rerun checks.</li>
				<li><strong>No LLM explanation</strong>: verify backend env has valid Gemini key/model.</li>
				<li><strong>Service URL</strong> in details is clickable for direct verification.</li>
			</ul>
		</div>
	</div>
</main>
