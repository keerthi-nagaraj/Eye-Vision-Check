<script lang="ts">
	import type { DistortionMark } from '$lib/types/test';

	interface Props {
		marks?: DistortionMark[];
	}

	let { marks = $bindable([]) }: Props = $props();

	let gridRef: HTMLButtonElement;

	const gridSize = 10;

	function handleInteraction(event: MouseEvent | KeyboardEvent) {
		const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();

		const clientX =
			event instanceof MouseEvent ? event.clientX : rect.left + rect.width / 2;

		const clientY =
			event instanceof MouseEvent ? event.clientY : rect.top + rect.height / 2;

		const x = Math.floor(((clientX - rect.left) / rect.width) * gridSize);
		const y = Math.floor(((clientY - rect.top) / rect.height) * gridSize);

		marks = [...marks, { x, y }];
	}
</script>

<div class="flex justify-center">
	<button
		bind:this={gridRef}
		type="button"
		class="relative w-[500px] h-[500px] border-2 border-black bg-white cursor-crosshair"
		onclick={handleInteraction}
		onkeydown={(e) => {
			if (e.key === 'Enter' || e.key === ' ') {
				handleInteraction(e);
			}
		}}
		aria-label="Amsler grid test area. Click to mark distortion points."
	>
		{#each Array(gridSize + 1) as _, i}
			<div
				class="absolute bg-black"
				style="left:{(i / gridSize) * 100}%; top:0; width:1px; height:100%;"
			></div>
			<div
				class="absolute bg-black"
				style="top:{(i / gridSize) * 100}%; left:0; height:1px; width:100%;"
			></div>
		{/each}

		<div
			class="absolute w-4 h-4 bg-black rounded-full"
			style="left:50%; top:50%; transform:translate(-50%, -50%);"
			aria-hidden="true"
		></div>

		{#each marks as mark}
			<div
				class="absolute w-3 h-3 bg-red-500 rounded-full"
				style="left:{(mark.x / gridSize) * 100}%; top:{(mark.y / gridSize) * 100}%; transform:translate(-50%, -50%);"
				aria-label="Distortion mark at ({mark.x}, {mark.y})"
			></div>
		{/each}
	</button>
</div>
