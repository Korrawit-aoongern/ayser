<script lang="ts">
	import '../../layout.css';

	let { children } = $props();
</script>

<div class="min-h-screen bg-gray-100">
	{@render children()}
</div>
