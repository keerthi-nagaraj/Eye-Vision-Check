import { browser } from '$app/environment';
import { writable } from 'svelte/store';

type ThemeMode = 'light' | 'dark';

const defaultTheme: ThemeMode = 'light';
const storedTheme = browser ? localStorage.getItem('theme') : null;
const initialTheme: ThemeMode = storedTheme === 'dark' ? 'dark' : defaultTheme;

export const theme = writable<ThemeMode>(initialTheme);

if (browser) {
	theme.subscribe((value) => {
		localStorage.setItem('theme', value);
	});
}
