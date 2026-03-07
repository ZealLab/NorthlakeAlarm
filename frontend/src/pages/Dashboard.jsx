import React, { useEffect, useState } from 'react';

export default function Dashboard() {
    const [systemState, setSystemState] = useState("DISARMED");
    const [zones, setZones] = useState({
        1: "SECURE", 2: "SECURE", 3: "SECURE",
        4: "SECURE", 5: "SECURE", 6: "SECURE"
    });
    const [connected, setConnected] = useState(false);

    const [metrics, setMetrics] = useState({ temperature: '--', uptime: '--' });

    useEffect(() => {
        // Determine WS protocol based on current origin
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // For local dev where backend is 8081
        const host = window.location.port === '5173' ? 'localhost:8081' : window.location.host;

        const fetchMetrics = async () => {
            try {
                const res = await fetch(`${window.location.protocol}//${host}/api/metrics`);
                const data = await res.json();
                setMetrics(data);
            } catch (e) {
                console.error('Failed to fetch metrics', e);
            }
        };
        fetchMetrics();
        const metricsInterval = setInterval(fetchMetrics, 60000);

        const ws = new WebSocket(`${protocol}//${host}/ws`);

        ws.onopen = () => {
            setConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'state_update') {
                    setSystemState(data.system_state);
                    setZones(data.zones);
                }
            } catch (e) {
                console.error("Failed to parse WS message", e);
            }
        };

        ws.onclose = () => {
            setConnected(false);
            // Reconnect logic could go here
        };

        return () => {
            ws.close();
            clearInterval(metricsInterval);
        };
    }, []);

    const getSystemStateColor = () => {
        switch (systemState) {
            case 'DISARMED': return 'text-green-400 border-green-400 bg-green-400/10';
            case 'ARMED_PARTIAL': return 'text-yellow-400 border-yellow-400 bg-yellow-400/10';
            case 'ARMED_FULL': return 'text-red-500 border-red-500 bg-red-500/10';
            default: return 'text-gray-400 border-gray-400 bg-gray-400/10';
        }
    };

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
            <header className="flex justify-between items-center mb-12">
                <div>
                    <h1 className="text-3xl font-light tracking-tight">Northlake Dashboard</h1>
                    <div className="flex items-center mt-2 space-x-4">
                        <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                            <span className="text-sm text-slate-400">{connected ? 'Live Connection' : 'Disconnected'}</span>
                        </div>
                        <div className="text-sm text-slate-500 font-mono">
                            Pi CPU: {metrics.temperature} | Uptime: {metrics.uptime}
                        </div>
                    </div>
                </div>
                <div className={`px-6 py-2 border rounded-full text-sm font-semibold tracking-wider uppercase backdrop-blur-sm ${getSystemStateColor()}`}>
                    {systemState.replace('_', ' ')}
                </div>
            </header>

            <main className="max-w-7xl mx-auto space-y-12">
                <section>
                    <h2 className="text-xl font-medium text-slate-300 mb-6">Zone Status</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[1, 2, 3, 4, 5, 6].map(zoneId => (
                            <div
                                key={zoneId}
                                className={`p-6 rounded-2xl border transition-all duration-300 ${zones[zoneId] === 'TRIPPED'
                                    ? 'bg-red-500/10 border-red-500/50 shadow-[0_0_15px_rgba(239,68,68,0.2)]'
                                    : 'bg-slate-800/50 border-slate-700/50 hover:border-slate-600'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-lg font-medium text-slate-200">Zone {zoneId}</h3>
                                        <p className="text-sm text-slate-400 mt-1">
                                            {zoneId === 6 ? 'Front Entry (Delay)' : `Sensor ${zoneId}`}
                                        </p>
                                    </div>
                                    <div className={`px-3 py-1 rounded-full text-xs font-bold tracking-wide flex items-center space-x-2 ${zones[zoneId] === 'TRIPPED' ? 'bg-red-500 text-white' : 'bg-green-500/10 text-green-400'
                                        }`}>
                                        {zones[zoneId] === 'TRIPPED' && (
                                            <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
                                        )}
                                        <span>{zones[zoneId]}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="bg-slate-800/30 rounded-3xl p-8 border border-slate-700/50">
                    <h2 className="text-xl font-medium text-slate-300 mb-6">System Controls</h2>
                    <div className="flex flex-wrap gap-4">
                        <button
                            onClick={() => { const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.port === '5173' ? 'localhost:8081' : window.location.host}/ws`); ws.onopen = () => { ws.send(JSON.stringify({ command: 'ARM_FULL' })); ws.close(); } }}
                            className="px-8 py-3 bg-red-500 hover:bg-red-600 text-white rounded-xl font-semibold transition-colors shadow-lg shadow-red-500/20"
                        >
                            Arm Full
                        </button>
                        <button
                            onClick={() => { const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.port === '5173' ? 'localhost:8081' : window.location.host}/ws`); ws.onopen = () => { ws.send(JSON.stringify({ command: 'ARM_PARTIAL' })); ws.close(); } }}
                            className="px-8 py-3 bg-yellow-500 hover:bg-yellow-600 text-slate-900 rounded-xl font-semibold transition-colors shadow-lg shadow-yellow-500/20"
                        >
                            Arm Partial (Zones 1-4)
                        </button>
                        <button
                            onClick={() => { const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.port === '5173' ? 'localhost:8081' : window.location.host}/ws`); ws.onopen = () => { ws.send(JSON.stringify({ command: 'DISARM' })); ws.close(); } }}
                            className="px-8 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-semibold transition-colors"
                        >
                            Disarm
                        </button>
                    </div>
                </section>

                <section className="bg-slate-800/30 rounded-3xl p-8 border border-slate-700/50">
                    <h2 className="text-xl font-medium text-slate-300 mb-6">Recent Events</h2>
                    <div className="space-y-4 max-h-64 overflow-y-auto pr-4">
                        <div className="flex justify-between items-center text-sm p-4 bg-slate-800/50 rounded-xl border border-slate-700/30">
                            <span className="text-slate-400">Today, 10:42 AM</span>
                            <span className="text-green-400 font-medium">System Disarmed by PIN</span>
                        </div>
                        <div className="flex justify-between items-center text-sm p-4 bg-slate-800/50 rounded-xl border border-slate-700/30">
                            <span className="text-slate-400">Today, 06:00 AM</span>
                            <span className="text-red-400 font-medium">System Armed (Full)</span>
                        </div>
                        <div className="flex justify-between items-center text-sm p-4 bg-slate-800/50 rounded-xl border border-slate-700/30">
                            <span className="text-slate-400">Yesterday, 11:30 PM</span>
                            <span className="text-yellow-400 font-medium">Zone 6 Tripped (Entry Delay started)</span>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
