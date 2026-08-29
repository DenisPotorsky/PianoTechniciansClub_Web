import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home: React.FC = () => {
  const { user } = useAuth();

  const scrollToAbout = () => {
    document.getElementById('about-section')?.scrollIntoView({ behavior: 'smooth' });
  };

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
    <div className="min-h-screen py-6 md:py-10">
      <div className="container mx-auto px-3 md:px-4">

        {/* ===== КОМПАКТНЫЙ ГЕРОЙ + ТИЗЕР ===== */}
        <div className="glass-card max-w-5xl mx-auto p-4 md:p-8 lg:p-10 text-center">
          {/*<div className="text-4xl md:text-6xl mb-3">🎹</div>*/}
          <h1 className="text-2xl md:text-4xl lg:text-5xl font-bold text-white mb-2 md:mb-3">
            Piano Technicians Club
          </h1>
          <p className="text-base md:text-xl text-white/70 mb-4 md:mb-5">
            Закрытый клуб для фортепианных мастеров экстра-класса
          </p>

          {/* Тизер — суть клуба видна сразу */}
          <p className="text-sm md:text-base text-white/60 max-w-2xl mx-auto mb-6 md:mb-8">
            Базы мензур струн, регулировочных параметров и серийных номеров.
            Профессиональные инструменты расчёта для мастеров, реставраторов и настройщиков.
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
              <GuestCards />
              <div className="flex flex-col sm:flex-row gap-3 md:gap-4 justify-center pt-2">
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

          {/* Кнопка + стрелка вниз */}
          <div className="mt-6 md:mt-8">
            <button
              onClick={scrollToAbout}
              className="text-white/50 hover:text-white transition text-sm md:text-base"
            >
              Подробнее о клубе
            </button>
            <div className="animate-bounce text-white/40 text-xl mt-1">↓</div>
          </div>
        </div>

        {/* ===== О КЛУБЕ ===== */}
        <div id="about-section" className="glass-card max-w-5xl mx-auto mt-6 md:mt-8 p-4 md:p-8 lg:p-12">
          <div className="text-center mb-6 md:mb-10">
            <div className="text-4xl md:text-5xl mb-3">📖</div>
            <h2 className="text-2xl md:text-3xl font-bold text-white">О клубе</h2>
          </div>

          <p className="text-white/70 text-base md:text-lg text-center max-w-3xl mx-auto mb-8 md:mb-10">
            <span className="text-white font-semibold">Piano Technicians Club</span> — закрытое
            сообщество фортепианных мастеров, реставраторов и настройщиков экстра-класса.
            Базы данных, профессиональные инструменты расчёта и обмен опытом
            между лучшими специалистами отрасли.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8 md:mb-10">
            <div className="glass p-4 md:p-6 rounded-2xl">
              <div className="text-3xl mb-2">🧮</div>
              <h3 className="font-semibold text-white mb-2">Калькулятор басовых струн</h3>
              <p className="text-white/60 text-sm md:text-base">
                Точный расчёт параметров для изготовления и замены струн при реставрации.
              </p>
            </div>
            <div className="glass p-4 md:p-6 rounded-2xl">
              <div className="text-3xl mb-2">🔍</div>
              <h3 className="font-semibold text-white mb-2">Атлас серийных номеров</h3>
              <p className="text-white/60 text-sm md:text-base">
                Определение года выпуска и производителя инструмента за секунды.
              </p>
            </div>
            <div className="glass p-4 md:p-6 rounded-2xl">
              <div className="text-3xl mb-2">🔧</div>
              <h3 className="font-semibold text-white mb-2">Регулировочные параметры</h3>
              <p className="text-white/60 text-sm md:text-base">
                Справочные данные по настройке механики роялей и пианино ведущих мировых брендов.
              </p>
            </div>
            <div className="glass p-4 md:p-6 rounded-2xl">
              <div className="text-3xl mb-2">🎵</div>
              <h3 className="font-semibold text-white mb-2">Мензуры струн</h3>
              <p className="text-white/60 text-sm md:text-base">
                Обширная база длин и диаметров струн для различных моделей фортепиано.
              </p>
            </div>
          </div>

          <div className="glass p-4 md:p-6 rounded-2xl mb-6 md:mb-8">
            <h3 className="font-semibold text-white mb-2 text-center">🔒 Почему клуб закрытый?</h3>
            <p className="text-white/60 text-sm md:text-base text-center">
              Знания и данные, собранные здесь, — результат многолетней практики ведущих мастеров.
              Мы сохраняем ценность информации и объединяем тех, кто относится к ремеслу
              с уважением и страстью.
            </p>
          </div>

          {!user && (
            <div className="text-center">
              <h3 className="font-semibold text-white mb-2">📩 Как вступить?</h3>
              <p className="text-white/60 text-sm md:text-base mb-4 max-w-2xl mx-auto">
                Членство — только по заявке. Мы рады действующим фортепианным мастерам,
                реставраторам и настройщикам с опытом практической работы.
              </p>
              <Link
                to="/request-access"
                className="glass-btn glass-btn-primary px-6 md:px-8 py-3 inline-block"
              >
                📩 Отправить заявку
              </Link>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Home;