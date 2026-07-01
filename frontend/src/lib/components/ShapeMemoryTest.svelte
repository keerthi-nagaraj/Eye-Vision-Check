<script lang="ts">
  import { onMount } from "svelte";
  import {
    DISPLAY_TIME,
    TOTAL_QUESTIONS,
    SHAPES,
    generateSequence,
    generateResult,
  } from "$lib/shapeMemoryTest";

  // Test state
  let step = 0; // 0=show mapping, 1..TOTAL_QUESTIONS questions, -1=finished
  let mappingVisible = true;
  let sequence: number[] = [];
  let showSeq = false;
  let userAnswer = "";
  let correctAnswers = 0;
  let results: { sequence: number[]; user: number[]; correct: boolean }[] = [];
  let finalResult: {
    accuracy: number;
    category: string;
    recommendation: string;
  } | null = null;

  function startTest() {
    step = 1;
    mappingVisible = false;
    nextQuestion();
  }

  function nextQuestion() {
    if (step > TOTAL_QUESTIONS) {
      finishTest();
      return;
    }
    // Determine difficulty level (mirroring backend logic)
    let level = step <= 3 ? 3 : step <= 7 ? 4 : 5;
    sequence = generateSequence(level);
    showSeq = true;
    // After DISPLAY_TIME seconds hide and enable answer input
    setTimeout(() => {
      showSeq = false;
    }, DISPLAY_TIME * 1000);
  }

  function submitAnswer() {
    const userSeq = userAnswer
      .trim()
      .split(/\s+/)
      .map(Number)
      .filter((n) => !isNaN(n));
    const isCorrect = JSON.stringify(userSeq) === JSON.stringify(sequence);
    if (isCorrect) correctAnswers += 1;
    results.push({ sequence, user: userSeq, correct: isCorrect });
    userAnswer = "";
    step += 1;
    nextQuestion();
  }

  function finishTest() {
    finalResult = generateResult(correctAnswers, TOTAL_QUESTIONS);
    step = -1;
  }
</script>

{#if mappingVisible}
  <div class="container">
    <h1 class="title">Shape Memory Test</h1>
    <div class="mapping">
      <h2>Shape Mapping</h2>
      <ul>
        {#each Object.entries(SHAPES) as [num, shape]}
          <li>{num} = {shape}</li>
        {/each}
      </ul>
    </div>
    <button class="btn" on:click={startTest}>Start Test</button>
  </div>
{:else if step === -1 && finalResult}
  <div class="container">
    <h1 class="title">Final Result</h1>
    <div class="result">
      <p>Questions: {TOTAL_QUESTIONS}</p>
      <p>Correct Answers: {correctAnswers}</p>
      <p>Wrong Answers: {TOTAL_QUESTIONS - correctAnswers}</p>
      <p>Accuracy: {finalResult.accuracy.toFixed(1)}%</p>
      <p>Category: {finalResult.category}</p>
      <p>Recommendation: {finalResult.recommendation}</p>
    </div>
    <button class="btn" on:click={() => location.reload()}>Retake Test</button>
  </div>
{:else}
  <div class="container">
    <h1 class="title">Question {step} / {TOTAL_QUESTIONS}</h1>
    {#if showSeq}
      <div class="sequence">
        <p>Remember this sequence:</p>
        <p style="font-size: 1.5rem; letter-spacing: 0.2rem;">
          {sequence.join(" ")}
        </p>
      </div>
    {:else}
      <div class="sequence">
        <p>Enter the sequence (space separated numbers):</p>
        <input
          class="input"
          bind:value={userAnswer}
          on:keydown={(e) => e.key === "Enter" && userAnswer && submitAnswer()}
          placeholder="e.g. 1 4 3"
        />
        <button
          class="btn"
          on:click={submitAnswer}
          disabled={!userAnswer.trim()}>Submit</button
        >
      </div>
    {/if}
  </div>
{/if}

<style>
  :global(:root) {
    --primary: #3b82f6;
    --primary-dark: #2563eb;
    --bg: #f5f5f5;
    --card-bg: #ffffff;
    --text: #111827;
    --success: #10b981;
    --error: #ef4444;
    --radius: 12px;
    --transition: all 0.3s ease;
  }
  .container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  }
  .title {
    text-align: center;
    font-size: 1.8rem;
    color: var(--text);
    margin-bottom: 1rem;
  }
  .mapping,
  .sequence,
  .result {
    margin: 1.5rem 0;
    padding: 1rem;
    background: var(--bg);
    border-radius: var(--radius);
  }
  .btn {
    display: inline-block;
    background: var(--primary);
    color: white;
    padding: 0.6rem 1.2rem;
    border-radius: var(--radius);
    cursor: pointer;
    transition: var(--transition);
    border: none;
    font-weight: 600;
  }
  .btn:hover {
    background: var(--primary-dark);
  }
  .input {
    width: 100%;
    padding: 0.5rem;
    margin-top: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: var(--radius);
    font-size: 1rem;
  }
</style>
