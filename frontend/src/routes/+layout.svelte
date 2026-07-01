<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { page } from '$app/stores';
  import favicon from "$lib/assets/favicon.svg";
  import "../app.css";
  import { theme } from '$lib/stores/theme';
  import SplashScreen from '$lib/components/SplashScreen.svelte';

  let { children } = $props();
  let showSplash = $state(true);

  const unsubscribeTheme = theme.subscribe((value) => {
    if (!browser) return;
    document.documentElement.classList.toggle('dark', value === 'dark');
    document.documentElement.classList.toggle('light', value === 'light');
  });

  onDestroy(() => {
    unsubscribeTheme();
  });

  onMount(() => {
    // Check if splash screen has already been shown
    const splashShown = sessionStorage.getItem('splashShown');
    if (splashShown) {
      showSplash = false;
    }
  });

  function handleSplashComplete() {
    sessionStorage.setItem('splashShown', 'true');
    showSplash = false;
  }
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

{#if showSplash}
  <SplashScreen onComplete={handleSplashComplete} />
{:else}
  <div class="circular-container">
    {@render children()}
  </div>
{/if}
