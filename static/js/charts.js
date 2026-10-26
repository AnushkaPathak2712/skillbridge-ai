/**
 * SkillBridge AI - Charts Library
 * Handles all chart visualizations including radar charts, bar charts,
 * line charts, heatmaps, and progress tracking visualizations
 */

// ============================================================
// Chart.js Initialization Helper
// ============================================================

// Ensure Chart.js is loaded
if (typeof Chart === 'undefined') {
    console.error('Chart.js is not loaded. Please include Chart.js library.');
}

// ============================================================
// Radar Chart for Skill Comparison
// ============================================================

/**
 * Creates a radar chart comparing student skills vs industry benchmarks
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} skills - Array of skill names
 * @param {Array} studentScores - Array of student scores (0-4)
 * @param {Array} industryScores - Array of industry benchmark scores (0-4)
 * @param {Array} cohortScores - Optional array of cohort average scores
 */
function createRadarChart(canvasId, skills, studentScores, industryScores, cohortScores = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with id "${canvasId}" not found`);
        return null;
    }

    const datasets = [
        {
            label: 'Your Score',
            data: studentScores,
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            borderWidth: 2,
            pointBackgroundColor: '#8b5cf6',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
        },
        {
            label: 'Industry Benchmark',
            data: industryScores,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 2,
            pointBackgroundColor: '#ef4444',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
        }
    ];

    if (cohortScores) {
        datasets.push({
            label: 'Cohort Average',
            data: cohortScores,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            borderWidth: 2,
            borderDash: [5, 5],
            pointBackgroundColor: '#f59e0b',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 3,
            pointHoverRadius: 5
        });
    }

    return new Chart(ctx, {
        type: 'radar',
        data: { labels: skills, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 4,
                    ticks: { stepSize: 1, backdropColor: 'transparent' },
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(1)}/4`;
                        }
                    }
                },
                legend: { position: 'bottom' }
            }
        }
    });
}

// ============================================================
// Bar Chart for Skill Gaps
// ============================================================

/**
 * Creates a horizontal bar chart showing skill gaps
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} skills - Array of skill names
 * @param {Array} gaps - Array of gap values
 */
