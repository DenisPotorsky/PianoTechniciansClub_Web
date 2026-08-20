import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-5xl mx-auto bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-8 md:p-12 border border-white/50">
          <div className="text-center">
            <div className="text-7xl mb-4">🎹</div>
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-700 bg-clip-text text-transparent mb-4">
              PianoTechniciansClub
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8">
              Закрытый клуб для фортепианных мастеров экстра-класса
            </p>

            {user ? (
              <div className="space-y-6">
                <p className="text-gray-700 text-lg">
                  Добро пожаловать, <span className="font-bold text-indigo-700">{user.first_name}</span>! 👋
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
                  <Link to="/calculator" className="group">
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-200 hover:shadow-xl hover:scale-105 transition-all duration-300">
                      <div className="text-4xl mb-3">🧮</div>
                      <div className="font-semibold text-gray-800 group-hover:text-indigo-700 transition">Калькулятор</div>
                      <div className="text-sm text-gray-500 mt-1">Расчёт басовых струн</div>
                    </div>
                  </Link>
                  <Link to="/age" className="group">
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-2xl border border-purple-200 hover:shadow-xl hover:scale-105 transition-all duration-300">
                      <div className="text-4xl mb-3">🔍</div>
                      <div className="font-semibold text-gray-800 group-hover:text-purple-700 transition">Атлас</div>
                      <div className="text-sm text-gray-500 mt-1">Поиск по серийному номеру</div>
                    </div>
                  </Link>
                  {(user.is_admin || user.is_super_admin) && (
                    <Link to="/admin" className="group">
                      <div className="bg-gradient-to-br from-yellow-50 to-orange-50 p-6 rounded-2xl border border-yellow-200 hover:shadow-xl hover:scale-105 transition-all duration-300">
                        <div className="text-4xl mb-3">👑</div>
                        <div className="font-semibold text-gray-800 group-hover:text-amber-700 transition">Админ-панель</div>
                        <div className="text-sm text-gray-500 mt-1">Управление клубом</div>
                      </div>
                    </Link>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <p className="text-gray-600 text-lg max-w-2xl mx-auto">
                  Это закрытое сообщество для профессионалов.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link
                    to="/login"
                    className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
                  >
                    🔑 Войти
                  </Link>
                  <Link
                    to="/request-access"
                    className="px-8 py-3 bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
                  >
                    📩 Запросить доступ
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto">
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 text-center border border-white/50 shadow-sm hover:shadow-md transition">
            <div className="text-3xl">🔒</div>
            <div className="font-semibold text-gray-700 mt-1">Закрытый клуб</div>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 text-center border border-white/50 shadow-sm hover:shadow-md transition">
            <div className="text-3xl">🎯</div>
            <div className="font-semibold text-gray-700 mt-1">Только для мастеров</div>
          </div>
          <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 text-center border border-white/50 shadow-sm hover:shadow-md transition">
            <div className="text-3xl">🌟</div>
            <div className="font-semibold text-gray-700 mt-1">Экстра-класс</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;