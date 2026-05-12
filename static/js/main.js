/**
 * main.js – Global helpers for StockAnalyze
 */

// Format a number with locale commas
function formatNumber(n, decimals = 2) {
  if (n === null || n === undefined || n === 'N/A') return 'N/A';
  return Number(n).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

// Return CSS class string for a change value
function changeClass(chg) {
  const v = parseFloat(chg);
  if (v > 0) return 'text-success';
  if (v < 0) return 'text-danger';
  return 'text-muted';
}

// Initialise Bootstrap tooltips on page load
document.addEventListener('DOMContentLoaded', () => {
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(el => new bootstrap.Tooltip(el));
});
