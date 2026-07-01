<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import { onMount } from 'svelte';
	import { fetchTestResults, clearAllResults as clearResultsInDb, deleteTestResult } from '$lib/api/results';

	interface DisplayResult {
		id: string;
		testType: string;
		score: number;
		result: string;
		timestamp: string;
		webcamStatus?: string;
		averageDistance?: number;
		brightness?: string;
		positioning?: string;
	}

	let allResults: DisplayResult[] = [];

	// Configurable diagnosis thresholds
	const DIAGNOSIS_THRESHOLD_NORMAL = 80;
	const DIAGNOSIS_THRESHOLD_MILD = 60;
	const DIAGNOSIS_THRESHOLD_MODERATE = 40;

	onMount(() => {
		loadResults();
	});

	async function loadResults() {
		try {
			const results = await fetchTestResults();
			allResults = results.map((r) => ({
				id: r.id || '',
				testType: r.testType || 'Unknown',
				score:
					typeof r.score === 'string'
						? parseFloat(String(r.score).replace('%', ''))
						: Number(r.score) || 0,
				result: r.result || r.diagnosis || 'Completed',
				timestamp: r.timestamp || new Date().toISOString(),
				webcamStatus: (r.testData?.webcamStatus as string) || '',
				averageDistance: Number(r.testData?.averageDistance) || 0,
				brightness: (r.testData?.brightness as string) || '',
				positioning: (r.testData?.positioning as string) || ''
			}));
		} catch (err) {
			console.error('Error loading results:', err);
			allResults = [];
		}
	}

	// =========================
	// FILTERS
	// =========================

	$: ishiharaResults =
		allResults.filter((r) =>
			r.testType
				.toLowerCase()
				.includes('ishihara')
		);

	$: tritanResults =
		allResults.filter((r) =>
			r.testType
				.toLowerCase()
				.includes('tritan')
		);

	$: hueResults =
		allResults.filter((r) =>
			r.testType
				.toLowerCase()
				.includes('hue')
		);

	$: contrastResults =
	     allResults.filter((r) =>
		    r.testType
			    .toLowerCase()
				.includes('contrast'));

	$: webcamResults =
		allResults.filter((r) =>
			r.testType
				.toLowerCase()
				.includes('webcam')
		);

	// =========================
	// COUNTS
	// =========================

	$: totalTestsTaken = {
		ishihara: ishiharaResults.length,
		tritan: tritanResults.length,
		hue: hueResults.length,
		contrast: contrastResults.length,
		webcam: webcamResults.length
	};

	$: grandTotal =
		totalTestsTaken.ishihara +
		totalTestsTaken.tritan +
		totalTestsTaken.hue +
		totalTestsTaken.contrast +
		totalTestsTaken.webcam;

	// =========================
	// OVERALL SCORE
	// =========================

	$: overallScore =
		allResults.length > 0
			? Math.round(
					allResults.reduce(
						(sum, r) =>
							sum + Number(r.score || 0),
						0
					) / allResults.length
			  )
			: 0;

	function getDiagnosis(score: number) {
		if (score >= DIAGNOSIS_THRESHOLD_NORMAL) {
			return 'Normal Color Vision';
		}

		if (score >= DIAGNOSIS_THRESHOLD_MILD) {
			return 'Mild Deficiency';
		}

		if (score >= DIAGNOSIS_THRESHOLD_MODERATE) {
			return 'Moderate Deficiency';
		}

		return 'Significant Deficiency';
	}

	// =========================
	// CLEAR RESULTS
	// =========================

	async function clearAllResults() {
		try {
			const data = await clearResultsInDb();
			if (data.success) {
				await loadResults();
			} else {
				alert('Failed to clear results');
			}
		} catch (err) {
			console.error('Error clearing results:', err);
			alert('Failed to clear results');
		}
	}

	async function deleteResult(id: string) {
		try {
			await deleteTestResult(id);
			await loadResults();
		} catch (err) {
			console.error('Error deleting result:', err);
			alert('Failed to delete result');
		}
	}



	// =========================
	// EXPORT JSON
	// =========================

	function exportResults() {
		const blob = new Blob(
			[
				JSON.stringify(
					allResults,
					null,
					2
				)
			],
			{
				type: 'application/json'
			}
		);

		const url =
			URL.createObjectURL(blob);

		const a =
			document.createElement('a');

		a.href = url;

		a.download = `color-vision-results-${
			new Date()
				.toISOString()
				.split('T')[0]
		}.json`;

		a.click();

		URL.revokeObjectURL(url);
	}

	// =========================
	// EXPORT PDF
	// =========================

	function exportPDF() {
		const printWindow = window.open(
			'',
			'_blank'
		);

		if (!printWindow) return;

		const rows = allResults
			.map(
				(
					result,
					index
				) => `
			<tr>
				<td>${index + 1}</td>
				<td>${result.testType}</td>
				<td>${result.score}%</td>
				<td>${result.result}</td>
				<td>${new Date(
					result.timestamp
				).toLocaleString()}</td>
			</tr>
		`
			)
			.join('');

		printWindow.document.write(`
			<html>
				<head>
					<title>Eye Vision Test Report</title>

					<style>
						body {
							font-family: Arial, sans-serif;
							padding: 30px;
						}

						table {
							width: 100%;
							border-collapse: collapse;
							margin-top: 20px;
						}

						th,
						td {
							border: 1px solid #ddd;
							padding: 12px;
							text-align: left;
						}

						th {
							background: #f3f4f6;
						}
					</style>
				</head>

				<body>

					<h1>
						Eye Vision Test Report
					</h1>

					<p>
						<strong>Total Tests:</strong>
						${grandTotal}
					</p>

					<p>
						<strong>Overall Score:</strong>
						${overallScore}%
					</p>

					<p>
						<strong>Diagnosis:</strong>
						${getDiagnosis(overallScore)}
					</p>

					<table>
						<thead>
							<tr>
								<th>#</th>
								<th>Test Type</th>
								<th>Score</th>
								<th>Result</th>
								<th>Date</th>
							</tr>
						</thead>

						<tbody>
							${rows}
						</tbody>
					</table>

				</body>
			</html>
		`);

		printWindow.document.close();

		printWindow.print();
	}

	// =========================
	// BADGE COLORS
	// =========================

	function getBadgeColor(type: string) {
		const lower =
			type.toLowerCase();

		if (lower.includes('ishihara')) {
			return 'bg-red-100 text-red-700';
		}

		if (lower.includes('tritan')) {
			return 'bg-cyan-100 text-cyan-700';
		}

		if (lower.includes('hue')) {
			return 'bg-purple-100 text-purple-700';
		}

		if (lower.includes('webcam')) {
			return 'bg-green-100 text-green-700';
		}

		if (lower.includes('contrast')) {
			return 'bg-pink-100 text-pink-700';
		}

		return 'bg-gray-100 text-gray-700';
	}
