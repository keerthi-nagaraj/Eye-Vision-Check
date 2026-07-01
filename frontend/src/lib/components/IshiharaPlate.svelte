<script lang="ts">
	export let number: number;
	export let showAnswer = false;

	type Dot = {
		x: number;
		y: number;
		r: number;
		color: string;
	};

	let dots: Dot[] = [];

	function createPlate(num: number) {
		const canvas = document.createElement('canvas');
		canvas.width = 500;
		canvas.height = 500;

		const ctx = canvas.getContext('2d');
		if (!ctx) return [];

		// White background
		ctx.fillStyle = 'white';
		ctx.fillRect(0, 0, 500, 500);

		// Draw number mask
		ctx.fillStyle = 'black';
		ctx.font = 'bold 200px Arial';
		ctx.textAlign = 'center';
		ctx.textBaseline = 'middle';
		ctx.fillText(num.toString(), 250, 250);

		const imageData = ctx.getImageData(0, 0, 500, 500);

		const generatedDots: Dot[] = [];

		const bgColors = [
			'#79d279',
			'#66cc66',
			'#5cb85c',
			'#70db70',
			'#8cd98c'
		];

		const fgColors = [
			'#ff7f50',
			'#ff6347',
			'#ff8c69',
			'#ff6b6b',
			'#ff9966'
		];

		for (let i = 0; i < 7000; i++) {
			const angle = Math.random() * Math.PI * 2;
			const distance = Math.sqrt(Math.random()) * 230;

			const px = 250 + Math.cos(angle) * distance;
			const py = 250 + Math.sin(angle) * distance;

			const ix = Math.floor(px);
			const iy = Math.floor(py);

			const index = (iy * 500 + ix) * 4;

			const insideNumber =
				imageData.data[index] < 128;

			generatedDots.push({
				x: (px / 500) * 100,
				y: (py / 500) * 100,
				r: Math.random() * 1.2 + 1.2,
				color: insideNumber
					? fgColors[
							Math.floor(
								Math.random() *
									fgColors.length
							)
					  ]
					: bgColors[
							Math.floor(
								Math.random() *
									bgColors.length
							)
					  ]
			});
		}

		return generatedDots;
	}

	$: dots = createPlate(number);
</script>

<div class="plate-container">
	<svg viewBox="0 0 100 100">
		{#each dots as dot}
			<circle
				cx={dot.x}
				cy={dot.y}
				r={dot.r}
				fill={dot.color}
			/>
		{/each}
	</svg>

	{#if showAnswer}
		<div class="answer">
			{number}
		</div>
	{/if}
</div>

<style>
	.plate-container {
		position: relative;
		width: 700px;
		height: 700px;
		border-radius: 50%;
		margin: auto;
	}

	svg {
		width: 100%;
		height: 100%;
		border-radius: 50%;
		background: white;
		box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
	}

	.answer {
		position: absolute;
		top: 10px;
		right: 10px;
		background: white;
		padding: 6px 12px;
		border-radius: 8px;
		font-weight: bold;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
	}
</style>