<script lang="ts">
  import ShapeMemoryTest from '$lib/components/ShapeMemoryTest.svelte';
</script>

<div class="page-wrapper">
  <ShapeMemoryTest />
</div>

<style>
  .page-wrapper {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    min-height: 100vh;
    background: var(--bg);
    padding: 2rem;
  }
</style>
