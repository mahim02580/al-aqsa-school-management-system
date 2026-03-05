// Auto dark-mode (system preference)
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
const savedTheme = localStorage.getItem('theme');

if (savedTheme) {
    document.documentElement.dataset.theme = savedTheme;
} else if (prefersDark) {
    document.documentElement.dataset.theme = 'dark';
}

document.getElementById('themeToggle').onclick = () => {
    const current = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = current;
    localStorage.setItem('theme', current);
};