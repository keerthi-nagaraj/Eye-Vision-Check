<script lang="ts">
	export let shape: string;
	export let showAnswer = false;

	type Dot = {
		x: number;
		y: number;
		r: number;
		color: string;
	};

	let dots: Dot[] = [];

	function drawButterfly(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		// Body
		ctx.ellipse(cx, cy, 5, 30, 0, 0, Math.PI * 2);

		// Left upper wing - simple rounded shape
		ctx.moveTo(cx, cy - 25);
		ctx.quadraticCurveTo(cx - 80, cy - 90, cx - 100, cy - 50);
		ctx.quadraticCurveTo(cx - 90, cy - 10, cx, cy - 5);

		// Left lower wing - simple rounded shape
		ctx.moveTo(cx, cy - 5);
		ctx.quadraticCurveTo(cx - 60, cy + 20, cx - 40, cy + 70);
		ctx.quadraticCurveTo(cx - 20, cy + 60, cx, cy + 25);

		// Right upper wing - simple rounded shape
		ctx.moveTo(cx, cy - 25);
		ctx.quadraticCurveTo(cx + 80, cy - 90, cx + 100, cy - 50);
		ctx.quadraticCurveTo(cx + 90, cy - 10, cx, cy - 5);

		// Right lower wing - simple rounded shape
		ctx.moveTo(cx, cy - 5);
		ctx.quadraticCurveTo(cx + 60, cy + 20, cx + 40, cy + 70);
		ctx.quadraticCurveTo(cx + 20, cy + 60, cx, cy + 25);

		// Antennae
		ctx.moveTo(cx, cy - 30);
		ctx.lineTo(cx - 15, cy - 55);
		ctx.moveTo(cx, cy - 30);
		ctx.lineTo(cx + 15, cy - 55);
	}

	function drawCat(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		// Cat body
		ctx.ellipse(cx, cy + 80, 110, 90, 0, 0, Math.PI * 2);
		// Cat head
		ctx.ellipse(cx, cy - 30, 95, 80, 0, 0, Math.PI * 2);
		// Left ear
		ctx.moveTo(cx - 65, cy - 80);
		ctx.lineTo(cx - 95, cy - 140);
		ctx.lineTo(cx - 25, cy - 95);
		// Right ear
		ctx.moveTo(cx + 65, cy - 80);
		ctx.lineTo(cx + 95, cy - 140);
		ctx.lineTo(cx + 25, cy - 95);
		// Tail
		ctx.moveTo(cx + 110, cy + 80);
		ctx.quadraticCurveTo(cx + 160, cy + 60, cx + 150, cy + 20);
		ctx.quadraticCurveTo(cx + 140, cy - 20, cx + 110, cy - 30);
	}

	// function drawDog(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
	// 	ctx.beginPath();
	// 	// Dog body
	// 	ctx.ellipse(cx, cy + 90, 115, 95, 0, 0, Math.PI * 2);
	// 	// Dog head
	// 	ctx.ellipse(cx, cy - 30, 105, 85, 0, 0, Math.PI * 2);
	// 	// Left ear
	// 	ctx.ellipse(cx - 90, cy - 50, 35, 75, -0.3, 0, Math.PI * 2);
	// 	// Right ear
	// 	ctx.ellipse(cx + 90, cy - 50, 35, 75, 0.3, 0, Math.PI * 2);
	// 	// Snout
	// 	ctx.ellipse(cx, cy + 10, 40, 50, 0, 0, Math.PI * 2);
	// 	// Tail
	// 	ctx.moveTo(cx - 115, cy + 90);
	// 	ctx.quadraticCurveTo(cx - 160, cy + 70, cx - 150, cy + 30);
	// 	ctx.quadraticCurveTo(cx - 140, cy - 10, cx - 115, cy - 30);
	// 	ctx.closePath();
	// }

	// function drawBird(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
	// 	ctx.beginPath();
	// 	// Bird body
	// 	ctx.ellipse(cx, cy + 30, 80, 55, 0, 0, Math.PI * 2);
	// 	// Bird head
	// 	ctx.arc(cx + 65, cy - 20, 40, 0, Math.PI * 2);
	// 	// Beak
	// 	ctx.moveTo(cx + 100, cy - 20);
	// 	ctx.lineTo(cx + 140, cy - 15);
	// 	ctx.lineTo(cx + 100, cy - 10);
	// 	// Wing
	// 	ctx.ellipse(cx - 20, cy + 40, 60, 35, -0.2, 0, Math.PI * 2);
	// 	// Tail
	// 	ctx.moveTo(cx - 80, cy + 30);
	// 	ctx.lineTo(cx - 120, cy + 10);
	// 	ctx.lineTo(cx - 120, cy + 50);
	// 	ctx.closePath();
	// }

	function drawFish(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		// Fish body
		ctx.ellipse(cx, cy, 100, 60, 0, 0, Math.PI * 2);
		// Tail
		ctx.moveTo(cx - 100, cy);
		ctx.lineTo(cx - 150, cy - 55);
		ctx.lineTo(cx - 150, cy + 55);
		ctx.lineTo(cx - 100, cy);
		// Top fin
		ctx.moveTo(cx, cy - 60);
		ctx.lineTo(cx + 20, cy - 100);
		ctx.lineTo(cx + 50, cy - 60);
		ctx.lineTo(cx, cy - 60);
		// Bottom fin
		ctx.moveTo(cx, cy + 60);
		ctx.lineTo(cx + 20, cy + 100);
		ctx.lineTo(cx + 50, cy + 60);
		ctx.lineTo(cx, cy + 60);
	}

	function drawRabbit(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		// Rabbit body
		ctx.ellipse(cx, cy + 100, 100, 85, 0, 0, Math.PI * 2);
		// Rabbit head
		ctx.arc(cx, cy - 20, 80, 0, Math.PI * 2);
		// Left ear
		ctx.ellipse(cx - 45, cy - 100, 25, 95, -0.1, 0, Math.PI * 2);
		// Right ear
		ctx.ellipse(cx + 45, cy - 100, 25, 95, 0.1, 0, Math.PI * 2);
		// Tail
		ctx.arc(cx + 100, cy + 100, 30, 0, Math.PI * 2);
	}

	// function drawElephant(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
	// 	ctx.beginPath();
	// 	// Elephant body
	// 	ctx.ellipse(cx, cy + 120, 130, 100, 0, 0, Math.PI * 2);
	// 	// Elephant head
	// 	ctx.ellipse(cx, cy - 20, 100, 85, 0, 0, Math.PI * 2);
	// 	// Ears
	// 	ctx.ellipse(cx - 90, cy - 10, 55, 75, -0.5, 0, Math.PI * 2);
	// 	ctx.ellipse(cx + 90, cy - 10, 55, 75, 0.5, 0, Math.PI * 2);
	// 	// Trunk
	// 	ctx.moveTo(cx - 35, cy + 60);
	// 	ctx.quadraticCurveTo(cx - 50, cy + 120, cx - 20, cy + 160);
	// 	ctx.quadraticCurveTo(cx + 20, cy + 120, cx + 35, cy + 60);
	// 	// Legs
	// 	ctx.ellipse(cx - 80, cy + 200, 25, 60, 0, 0, Math.PI * 2);
	// 	ctx.ellipse(cx + 80, cy + 200, 25, 60, 0, 0, Math.PI * 2);
	// }

	function drawTriangle(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		const size = 100;
		ctx.moveTo(cx, cy - size);
		ctx.lineTo(cx + size, cy + size);
		ctx.lineTo(cx - size, cy + size);
		ctx.closePath();
	}

	function drawCircle(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		ctx.arc(cx, cy, 100, 0, Math.PI * 2);
	}

	function drawSquare(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		const size = 100;
		ctx.rect(cx - size, cy - size, size * 2, size * 2);
	}

	function drawStar(ctx: CanvasRenderingContext2D, cx: number, cy: number) {
		ctx.beginPath();
		const outerRadius = 150;
		const innerRadius = 70;
		const spikes = 5;

		let rot = Math.PI / 2 * 3;
		let x = cx;
		let y = cy;
		const step = Math.PI / spikes;

		ctx.moveTo(cx, cy - outerRadius);

		for (let i = 0; i < spikes; i++) {
			x = cx + Math.cos(rot) * outerRadius;
			y = cy + Math.sin(rot) * outerRadius;
			ctx.lineTo(x, y);
			rot += step;

			x = cx + Math.cos(rot) * innerRadius;
			y = cy + Math.sin(rot) * innerRadius;
			ctx.lineTo(x, y);
			rot += step;
		}

		ctx.lineTo(cx, cy - outerRadius);
		ctx.closePath();
	}

	function createPlate(shapeText: string) {
		const canvas = document.createElement('canvas');
		canvas.width = 500;
		canvas.height = 500;

		const ctx = canvas.getContext('2d');
		if (!ctx) return [];

		// White background
		ctx.fillStyle = 'white';
		ctx.fillRect(0, 0, 500, 500);

		// Draw shape mask for tritan test
		const isAnimal = ['butterfly', 'cat', 'dog', 'bird', 'fish', 'rabbit', 'elephant'].includes(shapeText.toLowerCase());

		if (isAnimal) {
			// Draw outline for animals
			ctx.strokeStyle = 'black';
			ctx.lineWidth = 20;

			switch (shapeText.toLowerCase()) {
				case 'butterfly':
					drawButterfly(ctx, 250, 250);
					break;
				case 'cat':
					drawCat(ctx, 250, 220);
					break;
				case 'fish':
					drawFish(ctx, 250, 250);
					break;
				case 'rabbit':
					drawRabbit(ctx, 250, 220);
					break;
				default:
					// Default to cat
					drawCat(ctx, 250, 220);
			}

			ctx.stroke();
		} else {
			// Draw filled shape for geometric shapes
			ctx.fillStyle = 'black';

			switch (shapeText.toLowerCase()) {
				case 'triangle':
					drawTriangle(ctx, 250, 250);
					break;
				case 'circle':
					drawCircle(ctx, 250, 250);
					break;
				case 'square':
					drawSquare(ctx, 250, 250);
					break;
				case 'star':
					drawStar(ctx, 250, 250);
					break;
				default:
					// Default to triangle
					drawTriangle(ctx, 250, 250);
			}

			ctx.fill();
		}

		const imageData = ctx.getImageData(0, 0, 500, 500);

		const generatedDots: Dot[] = [];

		// Tritan colors (blue-yellow color blindness testing)
		// Background: shades of blue
		const bgColors = [
			'#4a90d9',
			'#5ba3e8',
			'#3d7cc7',
			'#6bb3f0',
			'#2e6cb0'
		];

		// Foreground: shades of yellow
		const fgColors = [
			'#fff59d',
			'#fff176',
			'#ffee58',
			'#ffeb3b',
			'#fdd835'
		];

		for (let i = 0; i < 7000; i++) {
			const angle = Math.random() * Math.PI * 2;
			const distance = Math.sqrt(Math.random()) * 230;

			const px = 250 + Math.cos(angle) * distance;
			const py = 250 + Math.sin(angle) * distance;

			const ix = Math.floor(px);
			const iy = Math.floor(py);

			const index = (iy * 500 + ix) * 4;

			const insideShape =
				imageData.data[index] < 128;

			generatedDots.push({
				x: (px / 500) * 100,
				y: (py / 500) * 100,
				r: Math.random() * 0.4 + 0.3,
				color: insideShape
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

	$: dots = createPlate(shape);
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
			{shape}
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
