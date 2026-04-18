import React, { useEffect, useState, useRef } from 'react';
import { fetchLogs, startMonitoring, stopMonitoring, getStatus, LogEntry } from './services/api';
import { Activity, Shield, AlertTriangle, ShieldAlert, Play, Square, ServerCrack } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInterval = useRef<number | null>(null);

  const loadData = async () => {
    try {
      const data = await fetchLogs();
      setLogs(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
      // Optional: set error state, but we don't want to break the UI constantly on polling failures if backend gen is slow.
    }
  };

  const checkStatus = async () => {
    try {
      const { is_running } = await getStatus();
      setIsRunning(is_running);
    } catch (err) {
      console.error("Failed to get status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
    loadData();

    // Poll every 2 seconds
    fetchInterval.current = window.setInterval(() => {
      loadData();
    }, 2000);

    return () => {
      if (fetchInterval.current) clearInterval(fetchInterval.current);
    };
  }, []);

  const handleStart = async () => {
    try {
      await startMonitoring();
      setIsRunning(true);
    } catch (err: any) {
      setError(err.message || "Failed to start monitoring");
    }
  };

  const handleStop = async () => {
    try {
      await stopMonitoring();
      setIsRunning(false);
    } catch (err: any) {
      setError(err.message || "Failed to stop monitoring");
    }
  };

  // Derived metrics
  const latestLog = logs.length > 0 ? logs[logs.length - 1] : null;
  const currentRisk = latestLog ? latestLog.risk_score : 0;
  
  // High risk alerts
  const alerts = logs.filter(l => l.risk_score > 70).slice(-5).reverse();

  // Chart data preparing
  const chartData = logs.slice(-20).map(l => ({
    time: l.timestamp.split(' ')[1] || l.timestamp,
    risk: l.risk_score,
  }));

  if (loading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-cyan-400">Loading Dashboard...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-cyan-500/30">
      
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Shield className="text-white w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">NetGuard Sentinel</h1>
              <p className="text-xs text-slate-400 font-medium">Real-time DDoS AI Detection</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-white/5">
              <div className={`w-2.5 h-2.5 rounded-full ${isRunning ? 'bg-emerald-500 animate-pulse box-shadow-glow-emerald' : 'bg-rose-500'}`} />
              <span className="text-sm font-medium text-slate-300">{isRunning ? 'Active Monitoring' : 'System Offline'}</span>
            </div>
            
            <button
              onClick={isRunning ? handleStop : handleStart}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold transition-all duration-300 ${
                isRunning 
                ? 'bg-rose-500/10 text-rose-500 hover:bg-rose-500/20 border border-rose-500/20' 
                : 'bg-cyan-500 text-white hover:bg-cyan-400 hover:shadow-lg hover:shadow-cyan-500/25 border border-cyan-400/50'
              }`}
            >
              {isRunning ? <Square className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
              {isRunning ? 'Stop Capture' : 'Start Capture'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3">
            <AlertTriangle className="text-red-400 w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <h3 className="text-red-400 font-medium">System Error</h3>
              <p className="text-red-400/80 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Top Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Risk Score Card */}
          <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="flex justify-between items-start mb-4 relative z-10">
              <h3 className="text-slate-400 font-medium">Current Risk Score</h3>
              <Activity className="text-cyan-400 w-5 h-5" />
            </div>
            <div className="flex items-end gap-3 relative z-10">
              <span className={`text-4xl font-bold ${currentRisk > 70 ? 'text-rose-500' : currentRisk > 40 ? 'text-amber-500' : 'text-emerald-400'}`}>
                {currentRisk.toFixed(1)}
              </span>
              <span className="text-sm text-slate-500 mb-1">/ 100</span>
            </div>
            
            {/* Risk Bar */}
            <div className="h-1.5 w-full bg-slate-800 rounded-full mt-5 overflow-hidden">
              <div 
                className={`h-full transition-all duration-1000 ${currentRisk > 70 ? 'bg-rose-500' : currentRisk > 40 ? 'bg-amber-500' : 'bg-emerald-400'}`}
                style={{ width: `${Math.min(currentRisk, 100)}%` }}
              />
            </div>
          </div>

          {/* Last Attack Mode */}
          <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="flex justify-between items-start mb-4 relative z-10">
              <h3 className="text-slate-400 font-medium">Traffic Status</h3>
              <ServerCrack className={`w-5 h-5 ${latestLog?.anomaly ? 'text-rose-500' : 'text-emerald-400'}`} />
            </div>
            <div className="relative z-10">
              <span className="text-2xl font-bold text-white block truncate">
                {latestLog ? latestLog.attack_type : 'Awaiting Data'}
              </span>
              <span className="text-sm mt-1 block text-slate-400">
                {latestLog?.anomaly ? <span className="text-rose-400">Anomaly Detected</span> : <span className="text-emerald-400">Normal Flow</span>}
              </span>
            </div>
          </div>

          {/* Targeted IP */}
          <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="flex justify-between items-start mb-4 relative z-10">
              <h3 className="text-slate-400 font-medium">Source / Attacker IP</h3>
              <ShieldAlert className="text-blue-400 w-5 h-5" />
            </div>
            <div className="relative z-10">
              <span className="text-2xl font-mono font-bold text-white tracking-widest block">
                {latestLog ? latestLog.ip : '0.0.0.0'}
              </span>
              <span className="text-sm mt-1 block text-slate-400">
                Latest monitored source
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chart */}
          <div className="lg:col-span-2 bg-slate-900/40 border border-white/5 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold text-white">Risk Timeline</h3>
              <div className="flex gap-2 items-center">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                <span className="text-xs text-slate-400">Risk Score</span>
              </div>
            </div>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <defs>
                     <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="time" stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#ffffff40" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#ffffff20', borderRadius: '8px', color: '#fff' }}
                    itemStyle={{ color: '#06b6d4' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="risk" 
                    stroke="#06b6d4" 
                    strokeWidth={3}
                    dot={{ r: 4, fill: '#0f172a', stroke: '#06b6d4', strokeWidth: 2 }}
                    activeDot={{ r: 6, fill: '#06b6d4', stroke: '#0f172a', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Alerts Feed */}
          <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6 flex flex-col">
            <h3 className="text-lg font-semibold text-white mb-6">High Risk Alerts</h3>
            <div className="flex-1 overflow-y-auto pr-2 space-y-4">
              {alerts.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 pb-10">
                  <Shield className="w-12 h-12 mb-3 opacity-20" />
                  <p>No immediate threats detected.</p>
                </div>
              ) : (
                alerts.map((alert, i) => (
                  <div key={alert.packet_id + i} className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 relative overflow-hidden">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-rose-500"></div>
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs text-rose-400 font-mono">{alert.timestamp}</span>
                      <span className="text-xs font-bold bg-rose-500/20 text-rose-400 px-2 py-0.5 rounded text-[10px]">RISK: {alert.risk_score}</span>
                    </div>
                    <h4 className="font-semibold text-white text-sm mt-1">{alert.attack_type}</h4>
                    <p className="text-xs text-slate-400 mt-1">Source: {alert.ip}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

      </main>

    </div>
  );
}

export default App;
