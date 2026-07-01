<script lang="ts">
	import { page } from "$app/stores";
	import { onMount } from "svelte";
	import { slide, fade } from "svelte/transition";
	import { theme } from "$lib/stores/theme";
	import { fetchTestResults, fetchUserCount } from "$lib/api/results";
	import {
		Home,
		Eye,
		Droplet,
		Palette,
		Camera,
		BarChart3,
		Grid3X3,
		Contrast,
		Moon,
		Sun,
		Mic,
	} from "lucide-svelte";

	let testCount = 0;
	let isOpen = true;
	let totalUsers = 0;

	const navigationItems = [
		{ id: "home", label: "Home", icon: Home, route: "/", badge: 0 },
		{
			id: "colorvision",
			label: "Color Vision Test",
			icon: Palette,
			route: "/colorvision",
			badge: 0,
			children: [
				{
					id: "ishihara",
					label: "Ishihara Test",
					icon: Eye,
					route: "/ishihara",
					badge: 0,
				},
				{
					id: "tritan",
					label: "Tritan Test",
					icon: Droplet,
					route: "/tritan",
					badge: 0,
				},
				{
					id: "hue",
					label: "Hue Test",
					icon: Palette,
					route: "/hue",
					badge: 0,
				},
			],
		},
		{
			id: "visualacuity",
			label: "Visual Acuity",
			icon: Mic,
			route: "/visualacuity",
			badge: 0,
		},
		{
			id: "contrast",
			label: "Contrast Sensitivity",
			icon: Contrast,
			route: "/contrast",
			badge: 0,
		},
		{
			id: "webcam",
			label: "Webcam Test",
			icon: Camera,
			route: "/webcam",
			badge: 0,
		},
		{
			id: "results",
			label: "Results",
			icon: BarChart3,
			route: "/results",
			badge: testCount,
		},
	];

	onMount(async () => {
		try {
			const [results, count] = await Promise.all([
				fetchTestResults(),
				fetchUserCount(),
			]);
			testCount = results.length;
			totalUsers = count;
		} catch (error) {
			console.error("Failed to load sidebar data:", error);
		}
	});
</script>

<!-- Toggle and theme buttons inside circular container -->
<div class="flex items-center justify-between p-3 bg-gray-100 border-b border-gray-200">
	<button
		on:click={() => (isOpen = !isOpen)}
		class="p-2 rounded bg-blue-600 hover:bg-blue-700 focus:outline-none"
	>
		<Eye class="w-4 h-4 text-white" />
	</button>

	<button
		on:click={() => theme.update((v) => (v === "dark" ? "light" : "dark"))}
		class="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-1 text-xs font-semibold text-gray-700 shadow-sm transition hover:bg-gray-100 focus:outline-none"
	>
		{#if $theme === "dark"}
			<Sun class="w-3 h-3" /> Light
		{:else}
			<Moon class="w-3 h-3" /> Dark
		{/if}
	</button>
</div>

{#if isOpen}
	<nav
		class="bg-gray-100 flex-1 flex flex-col overflow-hidden"
		transition:slide
	>
		<!-- Header -->
		<div class="p-4 border-b border-gray-200" transition:fade>
			<h2 class="text-xl font-bold text-gray-900 text-center">
				Vision Fusion
			</h2>
			<p class="text-xs text-gray-700 text-center">Eye Vision Track</p>
		</div>
		<!-- Navigation -->
		<div class="flex-1 p-3 overflow-y-auto">
			<ul class="space-y-1">
				{#each navigationItems as item}
					{@const IconComponent = item.icon}
					<li transition:fade>
						<a
							href={item.route}
							class="flex items-center p-2 rounded-lg transition-colors duration-200 {$page
								.url.pathname === item.route
								? 'bg-blue-100 text-blue-700 shadow-sm'
								: 'text-gray-700 hover:bg-gray-100'}"
						>
							<IconComponent class="w-4 h-4 mr-2" />
							<span class="flex-1 text-sm">{item.label}</span>
							{#if item.badge && item.badge > 0}
								<span
									class="bg-blue-600 text-white text-xs px-1.5 py-0.5 rounded-full"
									>{item.badge}</span
								>
							{/if}
						</a>
					</li>
					{#if item.children}
						{#each item.children as child}
							{@const ChildIcon = child.icon}
							<li transition:fade class="ml-3">
								<a
									href={child.route}
									class="flex items-center p-1.5 rounded-lg transition-colors duration-200 {$page
										.url.pathname === child.route
										? 'bg-blue-100 text-blue-700 shadow-sm'
										: 'text-gray-700 hover:bg-gray-100'}"
								>
									<ChildIcon class="w-3 h-3 mr-1.5" />
									<span class="flex-1 text-xs">{child.label}</span>
								</a>
							</li>
						{/each}
					{/if}
				{/each}
			</ul>
		</div>
		<!-- Footer -->
		<div class="p-3 border-t border-gray-200">
			<div class="text-center">
				<p class="text-xs text-gray-500">Version 1.0.0</p>
				<p class="text-xs text-gray-400">© 2026 Color Vision Test</p>
			</div>
		</div>
	</nav>
{/if}
