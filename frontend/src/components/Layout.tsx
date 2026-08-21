import React, { useState, useRef, useEffect } from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
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
    <div
      className="min-h-screen bg-cover bg-center bg-fixed"
      style={{ backgroundImage: "url('/images/background.jpg')" }}
    >
      {/* НАВИГАЦИЯ */}
      <nav className="glass-nav sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Логотип */}
            <Link to="/" className="text-2xl font-bold text-white hover:opacity-80 transition">
              🎹 PianoTechniciansClub
            </Link>

            {/* ДЕСКТОПНОЕ МЕНЮ (ПОКАЗЫВАЕТСЯ НА БОЛЬШИХ ЭКРАНАХ) */}
            <div className="hidden md:flex items-center gap-6">
              <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
                🏠 Главная
              </Link>
              {user?.is_subscribed && (
                <>
                  <Link to="/calculator" className={`nav-link ${isActive('/calculator') ? 'active' : ''}`}>
                    🧮 Калькулятор
                  </Link>
                  <Link to="/age" className={`nav-link ${isActive('/age') ? 'active' : ''}`}>
                    🔍 Атлас
                  </Link>
                  <Link to="/regulating" className={`nav-link ${isActive('/regulating') ? 'active' : ''}`}>
                    🔧 Регулировка
                  </Link>
                </>
              )}
              {(user?.is_admin || user?.is_super_admin) && (
                <Link to="/admin" className={`nav-link ${isActive('/admin') ? 'active' : ''}`}>
                  👑 Админ
                </Link>
              )}
              {user ? (
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/10 transition"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                      {user.first_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <span className="text-white font-medium">{user.username}</span>
                    <svg className={`w-4 h-4 text-white/50 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-56 glass-card py-2 z-50">
                      <div className="px-4 py-2 border-b border-white/10">
                        <p className="text-sm font-semibold text-white">{user.first_name} {user.last_name || ''}</p>
                        <p className="text-xs text-white/50">@{user.username}</p>
                      </div>
                      <Link to="/profile" className="flex items-center gap-3 px-4 py-2 text-sm text-white/70 hover:bg-white/10 transition" onClick={() => setIsDropdownOpen(false)}>
                        <span>👤</span> Профиль
                      </Link>
                      <hr className="my-1 border-white/10" />
                      <button onClick={handleLogout} className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-400 hover:bg-white/10 transition text-left">
                        <span>🚪</span> Выйти
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <Link to="/login" className="glass-btn glass-btn-primary">
                  🔑 Вход
                </Link>
              )}
            </div>

            {/* ===== БУРГЕР-КНОПКА (ТОЛЬКО НА ТЕЛЕФОНАХ) ===== */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex flex-col gap-1.5 p-2 hover:bg-white/10 rounded-lg transition md:hidden"
              aria-label="Меню"
            >
              <span className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'rotate-45 translate-y-2' : ''}`}></span>
              <span className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
              <span className={`w-6 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-2' : ''}`}></span>
            </button>
          </div>

          {/* ===== МОБИЛЬНОЕ МЕНЮ ===== */}
          <div
            ref={menuRef}
            className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${
              isMenuOpen ? 'max-h-[600px] opacity-100 pb-4' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="glass rounded-xl p-4 space-y-1">
              <Link
                to="/"
                className={`block px-4 py-3 rounded-xl text-white transition ${
                  isActive('/') ? 'bg-white/15' : 'hover:bg-white/10'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                🏠 Главная
              </Link>

              {user?.is_subscribed && (
                <>
                  <Link
                    to="/calculator"
                    className={`block px-4 py-3 rounded-xl text-white transition ${
                      isActive('/calculator') ? 'bg-white/15' : 'hover:bg-white/10'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    🧮 Калькулятор
                  </Link>
                  <Link
                    to="/age"
                    className={`block px-4 py-3 rounded-xl text-white transition ${
                      isActive('/age') ? 'bg-white/15' : 'hover:bg-white/10'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    🔍 Атлас
                  </Link>
                  <Link
                    to="/regulating"
                    className={`block px-4 py-3 rounded-xl text-white transition ${
                      isActive('/regulating') ? 'bg-white/15' : 'hover:bg-white/10'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    🔧 Регулировка
                  </Link>
                </>
              )}

              {(user?.is_admin || user?.is_super_admin) && (
                <Link
                  to="/admin"
                  className={`block px-4 py-3 rounded-xl text-white transition ${
                    isActive('/admin') ? 'bg-white/15' : 'hover:bg-white/10'
                  }`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  👑 Админ
                </Link>
              )}

              {user ? (
                <>
                  <Link
                    to="/profile"
                    className="block px-4 py-3 rounded-xl text-white hover:bg-white/10 transition"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    👤 Профиль
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-3 rounded-xl text-red-400 hover:bg-white/10 transition"
                  >
                    🚪 Выйти
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  className="block text-center px-4 py-3 rounded-xl glass-btn glass-btn-primary"
                  onClick={() => setIsMenuOpen(false)}
                >
                  🔑 Войти
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto p-4 md:p-8">
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;