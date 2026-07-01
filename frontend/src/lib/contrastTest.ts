export type ContrastPattern = {
  letters: string[];
  contrast: number;
  spatialFrequency?: number; // cycles per degree (cpd)
  fontSize?: number; // pixels
};

export class ContrastTest {
  // Configurable constants
  private static readonly INITIAL_CONTRAST = 0.5; // Start at 50% contrast
  private static readonly INITIAL_STEP_SIZE = 0.1; // Initial step size
  private static readonly MIN_CONTRAST = 0.02; // 2% - minimum visible
  private static readonly MAX_CONTRAST = 1.0; // 100% - maximum
  private static readonly REQUIRED_REVERSALS = 3; // Standard clinical protocol: 3 reversals
  private static readonly SPATIAL_FREQUENCIES = [1.5, 3, 6, 12, 18]; // Based on clinical standards
  private static readonly START_SPATIAL_INDEX = 2; // Start at 6 cpd (middle)
  private static readonly BASE_FONT_SIZE = 48; // Base size at 6 cpd in pixels
  private static readonly STEP_REDUCTION_THRESHOLD = 2; // Reversals before reducing step size
  private static readonly MIN_STEP_SIZE = 0.02; // Minimum step size
  private static readonly STEP_REDUCTION_FACTOR = 0.5; // Factor to reduce step size by
  private static readonly MIN_REVERSALS_FOR_THRESHOLD = 2; // Minimum reversals for threshold calculation
  private static readonly REVERSAL_COUNT_FOR_THRESHOLD = 4; // Number of reversals to average
  private static readonly ADAPTIVE_RANGE = 0.4; // Range around threshold for adaptive patterns
  private static readonly ADAPTIVE_STEPS = 10; // Number of steps in adaptive pattern generation
  private static readonly MAX_LETTER_COUNT = 10; // Maximum letters in a pattern

  // Adaptive testing parameters
  private currentContrast = ContrastTest.INITIAL_CONTRAST;
  private stepSize = ContrastTest.INITIAL_STEP_SIZE;
  private minContrast = ContrastTest.MIN_CONTRAST;
  private maxContrast = ContrastTest.MAX_CONTRAST;
  private reversals = 0; // Track direction changes for threshold calculation
  private lastDirection: 'up' | 'down' | null = null;
  private reversalThresholds: number[] = []; // Store contrast values at reversals
  private adaptiveMode = false; // Toggle between fixed and adaptive modes
  private requiredReversals = ContrastTest.REQUIRED_REVERSALS;
  private testComplete = false; // Test completion flag

  // Spatial frequencies (cycles per degree - cpd)
  private spatialFrequencies = ContrastTest.SPATIAL_FREQUENCIES;
  private currentSpatialFrequencyIndex = ContrastTest.START_SPATIAL_INDEX;
  private multiFrequencyMode = false; // Toggle for multi-frequency testing

  // Character pools for variety
  private lettersPool = "ABCDEFGHJKLMNOPRSTUVWXYZ".split("");
  private numbersPool = "23456789".split(""); // Exclude 0,1 to avoid confusion
  private allChars = "ABCDEFGHJKLMNOPRSTUVWXYZ23456789".split("");

  reset() {
    this.currentContrast = ContrastTest.INITIAL_CONTRAST;
    this.stepSize = ContrastTest.INITIAL_STEP_SIZE;
    this.reversals = 0;
    this.lastDirection = null;
    this.reversalThresholds = [];
    this.adaptiveMode = false;
    this.testComplete = false;
    this.currentSpatialFrequencyIndex = ContrastTest.START_SPATIAL_INDEX;
    this.index = 0; // Reset index to start from 1 letter
  }

  enableAdaptiveMode() {
    this.adaptiveMode = true;
    this.reset();
  }

  enableMultiFrequencyMode() {
    this.multiFrequencyMode = true;
    this.reset();
  }

  disableAdaptiveMode() {
    this.adaptiveMode = false;
  }

  // Spatial frequency management
  getCurrentSpatialFrequency(): number {
    return this.spatialFrequencies[this.currentSpatialFrequencyIndex];
  }

  nextSpatialFrequency(): boolean {
    if (this.currentSpatialFrequencyIndex < this.spatialFrequencies.length - 1) {
      this.currentSpatialFrequencyIndex++;
      // Reset adaptive parameters for new frequency
      this.reversals = 0;
      this.lastDirection = null;
      this.reversalThresholds = [];
      this.currentContrast = ContrastTest.INITIAL_CONTRAST;
      this.stepSize = ContrastTest.INITIAL_STEP_SIZE;
      this.testComplete = false;
      return true;
    }
    return false;
  }

  // Convert spatial frequency to font size (approximate)
  spatialFrequencyToFontSize(cpd: number): number {
    return Math.round(ContrastTest.BASE_FONT_SIZE * (6 / cpd));
  }

