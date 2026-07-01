<script lang="ts">
  import ContrastCard from "./ContrastCard.svelte";
  import { onMount, onDestroy } from "svelte";
  import { ContrastTest } from "$lib/contrastTest";
  import { goto } from "$app/navigation";

  let test: ContrastTest;
  let allPatterns: { letters: string[]; contrast: number }[] = [];
  let pattern: { letters: string[]; contrast: number };
  let loading = true;

  // Combined State Management
  let started = false;
  let currentStep: 1 | 2 = 1;
  let stepCompleted = false;
  let combinedCompleted = false;

  // Part 1: Step-by-Step results
  let stepResults: { shown: string[]; answer: string; correct: boolean; contrast: number }[] = [];
  let userAnswer = "";

  // Part 2: Triangle Chart results
  let chartResults: boolean[] = [];

  // Combined results submission status
  let submitting = false;
  let submitted = false;

  // Active tab for result details
  let activeTab: 'step' | 'chart' = 'step';

  // WebSocket connection
  let ws: WebSocket | null = null;
  let wsConnected = false;
  let visionDistance: number | null = null;

  // Configurable constants
  const WEBSOCKET_URL = 'ws://localhost:8765';
  const DISTANCE_ROUNDING_FACTOR = 10;

 //
  onMount(() => {
    test = new ContrastTest();
    pattern = test.generate();
    allPatterns = test.generateAll();
    chartResults = new Array(allPatterns.length).fill(false);
    loading = false;
    connectWebSocket();
  });

  onDestroy(() => {
    disconnectWebSocket();
  });

  function connectWebSocket() {
    try {
      ws = new WebSocket(WEBSOCKET_URL);
      ws.onopen = () => {
        console.log('WebSocket connected to bridge');
        wsConnected = true;
      };
      ws.onmessage = (event) => {
        const data = event.data;
        try {
          const jsonData = JSON.parse(data);
          if (jsonData.mean !== undefined) {
            visionDistance = Math.round(jsonData.mean * DISTANCE_ROUNDING_FACTOR) / DISTANCE_ROUNDING_FACTOR;
          }
        } catch (e) {
          // Not JSON, ignore
        }
      };
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        wsConnected = false;
      };
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        wsConnected = false;
      };
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      wsConnected = false;
    }
  }

  function disconnectWebSocket() {
    if (ws) {
      ws.close();
      ws = null;
    }
    wsConnected = false;
  }

  function startTest() {
    started = true;
    currentStep = 1;
    stepCompleted = false;
    combinedCompleted = false;
    submitted = false;
    stepResults = [];
    userAnswer = "";
    test.reset();
    test.enableAdaptiveMode(); // Enable adaptive real-time testing
    pattern = test.generate();
    allPatterns = test.generateAll();
    chartResults = new Array(allPatterns.length).fill(false);
  }

  function submitStepAnswer() {
    const upperAnswer = userAnswer.trim().toUpperCase();
    const enteredLetters = upperAnswer.split('');

    // Check if the entered letters are present in the shown letters
    const correct = enteredLetters.length > 0 && enteredLetters.every(letter => pattern.letters.includes(letter));

    // Send answer data to backend via WebSocket
    if (ws && wsConnected) {
      try {
        ws.send(JSON.stringify({
          type: 'contrast_answer',
          step: stepResults.length + 1,
          lettersShown: pattern.letters,
          userAnswer: userAnswer,
          contrast: pattern.contrast,
          correct: correct,
          distance: visionDistance || 0
        }));
      } catch (error) {
        console.error('Failed to send Contrast answer data:', error);
      }
    }

    // Update adaptive difficulty based on performance
    test.updateDifficulty(correct);

    stepResults.push({
      shown: pattern.letters,
      answer: userAnswer,
      correct,
      contrast: pattern.contrast
    });

    stepResults = [...stepResults];

    const next = test.next();

    if (next === null) {
      stepCompleted = true;
      userAnswer = "";
      return;
    }

    pattern = test.generate();
    userAnswer = "";
  }

  function proceedToPart2() {
    currentStep = 2;
    // Reset adaptive test for Part 2 and generate adaptive patterns
    test.reset();
    test.enableAdaptiveMode();
    allPatterns = test.generateAll();
    chartResults = new Array(allPatterns.length).fill(false);
  }

  function toggleChartRow(index: number) {
    chartResults[index] = !chartResults[index];
    chartResults = [...chartResults];
  }

  async function submitCombinedTest() {
    submitting = true;

    const stepCorrectCount = stepResults.filter(r => r.correct).length;
    const chartCorrectCount = chartResults.filter(r => r).length;

    const totalQuestions = stepResults.length + allPatterns.length; // 10 + 10 = 20
    const correctAnswers = stepCorrectCount + chartCorrectCount;
    const score = Math.round((correctAnswers / totalQuestions) * 100);

    const result = score >= 80
      ? 'Normal Contrast Sensitivity'
      : score >= 50
        ? 'Mild Contrast Sensitivity Loss'
        : 'Severe Contrast Sensitivity Loss';

    // Send completion data to backend via WebSocket
    if (ws && wsConnected) {
      try {
        const stepScore = stepResults.length > 0 ? Math.round((stepCorrectCount / stepResults.length) * 100) : 0;
        const chartScore = allPatterns.length > 0 ? Math.round((chartCorrectCount / allPatterns.length) * 100) : 0;
        ws.send(JSON.stringify({
          type: 'contrast_complete',
          stepScore: stepScore,
          chartScore: chartScore,
          combinedScore: score,
          diagnosis: result,
          distance: visionDistance || 0
        }));
      } catch (error) {
        console.error('Failed to send Contrast completion data:', error);
      }
    }

    submitted = true;
    combinedCompleted = true;
    submitting = false;
  }

  function continueToResults() {
    goto('/results');
  }

  function resetTest() {
    started = false;
    currentStep = 1;
    stepCompleted = false;
    combinedCompleted = false;
    stepResults = [];
    userAnswer = '';
    chartResults = [];
    submitting = false;
    submitted = false;
    test.reset();
    pattern = test.generate();
    allPatterns = test.generateAll();
    chartResults = new Array(allPatterns.length).fill(false);
  }

  // Combined score calculations for display
  $: stepCorrectCount = stepResults.filter(r => r.correct).length;
  $: chartCorrectCount = chartResults.filter(r => r).length;
  $: totalQuestions = stepResults.length + allPatterns.length;
  $: correctAnswers = stepCorrectCount + chartCorrectCount;
  $: combinedScore = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
  $: stepScore = stepResults.length > 0 ? Math.round((stepCorrectCount / stepResults.length) * 100) : 0;
  $: chartScore = allPatterns.length > 0 ? Math.round((chartCorrectCount / allPatterns.length) * 100) : 0;
