import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Layout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
  };

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* En-tête */}
      <header style={{
        backgroundColor: 'white',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '0 20px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          height: '60px'
        }}>
          <h1 style={{ margin: 0, color: '#333', fontSize: '20px' }}>
            Gestion Promotions
          </h1>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <span style={{ color: '#666' }}>
              Bonjour, {user?.username} ({user?.role})
            </span>
            <button 
              onClick={handleLogout}
              className="btn btn-secondary"
              style={{ fontSize: '14px', padding: '8px 16px' }}
            >
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #eee',
        padding: '0 20px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          gap: '0'
        }}>
          <Link to="/dashboard" className={isActive('/dashboard')}>
            📊 Tableau de bord
          </Link>
          
          {user?.role === 'promotrice' && (
            <Link to="/daily-report" className={isActive('/daily-report')}>
              📝 Point journalier
            </Link>
          )}
          
          {(user?.role === 'superviseur' || user?.role === 'administrateur' || user?.role === 'super_administrateur') && (
            <>
              <Link to="/campaigns" className={isActive('/campaigns')}>
                🎯 Campagnes
              </Link>
              <Link to="/data" className={isActive('/data')}>
                📈 Données
              </Link>
              <Link to="/users" className={isActive('/users')}>
                👥 Utilisateurs
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* Contenu principal */}
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '30px 20px'
      }}>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
