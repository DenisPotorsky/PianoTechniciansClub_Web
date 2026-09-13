import React, {useState} from 'react';
import {useNavigate, Link} from 'react-router-dom';
import {useAuth} from '../contexts/AuthContext';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const {login} = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(email, password);
            navigate('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка входа');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            className="max-w-2xl mx-auto py-8">
            <div
                className="glass-card p-8 max-w-md mx-auto">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-white"> Вход в клуб</h2>
                    <p className="mt-2 text-blue-200 text-sm">
                        Введите email и пароль
                    </p>
                    <p className="text-blue-300 text-xs mt-1">
                        Если у вас нет доступа — запросите его ниже
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-blue-200">Email</label>
                            <input
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="glass-input w-full mt-1"
                                placeholder="Введите ваш email"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-blue-200">Пароль</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="glass-input w-full mt-1"
                                placeholder="Введите пароль"
                            />
                        </div>
                    </div>

                    {error && (
                        <div
                            className="text-red-400 text-sm text-center bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
                            ❌ {error}
                        </div>
                    )}
                    <div className="text-right">
                        <Link to="/forgot-password" className="text-sm text-white/40 hover:text-white transition">
                            Забыли пароль?
                        </Link>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full glass-btn glass-btn-primary py-3 text-lg disabled:opacity-50"
                    >
                        {loading ? 'Вход...' : '🔑 Войти'}
                    </button>

                    <div className="text-center space-y-2">
                        <Link to="/request-access"
                              className="text-blue-300 hover:text-blue-200 text-sm transition block">
                            Нет доступа? 📩 Запросить доступ
                        </Link>
                        <Link to="/whitelist-login"
                              className="text-yellow-300 hover:text-yellow-200 text-sm transition block">
                            👑 Вход по Telegram ID (для админов)
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Login;