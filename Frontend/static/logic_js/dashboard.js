// dashboard.js — minimal charts, live updates, modern UI integration
let riskChart = null;
let attackChart = null;

// helper to format timestamp nicely
function formatTime(isoString) {
    if (!isoString) return 'just now';
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch(e) {
        return isoString.substring(0, 8);
    }
}

// build risk trend chart (line) using last N logs (max 15 points)
function updateRiskTrendChart(logs) {
    const canvas = document.getElementById('riskTrendChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // take recent logs (show last 12 entries for clarity)
    const recentLogs = logs.slice(-14);
    if (recentLogs.length === 0) {
        if (riskChart) riskChart.destroy();
        return;
    }
    
    const labels = recentLogs.map((log, idx) => {
        // either short time or index
        if (log.timestamp) return formatTime(log.timestamp);
        return `#${idx+1}`;
    });
    const riskData = recentLogs.map(log => {
        let riskVal = log.risk_score;
        if (riskVal === undefined || riskVal === null) return 0;
        // ensure numeric
        return typeof riskVal === 'number' ? riskVal : parseFloat(riskVal);
    });
    
    if (riskChart) riskChart.destroy();
    
    riskChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Risk score',
                data: riskData,
                borderColor: '#f97316',
                backgroundColor: 'rgba(249,115,22,0.05)',
                borderWidth: 2.5,
                pointRadius: 3,
                pointBackgroundColor: '#fb923c',
                pointBorderColor: '#0f172a',
                pointHoverRadius: 6,
                tension: 0.2,
                fill: true,
                pointBorderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { labels: { color: '#cbd5e1', font: { size: 11 } } },
                tooltip: { backgroundColor: '#0f172a', titleColor: '#e2e8f0', bodyColor: '#94a3b8' }
            },
            scales: {
                y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' }, title: { display: true, text: 'Risk index', color: '#7e8aa2' } },
                x: { ticks: { color: '#7e8aa2', maxRotation: 35, autoSkip: true }, grid: { display: false } }
            }
        }
    });
}

// pie chart: attack type distribution (counts)
function updateAttackDistributionChart(logs) {
    const canvas = document.getElementById('attackPieChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (!logs || logs.length === 0) {
        if (attackChart) attackChart.destroy();
        return;
    }
    
    const attackCounts = new Map();
    logs.forEach(log => {
        let type = log.prediction || log.attack_type || 'Normal';
        if (type === 'unknown' || type === '--') type = 'Unknown';
        attackCounts.set(type, (attackCounts.get(type) || 0) + 1);
    });
    
    const labels = Array.from(attackCounts.keys());
    const values = Array.from(attackCounts.values());
    
    if (attackChart) attackChart.destroy();
    
    const backgroundColors = ['#38bdf8', '#f97316', '#a855f7', '#22c55e', '#ef4444', '#eab308', '#ec489a'];
    const borderColors = ['#0f172a', '#0f172a', '#0f172a', '#0f172a', '#0f172a', '#0f172a', '#0f172a'];
    
    attackChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors.slice(0, labels.length),
                borderColor: borderColors.slice(0, labels.length),
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 11 }, boxWidth: 12 } },
                tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw} events (${((ctx.raw/logs.length)*100).toFixed(1)}%)` } }
            }
        }
    });
}

// render logs with modern minimal style (enhanced readability)
function renderLogsList(logs) {
    const logsContainer = document.getElementById('logs');
    if (!logsContainer) return;
    
    if (!logs || logs.length === 0) {
        logsContainer.innerHTML = '<div class="log-placeholder">📭 No logs received yet. Waiting for telemetry...</div>';
        return;
    }
    
    // show most recent first (reversed)
    const reversed = [...logs].reverse();
    let html = '';
    for (let log of reversed.slice(0, 35)) { // show last 35 logs
        const attackName = log.prediction || log.attack_type || 'Benign';
        const risk = log.risk_score !== undefined && log.risk_score !== null ? log.risk_score : '—';
        const timeStr = log.timestamp ? formatTime(log.timestamp) : '—';
        const severityClass = (log.severity || '').toLowerCase();
        let severityBadge = '';
        if (log.severity) {
            severityBadge = `<span class="log-badge" style="background:${log.severity === 'HIGH' ? '#7f1a1a80' : log.severity === 'MEDIUM' ? '#a1620780' : '#14532d80'}">${log.severity}</span>`;
        }
        html += `
            <div class="log-entry">
                <div class="log-time">⏱️ ${timeStr}</div>
                <div class="log-badge">⚠️ ${escapeHtml(attackName)}</div>
                ${severityBadge}
                <div class="log-risk">📊 risk ${risk}</div>
                <div style="font-family: monospace; color:#7e8aa2;">🌐 ${escapeHtml(log.ip || 'unknown')}</div>
            </div>
        `;
    }
    logsContainer.innerHTML = html;
}

// simple escape to prevent injection
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

// update severity class on dashboard
function updateSeverityClass(severity) {
    const sevElem = document.getElementById('severity');
    if (!sevElem) return;
    sevElem.classList.remove('low', 'medium', 'high');
    if (severity === 'LOW') sevElem.classList.add('low');
    else if (severity === 'MEDIUM') sevElem.classList.add('medium');
    else if (severity === 'HIGH') sevElem.classList.add('high');
}

// main data fetcher: updates metrics, logs, and charts
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (!data || !data.logs || data.logs.length === 0) {
            // still update placeholders
            document.getElementById('risk').innerText = '—';
            document.getElementById('attack').innerText = '—';
            document.getElementById('ip').innerText = '—';
            updateSeverityClass('');
            renderLogsList([]);
            if (riskChart) riskChart.destroy();
            if (attackChart) attackChart.destroy();
            return;
        }
        
        const logs = data.logs;
        const lastLog = logs[logs.length - 1];
        
        // update top stats
        document.getElementById('attack').innerText = lastLog.prediction || lastLog.attack_type || 'Normal';
        document.getElementById('risk').innerText = (lastLog.risk_score !== undefined && lastLog.risk_score !== null) ? lastLog.risk_score : '—';
        document.getElementById('ip').innerText = lastLog.ip || '—';
        const severityVal = lastLog.severity || '—';
        document.getElementById('severity').innerText = severityVal;
        updateSeverityClass(severityVal);
        
        // render logs list with fresh data
        renderLogsList(logs);
        
        // update both charts (risk trend & attack distribution)
        updateRiskTrendChart(logs);
        updateAttackDistributionChart(logs);
        
        console.log("✅ Dashboard updated, logs:", logs.length);
    } catch (error) {
        console.error('Dashboard fetch error:', error);
        // show graceful offline hint
        const logsDiv = document.getElementById('logs');
        if (logsDiv && !logsDiv.innerHTML.includes('connection issue')) {
            logsDiv.innerHTML = '<div class="log-placeholder">⚠️ Connection issue — waiting for backend data...</div>';
        }
    }
}

// initial load + live interval (2 seconds same as original)
setInterval(fetchData, 2000);
fetchData();  // immediate call

// optional: ensure charts resize on window redraw (avoid glitches)
window.addEventListener('resize', () => {
    if (riskChart) riskChart.resize();
    if (attackChart) attackChart.resize();
});