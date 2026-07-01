import { apiUrl } from '$lib/config/api';
import type { ResultsStats, TestResult, TestResultInput, UserSettings } from '$lib/types/test';

const fetchOpts: RequestInit = { credentials: 'include' };

function normalizeResult(raw: Record<string, unknown>): TestResult {
	return {
		id: String(raw.id ?? ''),
		testType: String(raw.testType ?? raw.test_type ?? 'unknown'),
		result: String(raw.result ?? raw.diagnosis ?? 'Completed'),
		score: Number(raw.score ?? 0),
		timestamp: String(raw.timestamp ?? new Date().toISOString()),
		details: raw.details,
		totalQuestions: Number(raw.totalQuestions ?? raw.total_questions ?? 0),
		correctAnswers: Number(raw.correctAnswers ?? raw.correct_answers ?? 0),
		testData: (raw.testData ?? raw.test_data) as Record<string, unknown> | undefined,
		difficulty: raw.difficulty as string | undefined,
		diagnosis: String(raw.diagnosis ?? raw.result ?? ''),
		userId: String(raw.userId ?? raw.user_id ?? 'anonymous')
	};
}

function toSubmitPayload(result: TestResultInput) {
	return {
		user_id: result.userId ?? 'anonymous',
		test_type: result.testType,
		score: result.score,
		diagnosis: result.diagnosis ?? result.result,
		result: result.result,
		total_questions: result.totalQuestions ?? 0,
		correct_answers: result.correctAnswers ?? 0,
		test_data: result.testData ?? result.details ?? {},
		difficulty: result.difficulty ?? 'standard',
		duration_seconds: 0
	};
}

async function parseJson<T>(response: Response): Promise<T> {
	if (!response.ok) {
		throw new Error(`HTTP error! status: ${response.status}`);
	}
	const data = await response.json();
	if (!data.success) {
		throw new Error(data.message || 'Request failed');
	}
	return data;
}

export async function fetchTestResults(userId?: string): Promise<TestResult[]> {
	const params = new URLSearchParams();
	if (userId) params.set('user_id', userId);
	const qs = params.toString();
	const response = await fetch(apiUrl(qs ? `/results/?${qs}` : '/results/'), fetchOpts);
	const data = await parseJson<{ data: { results: Record<string, unknown>[] } }>(response);
	return data.data.results.map(normalizeResult);
}

export async function submitTestResult(result: TestResultInput): Promise<unknown> {
	const response = await fetch(apiUrl('/tests/submit'), {
		...fetchOpts,
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(toSubmitPayload(result))
	});
	const data = await parseJson<{ data: unknown }>(response);
	return data.data;
}

export async function deleteTestResult(id: string): Promise<void> {
	const response = await fetch(apiUrl(`/results/${id}`), {
		...fetchOpts,
		method: 'DELETE'
	});
	await parseJson(response);
}

export async function clearAllResults(userId?: string): Promise<{ success: boolean; message?: string }> {
	const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
	const response = await fetch(apiUrl(`/results/clear${params}`), {
		...fetchOpts,
		method: 'DELETE'
	});
	return response.json();
}

export async function fetchUserCount(): Promise<number> {
	const response = await fetch(apiUrl('/users/count'), fetchOpts);
	const data = await parseJson<{ data: { user_count: number } }>(response);
	return data.data.user_count;
}

export async function fetchResultsStats(): Promise<ResultsStats> {
	const response = await fetch(apiUrl('/results/stats'), fetchOpts);
	const data = await parseJson<{
		data: {
			total_results: number;
			ishihara_count: number;
			tritan_count: number;
			hue_count: number;
			webcam_count?: number;
			amsler_count?: number;
			contrast_count?: number;
		};
	}>(response);
	return {
		totalResults: data.data.total_results,
		ishiharaCount: data.data.ishihara_count,
		tritanCount: data.data.tritan_count,
		hueCount: data.data.hue_count,
		webcamCount: data.data.webcam_count ?? 0,
		amslerCount: data.data.amsler_count ?? 0,
		contrastCount: data.data.contrast_count ?? 0
	};
}

export async function fetchUserSettings(userId?: string): Promise<UserSettings> {
	const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
	const response = await fetch(apiUrl(`/settings${params}`), fetchOpts);
	if (!response.ok) {
		return { name: '', age: 0, notifications: true, darkMode: false };
	}
	const data = await response.json();
	if (!data.success) {
		return { name: '', age: 0, notifications: true, darkMode: false };
	}
	return {
		name: data.data.name ?? '',
		age: data.data.age ?? 0,
		notifications: data.data.notifications ?? true,
		darkMode: data.data.darkMode ?? false
	};
}

export async function saveUserSettings(
	settings: Partial<UserSettings>,
	userId?: string
): Promise<void> {
	const response = await fetch(apiUrl('/settings'), {
		...fetchOpts,
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			user_id: userId ?? 'anonymous',
			...settings,
			dark_mode: settings.darkMode
		})
	});
	await parseJson(response);
}
