import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Settings() {
    const navigate = useNavigate();
    const [webhookUrl, setWebhookUrl] = useState('');

    const handleSave = () => {
        alert("Settings saved!");
    };

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
            <header className="flex justify-between items-center mb-12 max-w-3xl mx-auto">
                <h1 className="text-3xl font-light tracking-tight">System Settings</h1>
                <button onClick={() => navigate('/dashboard')} className="px-4 py-2 border border-slate-700 rounded-lg text-sm hover:bg-slate-800 transition">
                    Back to Dashboard
                </button>
            </header>

            <main className="max-w-3xl mx-auto space-y-8">
                <section className="bg-slate-800/30 p-8 rounded-2xl border border-slate-700/50">
                    <h2 className="text-xl font-medium mb-6">UniFi Webhook Configuration</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Endpoint URL</label>
                            <input
                                type="url"
                                className="w-full bg-slate-900/50 border border-slate-700 p-3 rounded-xl focus:outline-none focus:border-blue-500 transition-all"
                                placeholder="https://..."
                                value={webhookUrl}
                                onChange={(e) => setWebhookUrl(e.target.value)}
                            />
                        </div>
                        <button onClick={handleSave} className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-xl transition-all font-semibold">
                            Save Webhook
                        </button>
                    </div>
                </section>
            </main>
        </div>
    );
}
