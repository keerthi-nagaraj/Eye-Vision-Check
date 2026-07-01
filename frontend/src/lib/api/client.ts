import { apiUrl } from '$lib/config/api';

const fetchOpts: RequestInit = { credentials: 'include' };

export type User = {
	user_id: string;
	email: string;
	name: string;
};

export type TestSubmission = {
	test_type: string;
	score: number;
	diagnosis: string;
	total_questions: number;
	correct_answers: number;
	test_data?: unknown;
	difficulty?: string;
	duration_seconds?: number;
};

export type TestResult = {
	id?: string;
	testType: 'ishihara' | 'tritan' | 'hue' | 'webcam' | 'amsler';
	score: number;
	result: string;
	timestamp?: string;
	details?: unknown;
};

export const apiClient = {
	async healthCheck() {
		const res = await fetch(apiUrl('/health'), fetchOpts);
		return res.json();
	},

	async getUserCount() {
		const res = await fetch(apiUrl('/users/count'), fetchOpts);
		return res.json();
	},

	async getResultsStats() {
		const res = await fetch(apiUrl('/results/stats'), fetchOpts);
		return res.json();
	},

	async submitTestResult(data: TestSubmission) {
		const res = await fetch(apiUrl('/tests/submit'), {
			...fetchOpts,
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
		});
		return res.json();
	},

	async getTestResults(userId = 'anonymous', testType?: string) {
		const params = new URLSearchParams({ user_id: userId });
		if (testType) params.set('test_type', testType);
		const res = await fetch(apiUrl(`/results/?${params}`), fetchOpts);
		return res.json();
	},

	async generateIshiharaPlate(round = 1, difficulty = 'standard') {
		const params = new URLSearchParams({
			round: String(round),
			difficulty
		});
		const res = await fetch(apiUrl(`/tests/generate/ishihara?${params}`), fetchOpts);
		return res.json();
	},

	async generateTritanPlate(round = 1) {
		const res = await fetch(apiUrl(`/tests/generate/tritan?round=${round}`), fetchOpts);
		return res.json();
	},

	async generateHueSpectrum(round = 1, numCaps = 16) {
		const res = await fetch(
			apiUrl(`/tests/generate/hue?round=${round}&num_caps=${numCaps}`),
			fetchOpts
		);
		return res.json();
	},

	async deleteTestResult(id: string) {
		const res = await fetch(apiUrl(`/results/${id}`), {
			...fetchOpts,
			method: 'DELETE'
		});
		return res.json();
	},

	async clearAllTestResults(userId = 'anonymous') {
		const res = await fetch(apiUrl(`/results/clear?user_id=${encodeURIComponent(userId)}`), {
			...fetchOpts,
			method: 'DELETE'
		});
		return res.json();
	}
};