</script>

{#if loading}
  <div class="loading-state">
      <div class="spinner"></div>
      <p>Preparing combined test...</p>
    </div>
  {:else}
    <!-- MAIN VIEWS -->
    {#if !started && !combinedCompleted}
      <!-- Instructions View -->
      <div class="intro-card ">
        <div class="icon-wrap">◑</div>
        <h2>Combined Contrast Sensitivity Test</h2>
        <p class="description">
          This comprehensive test measures your ability to distinguish detail at low contrast levels. It consists of two parts:
        </p>

        <div class="parts-grid">
          <div class="part-desc">
            <span class="badge">Part 1</span>
            <h3>Step-by-Step letter identification</h3>
            <p>Identify letters shown one screen at a time as they become increasingly harder to see.</p>
          </div>
          <div class="part-desc">
            <span class="badge">Part 2</span>
            <h3>Triangle Chart evaluation</h3>
            <p>Review a complete chart of letters grouped in rows of decreasing opacity. Mark the rows you can read.</p>
          </div>
        </div>


        <button class="btn btn-primary btn-lg btn-glow" on:click={startTest}>
          Start Combined Test
        </button>
      </div>

    {:else if started && currentStep === 1 && !stepCompleted}
      <!-- Part 1: Step-by-Step Active -->
      <div class="test-card">
        <div class="test-header">
          <span class="sub">Part 1: Step-by-Step Test</span>
          <h3>Level {stepResults.length + 1} of 10</h3>
          <div class="progress-bar-wrap">
            <div class="progress-bar-fill" style="width: {(stepResults.length / 10) * 100}%"></div>
          </div>
        </div>

        <div class="display-area">
          <ContrastCard letters={pattern.letters} contrast={pattern.contrast} />
        </div>

        <div class="input-area">
          <p class="input-hint">Type the letters you see above (case-insensitive):</p>
          <div class="input-group">
            <input
              type="text" style="background-color: white;"
              bind:value={userAnswer}
              placeholder="Enter letters (e.g. A, B, C)"
              autocomplete="off"
              autocorrect="off"
              autocapitalize="characters"
              on:keydown={(e) => e.key === 'Enter' && userAnswer.trim() && submitStepAnswer()}
            />
            <button
              class="btn btn-primary"
              on:click={submitStepAnswer}
              disabled={!userAnswer.trim()}
            >
              Submit Answer
            </button>
          </div>
        </div>
      </div>

    {:else if started && currentStep === 1 && stepCompleted}
      <!-- Transition Screen to Part 2 -->
      <div class="transition-card">
        <div class="icon-wrap success">✔</div>
        <h2>Part 1 Completed!</h2>
        <p class="description">
          Excellent job. You have completed the Step-by-Step part of the test.
        </p>

        <div class="part-stat-summary">
          <p>Letters correctly identified: <strong class="text-green">{stepCorrectCount} / 10</strong></p>
          <div class="mini-bar">
            <div class="mini-fill success" style="width: {stepScore}%"></div>
          </div>
        </div>

        <p class="next-prompt">
          Let's continue to **Part 2: Triangle Chart** to finish your combined evaluation.
        </p>

        <button class="btn btn-primary btn-lg btn-glow" on:click={proceedToPart2}>
          Proceed to Part 2
        </button>
      </div>

    {:else if started && currentStep === 2 && !combinedCompleted}
      <!-- Part 2: Triangle Chart Active -->
      <div class="test-card">
        <div class="test-header">
          <span class="sub">Part 2: Triangle Chart Test</span>
          <h3>Select All Readable Rows</h3>
        </div>

        <div class="triangle-chart-container">
          <div class="triangle-chart">
            {#each allPatterns as pattern, index}
              <button
                class="chart-row"
                class:selected={chartResults[index]}
                style="opacity: {pattern.contrast}"
                on:click={() => toggleChartRow(index)}
                aria-label="Row {index + 1}: letters {pattern.letters.join(', ')}"
              >
                <span class="row-indicator">Row {index + 1}</span>
                  {#each pattern.letters as letter}
                    <span class="letter-char">{letter}</span>
                  {/each}
                  <div class="checkbox" class:checked={chartResults[index]}>
                    {#if chartResults[index]}✓{/if}
                  </div>
                </button>
              {/each}
            </div>
          </div>

          <div class="actions">
            <button class="btn btn-outline" on:click={() => allPatterns = test.generateAll()}>
              Regenerate Chart
            </button>
            <button
              class="btn btn-primary btn-glow"
              on:click={submitCombinedTest}
              disabled={submitting}
            >
              {#if submitting}Saving Results...{:else}Submit Combined Test{/if}
            </button>
          </div>
        </div>

    {:else if combinedCompleted}
      <!-- Combined Results Summary View -->
      <div class="results-card">
        <h2>Combined Test Results</h2>
        <span class="date-tag">Completed Just Now</span>

        <div class="results-main">
          <!-- Individual Scores -->
          <div class="individual-scores">
            <div class="score-item">
              <span class="score-label">Part 1: Step-by-Step</span>
              <span class="score-value">{stepScore}%</span>
            </div>
            <div class="score-item">
              <span class="score-label">Part 2: Triangle Chart</span>
              <span class="score-value">{chartScore}%</span>
            </div>
          </div>

          <!-- Circular score display -->
          <div class="score-circle-wrapper">
            <svg viewBox="0 0 100 100" class="score-circle">
              <circle cx="50" cy="50" r="45" class="bg-track" />
              <circle
                cx="50"
                cy="50"
                r="45"
                class="fg-fill"
                class:normal={combinedScore >= 80}
                class:mild={combinedScore >= 50 && combinedScore < 80}
                class:severe={combinedScore < 50}
                style="stroke-dasharray: 282.7; stroke-dashoffset: {282.7 - (282.7 * combinedScore) / 100};"
              />
            </svg>
            <div class="score-value-wrap">
              <span class="score-percent">{combinedScore}%</span>
              <span class="score-label">Overall Score</span>
            </div>
          </div>

          <div class="diagnosis-box">
            <span class="label">Diagnosis</span>
            <h3 class:normal={combinedScore >= 80} class:mild={combinedScore >= 50 && combinedScore < 80} class:severe={combinedScore < 50}>
              {combinedScore >= 80
                ? 'Normal Contrast Sensitivity'
                : combinedScore >= 50
                  ? 'Mild Contrast Sensitivity Loss'
                  : 'Severe Contrast Sensitivity Loss'}
            </h3>
            <p class="explanation">
              {combinedScore >= 80
                ? 'Your vision is performing optimally under varying contrast settings.'
                : combinedScore >= 50
                  ? 'You have slight difficulty identifying low-contrast elements. This is common and manageable.'
                  : 'You have significant difficulty seeing items with low contrast. We recommend scheduling an eye test.'}
            </p>
          </div>
        </div>

        <button class="btn btn-primary btn-lg btn-glow" on:click={resetTest}>
          Retake Test
        </button>
      </div>
    {/if}
  {/if}

<style>
  /* PREMIUM CSS DESIGN FOR COMBINED CONTRAST TEST */
  :global(:root) {
    --primary: #3b82f6;
    --primary-hover: #2563eb;
    --primary-glow: rgba(59, 130, 246, 0.35);
    --success: #10b981;
    --success-bg: #ecfdf5;
    --success-text: #047857;
    --fail: #ef4444;
    --fail-bg: #fef2f2;
    --fail-text: #b91c1c;
    --mild-warning: #f59e0b;
    --mild-warning-bg: #fffbeb;
    --mild-warning-text: #b45309;
    --slate-50: #f8fafc;
    --slate-100: #f1f5f9;
    --slate-200: #e2e8f0;
    --slate-600: #475569;
    --slate-700: #334155;
    --slate-900: #0f172a;
    --border-radius: 16px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* MAIN CONTAINER - Centered in round screen */
  :global(body) {
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: #f5f5f5;
  }

  /* LOADING & SPINNER */
  .loading-state {
    text-align: center;
    padding: 40px 20px;
  }
  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid var(--slate-200);
    border-top-color: var(--primary);
    border-radius: 50%;
    margin: 0 auto 20px;
    animation: spin 1s infinite linear;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* INTRO CARD styling */
  .intro-card {
    text-align: center;
    height: 900px;
    width: 900px;
  }
  .icon-wrap {
    width: 80px;
    height: 80px;
    background: var(--slate-50);
    border-radius: 50%;
    margin: 0 auto 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    color: var(--slate-700);
    border: 1px solid var(--slate-200);
  }
  .icon-wrap.success {
    background: var(--success-bg);
    color: var(--success);
    border-color: rgba(16, 185, 129, 0.2);
  }
  h2 {
    font-size: 25px;
    font-weight: 800;
    color: var(--slate-900);
    margin-bottom: 12px;
  }
  @media (max-width: 480px) {
    h2 {
      font-size: 18px;
    }
  }
  .description {
    color: var(--slate-600);
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 20px;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
  }
  @media (max-width: 480px) {
    .description {
      font-size: 13px;
    }
  }

  .parts-grid {
    display: flex;
    flex-direction: row;
    gap: 16px;
    margin-bottom: 25px;
    text-align: left;
  }
  @media (max-width: 640px) {
    .parts-grid {
      flex-direction: column;
    }
  }
  .part-desc {
    background: var(--slate-50);
    border-radius: 12px;
    padding: 16px;
    border: 1px solid var(--slate-100);
    transition: var(--transition);
  }
  .part-desc:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
  }
  .part-desc .badge {
    display: inline-block;
    background: var(--slate-200);
    color: var(--slate-700);
    font-size: 10px;
    font-weight: 750;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 20px;
    margin-bottom: 10px;
  }
  .part-desc h3 {
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 6px;
    color: var(--slate-900);
  }
  .part-desc p {
    font-size: 12px;
    color: var(--slate-600);
    line-height: 1.5;
  }

  /* TEST CARDS */
  .test-header {
    margin-bottom: 30px;
    text-align: center;
  }
  .test-header .sub {
    font-size: 20px;
    font-weight: 750;
    text-transform: uppercase;
    color: var(--primary);
    letter-spacing: 0.05em;
    display: block;
    margin-bottom: 6px;
  }
  .test-header h3 {
    font-size: 23px;
    font-weight: 800;
    color: var(--slate-900);
    margin-bottom: 15px;
  }
  .progress-bar-wrap {
    width: 100%;
    height: 6px;
    background: var(--slate-100);
    border-radius: 10px;
    overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%;
    background: var(--primary);
    border-radius: 10px;
    transition: width 0.4s ease;
  }

  .display-area {
    margin-bottom: 25px;
  }

  /* INPUT & ACTION ARREAS */
  .input-area {
    background: var(--slate-50);
    border-radius: 12px;
    padding: 16px;
    border: 1px solid var(--slate-100);
  }
  .input-hint {
    font-size: 13px;
    font-weight: 600;
    color: var(--slate-700);
    margin-bottom: 10px;
    text-align: center;
  }
  .input-group {
    display: flex;
    gap: 10px;
  }
  .input-group input {
    flex: 1;
    padding: 12px 14px;
    border-radius: 8px;
    border: 2px solid var(--slate-200);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    outline: none;
    transition: var(--transition);
  }
  @media (max-width: 480px) {
    .input-group input {
      font-size: 14px;
      padding: 10px 12px;
    }
  }
  .input-group input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
  }

  /* BUTTONS */
  .btn {
    padding: 10px 20px;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    transition: var(--transition);
    border: 1px solid transparent;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  @media (max-width: 480px) {
    .btn {
      padding: 8px 16px;
      font-size: 13px;
    }
  }
  .btn:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .btn-primary {
    background: var(--slate-900);
    color: white;
  }
  .btn-primary:hover:not(:disabled) {
    background: black;
  }
  .btn-glow {
    box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  }
  .btn-lg {
    padding: 14px 28px;
    font-size: 15px;
    border-radius: 10px;
  }
  @media (max-width: 480px) {
    .btn-lg {
      padding: 12px 20px;
      font-size: 14px;
    }
  }
  .btn-outline {
    background: white;
    border-color: var(--slate-200);
    color: var(--slate-700);
  }
  .btn-outline:hover {
    background: var(--slate-50);
  }

  /* TRANSITION CARD */
  .transition-card {
    text-align: center;
  }
  .part-stat-summary {
    background: var(--slate-50);
    border-radius: 12px;
    padding: 14px;
    margin: 16px auto;
    max-width: 280px;
    border: 1px solid var(--slate-200);
  }
  .part-stat-summary p {
    font-size: 14px;
    color: var(--slate-700);
    margin-bottom: 8px;
  }
  .mini-bar {
    width: 100%;
    height: 6px;
    background: var(--slate-200);
    border-radius: 4px;
    overflow: hidden;
  }
  .mini-fill {
    height: 100%;
    border-radius: 4px;
  }
  .mini-fill.success {
    background: var(--success);
  }
  .next-prompt {
    font-size: 15px;
    color: var(--slate-600);
    margin-bottom: 25px;
  }

  /* TRIANGLE CHART PART */
  .triangle-chart-container {
    background: var(--slate-50);
    border-radius: 12px;
    padding: 20px;
    max-height: 450px;
    max-width: 1000px;
    overflow-y: auto;
    border: 2px dashed var(--slate-200);
    margin-bottom: 20px;
  }
  @media (max-width: 480px) {
    .triangle-chart-container {
      max-height: 350px;
      padding: 16px;
      max-width: 100%;
    }
  }
  .triangle-chart {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  .chart-row {
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: space-between;
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: 8px;
    padding: 10px 14px;
    cursor: pointer;
    transition: var(--transition);
    outline: none;
  }
  .chart-row:hover {
    border-color: var(--primary);
    transform: scale(1.01);
  }
  .chart-row.selected {
    border-color: var(--success);
    background: var(--success-bg);
  }
  .row-indicator {
    font-size: 11px;
    font-weight: 750;
    color: var(--slate-600);
    min-width: 50px;
    text-align: left;
  }
  .letter-char {
    font-size: 20px;
    font-weight: 750;
    font-family: sans-serif;
    margin: 0 6px;
  }
  @media (max-width: 480px) {
    .letter-char {
      font-size: 16px;
      margin: 0 4px;
    }
  }
  .checkbox {
    width: 24px;
    height: 24px;
    border: 2px solid var(--slate-300);
    border-radius: 6px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: white;
    font-size: 14px;
    transition: var(--transition);
    flex-shrink: 0;
    margin-left: auto;
  }
  .chart-row.selected .checkbox {
    background: var(--success);
    border-color: var(--success);
    color: white;
  }
  .actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    gap: 10px;
  }
  @media (max-width: 480px) {
    .actions {
      flex-direction: column;
      gap: 12px;
    }
    .actions .btn {
      width: 100%;
    }
  }

  /* RESULTS CARD */
  .results-card {
    text-align: center;
  }
  .date-tag {
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    color: var(--slate-600);
    background: var(--slate-100);
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 24px;
  }
  .results-main {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 24px;
    margin-bottom: 25px;
    background: var(--slate-50);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid var(--slate-100);
  }
  @media (max-width: 640px) {
    .results-main {
      gap: 16px;
      padding: 16px;
    }
  }

  .individual-scores {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
  }
  @media (max-width: 480px) {
    .individual-scores {
      flex-direction: column;
      gap: 12px;
    }
  }
  .score-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  .score-item .score-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--slate-600);
    text-transform: uppercase;
  }
  .score-item .score-value {
    font-size: 28px;
    font-weight: 800;
    color: var(--primary);
  }
  @media (max-width: 480px) {
    .score-item .score-value {
      font-size: 24px;
    }
  }

  /* Circle score progress */
  .score-circle-wrapper {
    position: relative;
    width: 110px;
    height: 110px;
  }
  @media (max-width: 480px) {
    .score-circle-wrapper {
      width: 90px;
      height: 90px;
    }
  }
  .score-circle {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
  }
  .score-circle circle {
    fill: none;
    stroke-width: 6;
  }
  .score-circle .bg-track {
    stroke: var(--slate-200);
  }
  .score-circle .fg-fill {
    stroke-linecap: round;
    transition: stroke-dashoffset 1s ease-out;
  }
  .score-circle .fg-fill.normal { stroke: var(--success); }
  .score-circle .fg-fill.mild { stroke: var(--mild-warning); }
  .score-circle .fg-fill.severe { stroke: var(--fail); }

  .score-value-wrap {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .score-percent {
    font-size: 24px;
    font-weight: 800;
    color: var(--slate-900);
    line-height: 1;
  }
  @media (max-width: 480px) {
    .score-percent {
      font-size: 20px;
    }
  }
  .score-label {
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--slate-600);
    margin-top: 4px;
  }

  .diagnosis-box {
    text-align: left;
    flex: 1;
  }
  .diagnosis-box .label {
    font-size: 10px;
    font-weight: 750;
    text-transform: uppercase;
    color: var(--slate-600);
    display: block;
    margin-bottom: 4px;
  }
  .diagnosis-box h3 {
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 6px;
  }
  @media (max-width: 480px) {
    .diagnosis-box h3 {
      font-size: 16px;
    }
  }
  .diagnosis-box h3.normal { color: var(--success-text); }
  .diagnosis-box h3.mild { color: var(--mild-warning-text); }
  .diagnosis-box h3.severe { color: var(--fail-text); }
  .diagnosis-box .explanation {
    font-size: 13px;
    color: var(--slate-600);
    line-height: 1.5;
  }
  @media (max-width: 480px) {
    .diagnosis-box .explanation {
      font-size: 12px;
    }
  }

  .results-card .actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin-top: 30px;
  }

  /* COLOR WRAPS */
  .text-green { color: var(--success-text); }
</style>