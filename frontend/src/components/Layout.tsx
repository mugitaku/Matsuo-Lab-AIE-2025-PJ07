import React from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="container">
          <Link to="/" className="nav-brand">
            GPU予約システム
          </Link>
          <div className="nav-menu">
            <Link to="/dashboard" className="nav-link">
              ダッシュボード
            </Link>
            <Link to="/new-reservation" className="nav-link">
              新規予約
            </Link>
            <Link to="/reservations" className="nav-link">
              予約一覧
            </Link>
            <Link to="/pending-rejections" className="nav-link">
              拒否確認待ち
            </Link>
          </div>
          <div className="nav-user">
            <span className="username">{user?.username}</span>
            <button onClick={handleLogout} className="btn btn-secondary">
              ログアウト
            </button>
          </div>
        </div>
      </nav>
      <main className="main-content">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;