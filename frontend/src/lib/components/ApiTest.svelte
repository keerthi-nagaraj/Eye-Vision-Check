<script lang="ts">
	import { apiClient } from '$lib/api/client';
	import { fetchTestResults } from '$lib/api/results';
	import { onMount } from 'svelte';

	let healthStatus = '';
	let testResults: Record<string, unknown>[] = [];
	let generatedPlate: Record<string, unknown> | null = null;
	let isLoading = false;

	onMount(async () => {
		await testHealthCheck();
		await loadTestResults();
	});

	async function testHealthCheck() {
		try {
			const health = await apiClient.healthCheck();
			healthStatus = `✅ Backend connected: ${health.status}`;
		} catch (error) {
			healthStatus = `❌ Backend connection failed: ${(error as Error).message}`;
		}
	}

	async function loadTestResults() {
		try {
			const results = await fetchTestResults();
			testResults = results as unknown as Record<string, unknown>[];
		} catch (error) {
			console.error('Failed to load test results:', error);
		}
	}

	async function generateTestPlate() {
		isLoading = true;
		try {
			const response = await apiClient.generateIshiharaPlate(1, 'standard');
			generatedPlate = response.success ? response.data : null;
		} catch (error) {
			console.error('Failed to generate plate:', error);
		} finally {
			isLoading = false;
		}
	}

	async function submitTestResult() {
		isLoading = true;
		try {
			await apiClient.submitTestResult({
				test_type: 'ishihara',
				score: 75.5,
				diagnosis: 'Normal color vision',
				total_questions: 8,
				correct_answers: 6,
				test_data: { test_mode: 'api_test' },
				duration_seconds: 120
			});
			await loadTestResults();
		} catch (error) {
			console.error('Failed to submit test result:', error);
		} finally {
			isLoading = false;
		}
	}
</script>

<div class="p-6 max-w-4xl mx-auto">
	<h1 class="text-3xl font-bold mb-6">API Integration Test</h1>

	<div class="mb-8 p-4 bg-gray-100 rounded-lg">
		<h2 class="text-xl font-semibold mb-2">Backend Connection</h2>
		<p class="text-lg">{healthStatus}</p>
		<button
			onclick={testHealthCheck}
			class="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
			disabled={isLoading}
		>
			Test Connection
		</button>
	</div>

	<div class="mb-8 p-4 bg-gray-100 rounded-lg">
		<h2 class="text-xl font-semibold mb-2">Test Generation</h2>
		<button
			onclick={generateTestPlate}
			class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
			disabled={isLoading}
		>
			{isLoading ? 'Generating...' : 'Generate Ishihara Plate'}
		</button>

		{#if generatedPlate}
			<div class="mt-4 p-4 bg-white rounded border">
				<h3 class="font-semibold mb-2">Generated Plate:</h3>
				<p><strong>Round:</strong> {generatedPlate.round}</p>
				<p><strong>Target Number:</strong> {generatedPlate.target_number}</p>
			</div>
		{/if}
	</div>

	<div class="mb-8 p-4 bg-gray-100 rounded-lg">
		<h2 class="text-xl font-semibold mb-2">Test Submission</h2>
		<button
			onclick={submitTestResult}
			class="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
			disabled={isLoading}
		>
			{isLoading ? 'Submitting...' : 'Submit Test Result'}
		</button>
	</div>

	<div class="p-4 bg-gray-100 rounded-lg">
		<h2 class="text-xl font-semibold mb-2">Test Results ({testResults.length})</h2>

		{#if testResults.length > 0}
			<div class="space-y-2">
				{#each testResults as result}
					<div class="p-3 bg-white rounded border">
						<div class="flex justify-between items-center">
							<div>
								<strong class="capitalize">{result.testType ?? result.test_type}</strong>
								<span class="ml-2 text-sm text-gray-600">
									{new Date(String(result.timestamp)).toLocaleDateString()}
								</span>
							</div>
							<div class="text-right">
								<div class="font-semibold">{result.score}%</div>
								<div class="text-sm text-gray-600">{result.diagnosis ?? result.result}</div>
							</div>
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<p class="text-gray-600">No test results found.</p>
		{/if}
	</div>

	{#if isLoading}
		<div class="fixed top-4 right-4 p-4 bg-yellow-100 border border-yellow-400 rounded-lg">
			<p class="text-yellow-800">⏳ Loading...</p>
		</div>
	{/if}
</div>