  // Adaptive staircase method
  updateDifficulty(correct: boolean) {
    if (!this.adaptiveMode) return;

    const direction = correct ? 'down' : 'up'; // Correct = harder (lower contrast), Incorrect = easier (higher contrast)

    // Check for reversal
    if (this.lastDirection && this.lastDirection !== direction) {
      this.reversals++;
      this.reversalThresholds.push(this.currentContrast);

      // Reduce step size after reversals for finer precision (clinical standard)
      if (this.reversals >= ContrastTest.STEP_REDUCTION_THRESHOLD) {
        this.stepSize = Math.max(ContrastTest.MIN_STEP_SIZE, this.stepSize * ContrastTest.STEP_REDUCTION_FACTOR);
      }

      // Check if test is complete (3-reversal protocol)
      if (this.reversals >= this.requiredReversals) {
        this.testComplete = true;
      }
    }

    this.lastDirection = direction;

    // Adjust contrast
    if (correct) {
      this.currentContrast = Math.max(this.minContrast, this.currentContrast - this.stepSize);
    } else {
      this.currentContrast = Math.min(this.maxContrast, this.currentContrast + this.stepSize);
    }
  }

  isTestComplete(): boolean {
    return this.testComplete;
  }

  getCurrentContrast() {
    return this.currentContrast;
  }

  // Calculate threshold from reversals (average of last few reversals)
  getThreshold(): number {
    if (this.reversalThresholds.length < ContrastTest.MIN_REVERSALS_FOR_THRESHOLD) return this.currentContrast;

    // Use last 4 reversals for threshold calculation
    const recentReversals = this.reversalThresholds.slice(-ContrastTest.REVERSAL_COUNT_FOR_THRESHOLD);
    const sum = recentReversals.reduce((a, b) => a + b, 0);
    return sum / recentReversals.length;
  }

  // Fixed levels for backward compatibility
  private levels = [0.8,0.8, 0.7, 0.6, 0.5,0.4, 0.4, 0.3, 0.2, 0.1];
  private index = 0;

  getLevel() {
    return this.levels[this.index];
  }

  next(): number | null {
    if (this.adaptiveMode) {
      return this.getCurrentContrast();
    }

    this.index++;
    if (this.index >= this.levels.length) return null;
    return this.getLevel();
  }

  generateAll(): ContrastPattern[] {
    const allPatterns: ContrastPattern[] = [];

    if (this.adaptiveMode) {
      // Generate adaptive patterns based on current threshold
      // Create a range around the estimated threshold
      const threshold = this.getThreshold();
      const minC = Math.max(this.minContrast, threshold - ContrastTest.ADAPTIVE_RANGE);
      const maxC = Math.min(this.maxContrast, threshold + ContrastTest.ADAPTIVE_RANGE);

      for (let i = 0; i < ContrastTest.ADAPTIVE_STEPS; i++) {
        const contrast = minC + (i / (ContrastTest.ADAPTIVE_STEPS - 1)) * (maxC - minC);
        const letterCount = i + 1; // Fixed progression: 1, 2, 3, ..., 10
        const letters = [...this.allChars]
          .sort(() => Math.random() - 0.5)
          .slice(0, letterCount);
        allPatterns.push({ letters, contrast });
      }
    } else {
      // Fixed levels for backward compatibility
      for (let i = 0; i < this.levels.length; i++) {
        const contrast = this.levels[i];
        const letterCount = i + 1;
        const letters = [...this.allChars]
          .sort(() => Math.random() - 0.5)
          .slice(0, letterCount);
        allPatterns.push({ letters, contrast });
      }
    }

    return allPatterns;
  }

  generate(letterCount?: number): ContrastPattern {
    const contrast = this.adaptiveMode ? this.getCurrentContrast() : this.getLevel();

    // Fixed letter count progression from 1 to 10
    let actualLetterCount = letterCount;
    if (!letterCount) {
      if (this.adaptiveMode) {
        // Use index-based progression for consistent 1-10 letter count
        actualLetterCount = Math.min(ContrastTest.MAX_LETTER_COUNT, Math.max(1, this.index + 1));
      } else {
        actualLetterCount = this.index + 1;
      }
    }

    const letters = [...this.allChars]
      .sort(() => Math.random() - 0.5)
      .slice(0, actualLetterCount);

    // Add spatial frequency and font size if in multi-frequency mode
    const spatialFrequency = this.multiFrequencyMode ? this.getCurrentSpatialFrequency() : undefined;
    const fontSize = spatialFrequency ? this.spatialFrequencyToFontSize(spatialFrequency) : undefined;

    return { letters, contrast, spatialFrequency, fontSize };
  }

  contrastToLogCS(c: number) {
    return Math.log10(1 / c);
  }
}
