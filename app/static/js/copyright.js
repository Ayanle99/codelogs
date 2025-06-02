const startYear = 2025;
const currentYear = new Date().getFullYear();
const yearText = currentYear > startYear ? `${startYear}–present` : `${startYear}`;
document.getElementById('copyrightYear').textContent = yearText;
