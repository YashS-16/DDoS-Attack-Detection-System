// 🔔 Notification permission
if ("Notification" in window) {
    Notification.requestPermission();
}

let riskChart = null;
let attackChart = null;
let lastAlertTime = 0;

// format time
function formatTime(t) {
    return new Date(t).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// RISK TREND
function updateRiskTrendChart(logs) {
    const ctx = document.getElementById('riskTrendChart').getContext('2d');

    const recent = logs.slice(-20);

    const labels = recent.map(l => formatTime(l.timestamp));
    const data = recent.map(l => Number(l.risk_score) || 0);

    if (!riskChart) {
        riskChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    borderColor: '#f97316',
                    tension: 0.4,
                    pointRadius: 0,
                    fill: true,
                    backgroundColor: 'rgba(249,115,22,0.08)'
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        ticks: {
                            maxTicksLimit: 5,
                            color: '#64748b'
                        },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: '#64748b' },
                        grid: { color: '#1e293b' }
                    }
                }
            }
        });
    } else {
        riskChart.data.labels = labels;
        riskChart.data.datasets[0].data = data;
        riskChart.update();
    }
}

// ATTACK DISTRIBUTION
function updateAttackChart(logs) {
    const ctx = document.getElementById('attackChart').getContext('2d');

    const counts = {};

    logs.forEach(log => {
        const type = log.attack_type || "Normal";
        counts[type] = (counts[type] || 0) + 1;
    });

    if (!attackChart) {
        attackChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    data: Object.values(counts),
                    backgroundColor: ['#22c55e','#f59e0b','#ef4444','#38bdf8']
                }]
            },
            options: {
                plugins: { legend: { display: false } }
            }
        });
    } else {
        attackChart.data.labels = Object.keys(counts);
        attackChart.data.datasets[0].data = Object.values(counts);
        attackChart.update();
    }
}

// 🔥 TOP ATTACKER
function getTopAttacker(logs) {
    const counts = {};

    logs.forEach(log => {
        const ip = log.ip || 'unknown';
        counts[ip] = (counts[ip] || 0) + 1;
    });

    let top = null;
    let max = 0;

    for (let ip in counts) {
        if (counts[ip] > max) {
            max = counts[ip];
            top = ip;
        }
    }

    return { ip: top, count: max };
}

// 📋 LOGS
function renderLogs(logs) {
    const el = document.getElementById('logs');

    const latest = logs.slice(-10).reverse();

    el.innerHTML = latest.map(log => `
        <div class="log-entry">
            <span>${formatTime(log.timestamp)}</span>
            <span>${log.ip}</span>
            <span>${log.attack_type}</span>
            <span>${Number(log.risk_score).toFixed(2)}</span>
        </div>
    `).join('');
}

// 🔔 ALERT
function triggerAlert(log) {
    const now = Date.now();

    if (now - lastAlertTime < 20000) return;

    if (Number(log.risk_score) >= 70) {
        lastAlertTime = now;

        if (Notification.permission === "granted") {
            new Notification("DDoS Alert", {
                body: `${log.attack_type} | Risk ${log.risk_score}`
            });
        }
    }
}

// 🚀 MAIN
async function fetchData() {
    try {
        const res = await fetch('/api/data');
        const data = await res.json();

        if (!data.logs || data.logs.length === 0) return;

        const logs = data.logs;
        const last = logs[logs.length - 1];

        document.getElementById('risk').innerText = last.risk_score;
        document.getElementById('attack').innerText = last.attack_type;
        document.getElementById('ip').innerText = last.ip;
        document.getElementById('severity').innerText = last.severity;

        updateRiskTrendChart(logs);
        updateAttackChart(logs);
        renderLogs(logs);

        const top = getTopAttacker(logs);
        document.getElementById('top-ip').innerText = top.ip || '--';
        document.getElementById('top-count').innerText = top.count || 0;

        triggerAlert(last);

    } catch (err) {
        console.error("Fetch error:", err);
    }
}

// 🔄 refresh every 3s
setInterval(fetchData, 7000);
fetchData();