<script>
	import { fly } from "svelte/transition";

	const radius = 350;
	const center = 540;
	const nodeSize = 245;

	const tests = [
		{
			name: "Visual Acuity",
			link: "/visualacuity",
			// icon: "👁️",
			desc: "Voice Screening"
		},
		{
			name: "Color Vision",
			link: "/colorvision",
			// icon: "🎨",
			desc: "Ishihara,Tritan & Hue"
		},
		{
			name: "Blink Control Challenge",
			link: "/blink-control",
			desc: "Blink Control"
		},
		{
			name: "Contrast",
			link: "/contrast",
			//icon: "◐",
			desc: "Sensitivity"
		},
		{
			name: "Red Desaturation",
			link: "/red-desaturation",
			// icon: "❤️",
			desc: "Color Perception"
		},
		{
			name: "OKN Stripes",
			link: "/okn",
			// icon: "🌈",
			desc: "Eye Tracking"
		},
		{
			name: "Shape Memory",
			link: "/memory",
			// icon: "🧩",
			desc: "Visual Memory"
		}
	];

	const circles = tests.map((test, index) => {
		const angle =
			(index * (360 / tests.length) - 90) *
			(Math.PI / 180);

		return {
			...test,
			x: center + radius * Math.cos(angle) - nodeSize / 2,
			y: center + radius * Math.sin(angle) - nodeSize / 2
		};
	});
</script>

<div class="circular-container">
	<div class="content-wrapper">
		<!-- Outer Circle Ring -->
		<div
			class="absolute inset-[200px]
			rounded-full
			border-[4px]
			border-amber-200"
			
		></div>

		<!-- Center Circle -->
		<div
			class="absolute
			left-1/2
			top-1/2
			-transform
			-translate-x-1/2
			-translate-y-1/2
			w-64
			h-64
			rounded-full
			bg-white
			text-white
			shadow-2xl
			flex
			p-2
			flex-col
			items-center
			justify-center"
		>
			

			<h2 class="text-3xl font-bold text-center p-2">
				Select the test 
			</h2>

			
		</div>

		<!-- Nodes -->
		{#each circles as circle, i}
			<a
				href={circle.link}
				class="absolute
				bg-white
				rounded-full
				border-[3px]
				border-indigo-500
				shadow-xl
				hover:shadow-2xl
				hover:scale-110
				transition-all
				duration-300
				flex
				flex-col
				items-center
				justify-center
				text-center"
				style="
					width:{nodeSize}px;
					height:{nodeSize}px;
					left:{circle.x}px;
					top:{circle.y}px;
				"
				in:fly={{
					y: 50,
					duration: 800,
					// delay: 2000 + i * 3000
				}}
			>
				<div class="text-4xl mb-2">
					{circle.icon}
				</div>

				<h3
					class="font-bold
					text-gray-800
					text-2xl
					px-2"
				>
					{circle.name}
				</h3>

				<p
					class="text-[25px]
					text-gray-500
					mt-1
					px-3"
				>
					{circle.desc}
				</p>
			</a>
		{/each}
	</div>
</div>

<style>
	.content-wrapper {
		width: 1080px;
		height: 1080px;
		position: relative;
		padding: 40px;
		overflow: hidden;
	}
</style>