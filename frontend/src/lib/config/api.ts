/** API base URL — browser uses Vite proxy `/api`; override with VITE_API_BASE_URL if needed. */
export const API_BASE =
	(typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) ||
	'/api';

export function apiUrl(path: string): string {
	const base = API_BASE.replace(/\/$/, '');
	const p = path.startsWith('/') ? path : `/${path}`;
	return `${base}${p}`;
}
