<script lang="ts">
  export let letters: string[];
  export let contrast: number;
</script>

<div class="card">
  <div class="letters" style="color: rgba(0, 0, 0, {contrast})">
    {#each letters as letter}
      <span class="letter">{letter}</span>
    {/each}
  </div>
</div>

<style>
.card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  border: 2px solid #e0e0e0;
}

.letters {
  display: flex;
  gap: 20px;
  font-size: 48px;
  font-weight: bold;
  font-family: sans-serif;
}

.letter {
  display: inline-block;
}
</style>
