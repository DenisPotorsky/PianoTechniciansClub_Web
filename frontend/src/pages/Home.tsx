import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home: React.FC = () => {
  const { user } = useAuth();

  // Карточки для авторизованных пользователей
  const AuthCards = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6 max-w-4xl mx-auto">
      <Link to="/calculator" className="glass-card p-4 md:p-6 hover:bg-white/20 transition">
        <div className="text-3xl md:text-4xl mb-2 md:mb-3">🧮</div>
        <div className="font-semibold text-white text-sm md:text-base">Калькулятор</div>
        <div className="text-xs md:text-sm text-white/50 mt-1">Расчёт басовых струн</div>
      </Link>
      <Link to="/age" className="glass-card p-4 md:p-6 hover:bg-white/20 transition">
        <div className="text-3xl md:text-4xl mb-2 md:mb-3">🔍</div>
        <div className="font-semibold text-white text-sm md:text-base">Атлас</div>
        <div className="text-xs md:text-sm text-white/50 mt-1">Поиск по серийному номеру</div>
      </Link>
      <Link to="/regulating" className="glass-card p-4 md:p-6 hover:bg-white/20 transition">
        <div className="text-3xl md:text-4xl mb-2 md:mb-3">🔧</div>
        <div className="font-semibold text-white text-sm md:text-base">Регулировка</div>
        <div className="text-xs md:text-sm text-white/50 mt-1">Параметры роялей</div>
      </Link>
      <Link to="/strings" className="glass-card p-4 md:p-6 hover:bg-white/20 transition">
        <div className="text-3xl md:text-4xl mb-2 md:mb-3">🎵</div>
        <div className="font-semibold text-white text-sm md:text-base">Мензуры струн</div>
        <div className="text-xs md:text-sm text-white/50 mt-1">Данные по струнам</div>
      </Link>
    </div>
  );

  // Карточки для гостей (заблокированные)
  const GuestCards = () => (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-6 max-w-4xl mx-auto">
      {[
        {icon: '🧮', title: 'Калькулятор', desc: 'Расчёт басовых струн'},
        {icon: '🔍', title: 'Атлас', desc: 'Поиск по серийному номеру'},
        {icon: '🔧', title: 'Регулировка', desc: 'Параметры роялей'},
        {icon: '🎵', title: 'Мензуры струн', desc: 'Данные по струнам'},
      ].map((card, index) => (
        <div key={index} className="relative">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm rounded-2xl flex flex-col items-center justify-center z-10">
            <span className="text-3xl md:text-4xl mb-2">🔒</span>
            <p className="text-white/80 text-xs md:text-sm font-medium text-center px-2 md:px-4">
              Доступно только<br/>участникам клуба
            </p>
          </div>
          <div className="glass-card p-4 md:p-6 opacity-50">
            <div className="text-3xl md:text-4xl mb-2 md:mb-3">{card.icon}</div>
            <div className="font-semibold text-white/60 text-sm md:text-base">{card.title}</div>
            <div className="text-xs md:text-sm text-white/30 mt-1">{card.desc}</div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen py-6 md:py-12">
      <div className="container mx-auto px-3 md:px-4">
        <div className="glass-card max-w-5xl mx-auto p-4 md:p-8 lg:p-12 text-center">
          <div className="text-5xl md:text-7xl mb-4">🎹</div>
          <h1 className="text-2xl md:text-4xl lg:text-6xl font-bold text-white mb-3 md:mb-4">
            Piano Technicians Club
          </h1>
          <p className="text-base md:text-xl lg:text-2xl text-white/70 mb-6 md:mb-8">
            Закрытый клуб для фортепианных мастеров экстра-класса
          </p>

          {user ? (
            <div className="space-y-4 md:space-y-6">
              <p className="text-white/80 text-base md:text-lg">
                Добро пожаловать, <span className="font-bold text-white">{user.first_name}</span>! 👋
              </p>
              <AuthCards />
              {(user.is_admin || user.is_super_admin) && (
                <div className="mt-4">
                  <Link to="/admin" className="glass-btn glass-btn-primary">
                    👑 Админ-панель
                  </Link>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6 md:space-y-8">
              <p className="text-white/60 text-base md:text-lg max-w-2xl mx-auto">
                Присоединяйтесь к сообществу профессионалов и получите доступ ко всем инструментам
              </p>
              <GuestCards />
              <div className="flex flex-col sm:flex-row gap-3 md:gap-4 justify-center pt-4">
                <Link
                  to="/login"
                  className="glass-btn glass-btn-primary px-6 md:px-8 py-3 text-base md:text-lg"
                >
                  🔑 Войти
                </Link>
                <Link
                  to="/request-access"
                  className="glass-btn px-6 md:px-8 py-3 text-base md:text-lg"
                >
                  📩 Запросить доступ
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;