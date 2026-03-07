import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
    const [pin, setPin] = useState('');
    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault();
        if (pin === '1234') {
            navigate('/dashboard');
        } else {
            alert("Invalid PIN. Try 1234.");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 p-4 font-sans">
            <div className="bg-slate-800/50 p-10 rounded-3xl border border-slate-700 shadow-2xl w-full max-w-sm backdrop-blur-sm">
                <h1 className="text-3xl font-light text-center mb-2 tracking-tight">Northlake</h1>
                <p className="text-center text-slate-400 mb-8 text-sm uppercase tracking-widest">Security System</p>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <input
                            type="password"
                            placeholder="Enter PIN"
                            className="w-full bg-slate-900/50 border border-slate-700 text-center text-2xl tracking-[0.5em] p-4 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-mono"
                            value={pin}
                            onChange={(e) => setPin(e.target.value)}
                            autoFocus
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-4 rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-[0.98]"
                    >
                        DISARM / LOGIN
                    </button>
                </form>
            </div>
        </div>
    );
}