</script>

<div class="flex flex-col items-center justify-center h-full bg-gray-50">

	<div class="w-full max-w-lg px-4">
		<!-- HEADER -->
		<header class="mb-4">
			<h1 class="mb-2 text-2xl font-bold text-gray-900 text-center">
				📊 Test Results
			</h1>

			<p class="text-sm text-gray-600 text-center">
				View all your color vision test performance
				</p>
			</header>

			{#if allResults.length > 0}

				<!-- SUMMARY CARDS -->

				<div
					class="mb-8 grid grid-cols-1 gap-6 md:grid-cols-5"
				>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-gray-700"
						>
							Total Tests
						</h3>

						<p
							class="text-5xl font-bold text-blue-600"
						>
							{grandTotal}
						</p>
					</div>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-red-700"
						>
							Ishihara
						</h3>

						<p
							class="text-5xl font-bold text-red-600"
						>
							{totalTestsTaken.ishihara}
						</p>
					</div>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-cyan-700"
						>
							Tritan
						</h3>

						<p
							class="text-5xl font-bold text-cyan-600"
						>
							{totalTestsTaken.tritan}
						</p>
					</div>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-purple-700"
						>
							Hue
						</h3>

						<p
							class="text-5xl font-bold text-purple-600"
						>
							{totalTestsTaken.hue}
						</p>
					</div>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-green-700"
						>
							Webcam
						</h3>

						<p
							class="text-5xl font-bold text-green-600"
						>
							{totalTestsTaken.webcam}
						</p>
					</div>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-pink-700"
						>
							Contrast Sensitivity
						</h3>

						<p
							class="text-5xl font-bold text-pink-600"
						>
							{totalTestsTaken.contrast}
						</p>
					</div>

				</div>

				<!-- OVERALL -->

				<div
					class="mb-8 grid gap-6 md:grid-cols-2"
				>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-gray-700"
						>
							Overall Score
						</h3>

						<p
							class="text-5xl font-bold text-green-600"
						>
							{overallScore}%
						</p>
					</div>

					<div
						class="rounded-2xl bg-white p-6 shadow-lg"
					>
						<h3
							class="mb-2 text-lg font-semibold text-gray-700"
						>
							Diagnosis
						</h3>

						<p
							class="text-2xl font-bold text-purple-600"
						>
							{getDiagnosis(overallScore)}
						</p>
					</div>

				</div>

				<!-- WEBCAM DETAILS TABLE -->

				{#if webcamResults.length > 0}

					<div
						class="mb-8 overflow-hidden rounded-2xl bg-white shadow-lg"
					>

						<div
							class="border-b bg-green-50 px-6 py-4"
						>
							<h2
								class="text-2xl font-bold text-green-700"
							>
								🎥 Webcam Test Details
							</h2>
						</div>

						<div class="overflow-x-auto">

							<table
								class="min-w-full divide-y divide-gray-200"
							>

								<thead
									class="bg-green-100"
								>

									<tr>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Test No
										</th>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Status
										</th>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Average Distance
										</th>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Brightness
										</th>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Position
										</th>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Score
										</th>

										<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
											Date
										</th>

									</tr>

								</thead>

								<tbody
									class="divide-y divide-gray-200"
								>

									{#each webcamResults as webcam, index}

										<tr
											class="hover:bg-green-50 transition"
										>

											<td class="px-6 py-4 font-semibold">
												#{index + 1}
											</td>

											<td class="px-6 py-4">
												{webcam.webcamStatus || 'Perfect'}
											</td>

											<td class="px-6 py-4">
												{webcam.averageDistance || 0} cm
											</td>

											<td class="px-6 py-4">
												{webcam.brightness || 'Good'}
											</td>

											<td class="px-6 py-4">
												{webcam.positioning || 'Centered'}
											</td>

											<td class="px-6 py-4 font-semibold text-green-700">
												{webcam.score}%
											</td>

											<td class="px-6 py-4 text-gray-600">
												{new Date(
													webcam.timestamp
												).toLocaleString()}
											</td>

										</tr>

									{/each}

								</tbody>

							</table>

						</div>

					</div>

				{/if}



				<!-- MAIN RESULTS TABLE -->

				<div
					class="mb-8 overflow-hidden rounded-2xl bg-white shadow-lg"
				>

					<div class="overflow-x-auto">

						<table
							class="min-w-full divide-y divide-gray-200"
						>

							<thead
								class="bg-gray-100"
							>

								<tr>

									<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
										Test Type
									</th>

									<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
										Score
									</th>

									<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
										Result
									</th>

									<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
										Date
									</th>

									<th class="px-6 py-4 text-left text-sm font-semibold text-gray-700">
										Actions
									</th>

								</tr>

							</thead>

							<tbody
								class="divide-y divide-gray-200"
							>

								{#each allResults as result}

									<tr
										class="transition hover:bg-gray-50"
									>

										<td class="px-6 py-4">

											<span
												class={`rounded-full px-3 py-1 text-xs font-semibold ${getBadgeColor(result.testType)}`}
											>
												{result.testType}
											</span>

										</td>

										<td class="px-6 py-4 font-semibold">
											{result.score}%
										</td>

										<td class="px-6 py-4">
											{result.result}
										</td>

										<td class="px-6 py-4 text-gray-600">
											{new Date(
												result.timestamp
											).toLocaleString()}
										</td>

										<td class="px-6 py-4">
											<button
												on:click={() => deleteResult(result.id)}
												class="rounded-lg bg-red-100 px-3 py-1 text-sm font-semibold text-red-700 transition hover:bg-red-200"
											>
												Delete
											</button>
										</td>

									</tr>

								{/each}

							</tbody>

						</table>

					</div>

				</div>

				<!-- BUTTONS -->

				<div class="flex flex-wrap gap-4">

					<button
						on:click={exportResults}
						class="rounded-xl bg-green-600 px-6 py-3 text-white transition hover:bg-green-700"
					>
						📥 Export JSON
					</button>

					<button
						on:click={exportPDF}
						class="rounded-xl bg-blue-600 px-6 py-3 text-white transition hover:bg-blue-700"
					>
						📄 Download PDF
					</button>

					<button
						on:click={clearAllResults}
						class="rounded-xl bg-red-600 px-6 py-3 text-white transition hover:bg-red-700"
					>
						🗑 Clear Results
					</button>

					<a
						href="/"
						class="rounded-xl bg-gray-700 px-6 py-3 text-white transition hover:bg-gray-800"
					>
						← Back Home
					</a>

				</div>

			{:else}

				<div
					class="rounded-2xl bg-white p-12 text-center shadow-lg"
				>

					<div class="mb-4 text-7xl">
						📋
					</div>

					<h2
						class="mb-4 text-3xl font-bold text-gray-800"
					>
						No Results Yet
					</h2>

					<p
						class="text-lg text-gray-600"
					>
						Complete a test to see results here.
					</p>

				</div>

			{/if}

		</div>
	</div>