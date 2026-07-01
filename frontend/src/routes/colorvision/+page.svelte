<script lang="ts">
  import { fly } from "svelte/transition";
</script>

<svelte:head>
	<title>Color Vision Test</title>
</svelte:head>

<div class="circular-container" in:fly={{ y: 20, duration: 600 }}>
  <div class="content-wrapper bg-white">
    <h1 class="text-6xl font-bold mb-6 text-gray-900 text-center">Color Vision Test</h1>
    <p class="text-2xl text-gray-600 mb-8 text-center max-w-2xl">
      Select one of the three tests below to evaluate your color vision.
    </p>
    <div class="grid grid-cols-1 gap-6 w-full max-w-3xl">
      <a
        href="/ishihara"
        class="block p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition-all hover:scale-105"
        in:fly={{ y: 30, duration: 600, delay: 100 }}
      >
        <div class="flex items-center mb-3">
          <div
            class="w-16 h-16 bg-gradient-to-br from-red-400 to-orange-500 rounded-2xl flex items-center justify-center mr-4 shadow-lg"
          >
            <svg
              class="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          </div>
          <h2 class="text-3xl font-bold text-gray-800">Ishihara Test</h2>
        </div>
        <p class="text-xl text-gray-600">
          Classic color blindness test using dotted plates with hidden numbers.
        </p>
      </a>

      <a
        href="/tritan"
        class="block p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition-all hover:scale-105"
        in:fly={{ y: 30, duration: 600, delay: 400 }}
      >
        <div class="flex items-center mb-3">
          <div
            class="w-16 h-16 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-2xl flex items-center justify-center mr-4 shadow-lg"
          >
            <svg
              class="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
          <h2 class="text-3xl font-bold text-gray-900">Tritan Test</h2>
        </div>
        <p class="text-xl text-gray-600">
          Blue-yellow color blindness detection test.
        </p>
      </a>

      <a
        href="/hue"
        class="block p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition-all hover:scale-105"
        in:fly={{ y: 30, duration: 600, delay: 700 }}
      >
        <div class="flex items-center mb-3">
          <div
            class="w-16 h-16 bg-gradient-to-br from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mr-4 shadow-lg"
          >
            <svg
              class="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
              />
            </svg>
          </div>
          <h2 class="text-3xl font-bold text-gray-900">Hue Test</h2>
        </div>
        <p class="text-xl text-gray-600">
          Color discrimination test with drag-and-drop functionality.
        </p>
      </a>
    </div>
  </div>
</div>

<style>
	.circular-container {
		background-color: white !important;
	}

	.content-wrapper {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 60px 40px;
		overflow: hidden;
	}
</style>
