<script lang="ts">
	import ApiTest from '$lib/components/ApiTest.svelte';
	import { onMount } from 'svelte';

	let pageTitle = 'API Integration Test';

	onMount(() => {
		document.title = pageTitle;
	});
</script>

<svelte:head>
	<title>{pageTitle}</title>
	<meta name="description" content="Test API integration between SvelteKit frontend and FastAPI backend" />
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<div class="container mx-auto px-4 py-8">
		<div class="mb-8 text-center">
			<h1 class="text-4xl font-bold text-gray-900 mb-4">API Integration Test</h1>
			<p class="text-lg text-gray-600">
				Test the connection between SvelteKit frontend and FastAPI backend
			</p>
		</div>

		<ApiTest />
	</div>
</div>