function createGapBarChart(canvasId, skills, gaps) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    // Color based on gap severity
    const backgroundColors = gaps.map(gap => {
        if (gap >= 2) return 'rgba(239, 68, 68, 0.7)';
        if (gap >= 1.5) return 'rgba(249, 115, 22, 0.7)';
        if (gap >= 0.8) return 'rgba(234, 179, 8, 0.7)';
        return 'rgba(34, 197, 94, 0.7)';
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: skills,
            datasets: [{
                label: 'Skill Gap (Industry - Your Score)',
                data: gaps,
                backgroundColor: backgroundColors,
                borderRadius: 8,
                borderWidth: 0
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Gap: ${context.raw.toFixed(2)} points`;
                        }
                    }
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Gap Size', font: { size: 12 } },
                    beginAtZero: true,
                    max: 4
                }
            }
        }
    });
}

// ============================================================
// Progress Line Chart
// ============================================================

/**
 * Creates a line chart showing progress over time
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} dates - Array of assessment dates
 * @param {Array} scores - Array of readiness scores
 * @param {Array} projectedScores - Optional array of projected scores
 */
function createProgressChart(canvasId, dates, scores, projectedScores = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const datasets = [
        {
            label: 'Your Progress',
            data: scores,
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#8b5cf6',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 7
        }
    ];

    if (projectedScores) {
        datasets.push({
            label: 'Projected Path',
            data: projectedScores,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.05)',
            borderWidth: 2,
            borderDash: [5, 5],
            fill: false,
            pointRadius: 3,
            pointBackgroundColor: '#f59e0b'
        });
    }

    return new Chart(ctx, {
        type: 'line',
        data: { labels: dates, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Readiness Score (%)' },
                    min: 0,
                    max: 100,
                    ticks: { stepSize: 20 }
                },
                x: {
                    title: { display: true, text: 'Assessment Date' }
                }
            }
        }
    });
}

// ============================================================
// Heatmap Chart for Faculty Dashboard
// ============================================================

/**
 * Creates a heatmap-style bar chart for department-wide gaps
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} skills - Array of skill names
 * @param {Array} gaps - Array of average gap values
 * @param {Array} percentages - Array of percentage of students with critical gaps
 */
function createHeatmapChart(canvasId, skills, gaps, percentages = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const backgroundColors = gaps.map(gap => {
        if (gap >= 2) return '#ef4444';
        if (gap >= 1.2) return '#f97316';
        if (gap >= 0.6) return '#eab308';
        return '#22c55e';
    });

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: skills,
            datasets: [{
                label: 'Average Department Gap',
                data: gaps,
                backgroundColor: backgroundColors,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = `Gap: ${context.raw.toFixed(2)}`;
                            if (percentages && percentages[context.dataIndex]) {
                                label += ` | ${percentages[context.dataIndex]}% of students need improvement`;
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Gap Size' },
                    beginAtZero: true,
                    max: 4
                }
            }
        }
    });
}

// ============================================================
// Doughnut Chart for Readiness Score
// ============================================================

/**
 * Creates a doughnut chart showing readiness score
 * @param {string} canvasId - ID of the canvas element
 * @param {number} score - Readiness score (0-100)
 */
function createReadinessDoughnut(canvasId, score) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const remaining = 100 - score;
    const color = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444';

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Your Readiness', 'Gap Remaining'],
            datasets: [{
                data: [score, remaining],
                backgroundColor: [color, '#e5e7eb'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: { enabled: false },
                legend: { position: 'bottom' }
            }
        }
    });
}

// ============================================================
// Comparison Chart for Side-by-Side Assessment
// ============================================================

/**
 * Creates a grouped bar chart comparing two assessments
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} skills - Array of skill names
 * @param {Array} scores1 - First assessment scores
 * @param {Array} scores2 - Second assessment scores
 * @param {string} name1 - Name of first assessment
 * @param {string} name2 - Name of second assessment
 */
function createComparisonChart(canvasId, skills, scores1, scores2, name1, name2) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: skills,
            datasets: [
                {
                    label: name1,
                    data: scores1,
                    backgroundColor: 'rgba(139, 92, 246, 0.7)',
                    borderRadius: 8
                },
                {
                    label: name2,
                    data: scores2,
                    backgroundColor: 'rgba(34, 197, 94, 0.7)',
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toFixed(1)}/4`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Skill Score (0-4)' },
                    beginAtZero: true,
                    max: 4,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// ============================================================
// Weekly Progress Chart
// ============================================================

/**
 * Creates a chart showing weekly learning progress
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} weeks - Week labels
 * @param {Array} completedTasks - Number of completed tasks per week
 * @param {Array} plannedTasks - Planned tasks per week
 */
function createWeeklyProgressChart(canvasId, weeks, completedTasks, plannedTasks) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: [
                {
                    label: 'Completed Tasks',
                    data: completedTasks,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#22c55e'
                },
                {
                    label: 'Planned Tasks',
                    data: plannedTasks,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.05)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointBackgroundColor: '#8b5cf6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} tasks`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    title: { display: true, text: 'Number of Tasks' },
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

// ============================================================
// Distribution Pie Chart
// ============================================================

/**
 * Creates a pie chart showing gap distribution across skill categories
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} categories - Object with category names and values
 */
function createGapDistributionChart(canvasId, categories) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = Object.keys(categories);
    const values = Object.values(categories);
    const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#8b5cf6', '#3b82f6'];

    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = values.reduce((a, b) => a + b, 0);
                            const percentage = ((context.raw / total) * 100).toFixed(1);
                            return `${context.label}: ${context.raw} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// ============================================================
// Export Chart as Image
// ============================================================

/**
 * Exports a chart as an image (PNG)
 * @param {string} canvasId - ID of the canvas element
 * @param {string} filename - Name for the downloaded file
 */
function exportChartAsImage(canvasId, filename = 'chart.png') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas with id "${canvasId}" not found`);
        return;
    }

    const link = document.createElement('a');
    link.download = filename;
    link.href = canvas.toDataURL('image/png');
    link.click();
}

// ============================================================
// Update Chart Data
// ============================================================

/**
 * Updates an existing chart with new data
 * @param {Object} chart - Chart.js chart instance
 * @param {Array} newLabels - New label array
 * @param {Array} newData - New data array
 * @param {number} datasetIndex - Index of dataset to update (default 0)
 */
function updateChartData(chart, newLabels, newData, datasetIndex = 0) {
    if (!chart) return;

    chart.data.labels = newLabels;
    chart.data.datasets[datasetIndex].data = newData;
    chart.update();
}

// ============================================================
// Animate Chart on Scroll
// ============================================================

/**
 * Creates an intersection observer to animate charts when they come into view
 * @param {string} canvasId - ID of the canvas element
 * @param {Function} createChartFn - Function that creates the chart
 */
function animateChartOnScroll(canvasId, createChartFn) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    let chartCreated = false;
    let chartInstance = null;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !chartCreated) {
                chartInstance = createChartFn();
                chartCreated = true;
                observer.unobserve(canvas);
            }
        });
    }, { threshold: 0.3 });

    observer.observe(canvas);
    return chartInstance;
}

// ============================================================
// Helper: Get Color Based on Gap Value
// ============================================================

/**
 * Returns color based on gap severity
 * @param {number} gap - Gap value
 * @returns {string} CSS color
 */
function getGapColor(gap) {
    if (gap >= 2) return '#ef4444';
    if (gap >= 1.5) return '#f97316';
    if (gap >= 0.8) return '#eab308';
    return '#22c55e';
}

/**
 * Returns background color with opacity for gap
 * @param {number} gap - Gap value
 * @param {number} opacity - Opacity value (0-1)
 * @returns {string} RGBA color
 */
function getGapColorWithOpacity(gap, opacity = 0.7) {
    if (gap >= 2) return `rgba(239, 68, 68, ${opacity})`;
    if (gap >= 1.5) return `rgba(249, 115, 22, ${opacity})`;
    if (gap >= 0.8) return `rgba(234, 179, 8, ${opacity})`;
    return `rgba(34, 197, 94, ${opacity})`;
}

// ============================================================
// Export all functions for use in other scripts
// ============================================================

// Make functions globally available
window.SkillBridgeCharts = {
    createRadarChart,
    createGapBarChart,
    createProgressChart,
    createHeatmapChart,
    createReadinessDoughnut,
    createComparisonChart,
    createWeeklyProgressChart,
    createGapDistributionChart,
    exportChartAsImage,
    updateChartData,
    animateChartOnScroll,
    getGapColor,
    getGapColorWithOpacity
};