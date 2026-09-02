import React, {useState, useRef, useEffect} from 'react';
import {Link, Outlet, useNavigate, useLocation} from 'react-router-dom';
import {useAuth} from '../contexts/AuthContext';

const TELEGRAM_BOT_URL = "https://t.me/PianoTechniciansClub_bot";

const Layout: React.FC = () => {
    const {user, logout} = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const handleLogout = () => {
        logout();
        navigate('/');
        setIsMenuOpen(false);
        setIsDropdownOpen(false);
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className="min-h-screen bg-cover bg-center bg-fixed"
             style={{backgroundImage: "url('/images/background.jpg')"}}>

            {/* НАВИГАЦИЯ */}
            <nav className="glass-nav sticky top-0 z-50">
                <div className="container mx-auto px-4">
                    <div className="flex justify-between items-center h-16">
                        {/* Логотип */}
                        <Link to="/"
                              className="text-2xl font-bold text-white hover:opacity-80 transition whitespace-nowrap">
                            PianoTechniciansClub
                        </Link>

                        {/* Профиль + Telegram + Бургер (справа) */}
                        <div className="flex items-center gap-4">
                            {/* Кнопка Telegram-бота */}
                            <a
                                href={TELEGRAM_BOT_URL}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hidden md:flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/10 transition text-white/80 hover:text-white"
                                title="Открыть Telegram-бот"
                            >
                                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.479.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                                </svg>
                                <span className="text-sm font-medium">Тelegram-бот</span>
                            </a>

                            {/* Профиль (только на больших экранах) */}
                            {user && (
                                <div className="hidden md:block relative" ref={dropdownRef}>
                                    <button
                                        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                        className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/10 transition"
                                    >
                                        <div
                                            className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                                            {user.first_name?.charAt(0).toUpperCase() || 'U'}
                                        </div>
                                        <span className="text-white font-medium hidden sm:block">{user.username}</span>
                                        <svg
                                            className={`w-4 h-4 text-white/50 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`}
                                            fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                                  d="M19 9l-7 7-7-7"/>
                                        </svg>
                                    </button>
                                    {isDropdownOpen && (
                                        <div className="absolute right-0 mt-2 w-56 glass-card py-2 z-50">
                                            <div className="px-4 py-2 border-b border-white/10">
                                                <p className="text-sm font-semibold text-white">{user.first_name} {user.last_name || ''}</p>
                                                <p className="text-xs text-white/50">@{user.username}</p>
                                                {user.is_super_admin && <span
                                                    className="text-xs text-amber-400 font-semibold">👑 Супер-админ</span>}
                                                {user.is_admin && !user.is_super_admin && <span
                                                    className="text-xs text-indigo-400 font-semibold">⭐ Админ</span>}
                                            </div>
                                            <Link to="/profile"
                                                  className="flex items-center gap-3 px-4 py-2 text-sm text-white/70 hover:bg-white/10 transition"
                                                  onClick={() => setIsDropdownOpen(false)}>
                                                <span>👤</span> Профиль
                                            </Link>
                                            <hr className="my-1 border-white/10"/>
                                            <button onClick={handleLogout}
                                                    className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-400 hover:bg-white/10 transition text-left">
                                                <span>🚪</span> Выйти
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}

                            {!user && (
                                <Link to="/login" className="hidden md:block glass-btn glass-btn-primary">
                                    🔑 Вход
                                </Link>
                            )}

                            {/* БУРГЕР (всегда виден) */}
                            <button
                                onClick={() => setIsMenuOpen(!isMenuOpen)}
                                className="flex flex-col gap-1.5 p-2 hover:bg-white/10 rounded-lg transition"
                                aria-label="Меню"
                            >
                                <span
                                    className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></span>
                                <span
                                    className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
                                <span
                                    className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* ЗАТЕМНЕНИЕ */}
            {isMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
                    onClick={() => setIsMenuOpen(false)}
                />
            )}

            {/* ВЫЕЗЖАЮЩЕЕ МЕНЮ СПРАВА */}
            <div
                ref={menuRef}
                className={`fixed top-0 right-0 h-full w-80 glass-card rounded-l-2xl z-50 transition-transform duration-300 ease-in-out ${
                    isMenuOpen ? 'translate-x-0' : 'translate-x-full'
                }`}
                style={{
                    background: 'rgba(15, 15, 30, 0.92)',
                    backdropFilter: 'blur(24px)',
                    WebkitBackdropFilter: 'blur(24px)',
                    borderLeft: '1px solid rgba(255,255,255,0.08)'
                }}
            >
                {/* КРЕСТИК */}
                <div className="h-16 flex items-center justify-end px-4 border-b border-white/5">
                    <button
                        onClick={() => setIsMenuOpen(false)}
                        className="p-2 hover:bg-white/10 rounded-lg transition text-white/60 hover:text-white"
                    >
                        ✕
                    </button>
                </div>

                <div className="flex flex-col p-6 space-y-1">
                    <Link
                        to="/"
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl text-white transition ${
                            isActive('/') ? 'bg-white/15' : 'hover:bg-white/10'
                        }`}
                        onClick={() => setIsMenuOpen(false)}
                    >
                        <span className="text-xl">🏠</span> Главная
                    </Link>

                    {/* Telegram-бот в меню */}
                    <a
                        href={TELEGRAM_BOT_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 px-4 py-3 rounded-xl text-white hover:bg-white/10 transition"
                    >
                        <span className="text-xl">🤖</span> Telegram-бот
                    </a>

                    {user?.is_subscribed && (
                        <>
                            <Link
                                to="/calculator"
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-white transition ${
                                    isActive('/calculator') ? 'bg-white/15' : 'hover:bg-white/10'
                                }`}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <span className="text-xl">🧮</span> Калькулятор
                            </Link>
                            <Link
                                to="/age"
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-white transition ${
                                    isActive('/age') ? 'bg-white/15' : 'hover:bg-white/10'
                                }`}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <span className="text-xl">🔍</span> Атлас
                            </Link>
                            <Link
                                to="/regulating"
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-white transition ${
                                    isActive('/regulating') ? 'bg-white/15' : 'hover:bg-white/10'
                                }`}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <span className="text-xl">🔧</span> Регулировка
                            </Link>
                            <Link
                                to="/strings"
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-white transition ${
                                    isActive('/strings') ? 'bg-white/15' : 'hover:bg-white/10'
                                }`}
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <span className="text-xl">🎵</span> Мензуры
                            </Link>
                        </>
                    )}

                    {(user?.is_admin || user?.is_super_admin) && (
                        <Link
                            to="/admin"
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-white transition ${
                                isActive('/admin') ? 'bg-white/15' : 'hover:bg-white/10'
                            }`}
                            onClick={() => setIsMenuOpen(false)}
                        >
                            <span className="text-xl">👑</span> Админ
                        </Link>
                    )}

                    {!user && (
                        <Link
                            to="/login"
                            className="flex items-center justify-center gap-3 px-4 py-3 rounded-xl glass-btn glass-btn-primary"
                            onClick={() => setIsMenuOpen(false)}
                        >
                            <span className="text-xl">🔑</span> Войти
                        </Link>
                    )}

                    {user && (
                        <>
                            <div className="border-t border-white/10 my-2"/>
                            <Link
                                to="/profile"
                                className="flex items-center gap-3 px-4 py-3 rounded-xl text-white hover:bg-white/10 transition"
                                onClick={() => setIsMenuOpen(false)}
                            >
                                <span className="text-xl">👤</span> Профиль
                            </Link>
                            <button
                                onClick={handleLogout}
                                className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-red-400 hover:bg-white/10 transition text-left"
                            >
                                <span className="text-xl">🚪</span> Выйти
                            </button>
                        </>
                    )}
                </div>
            </div>

            <div className="container mx-auto p-4 md:p-8">
                <Outlet/>
            </div>
        </div>
    );
};

export default Layout;
