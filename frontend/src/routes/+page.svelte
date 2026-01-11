<script lang="ts">
  let backendStatus = "loading...";

  async function loadHealth() {
    const res = await fetch("http://localhost:8000/health");
    const data = await res.json();
    backendStatus = data.status;
  }

  loadHealth();
</script>

<h1>Ayser</h1>
<p>Backend status: {backendStatus}</p>
