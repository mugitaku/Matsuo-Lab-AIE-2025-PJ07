import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { reservationAPI } from '../services/api';
import { Reservation } from '../types';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [pendingRejections, setPendingRejections] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [allReservations, pending] = await Promise.all([
          reservationAPI.getReservations(),
          reservationAPI.getReservations(true),
        ]);
        setReservations(allReservations);
        setPendingRejections(pending);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const activeReservations = reservations.filter(
    (r) => r.status === 'confirmed' && new Date(r.end_time) > new Date()
  );

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>ダッシュボード</h1>
      <p className="welcome">ようこそ、{user?.username}さん</p>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>アクティブな予約</h2>
          <div className="stat-number">{activeReservations.length}</div>
          <Link to="/reservations" className="dashboard-link">
            すべて見る →
          </Link>
        </div>

        <div className="dashboard-card">
          <h2>拒否確認待ち</h2>
          <div className="stat-number">{pendingRejections.length}</div>
          {pendingRejections.length > 0 && (
            <div className="alert alert-warning">
              確認が必要な予約があります
            </div>
          )}
          <Link to="/pending-rejections" className="dashboard-link">
            確認する →
          </Link>
        </div>

        <div className="dashboard-card">
          <h2>新規予約</h2>
          <p>自然言語でGPUサーバーの予約を作成</p>
          <Link to="/new-reservation" className="btn btn-primary">
            予約を作成
          </Link>
        </div>
      </div>

      {activeReservations.length > 0 && (
        <div className="recent-reservations">
          <h2>直近の予約</h2>
          <div className="reservation-list">
            {activeReservations.slice(0, 3).map((reservation) => (
              <div key={reservation.id} className="reservation-item">
                <div className="reservation-header">
                  <strong>{reservation.server.name}</strong>
                  <span className="reservation-status confirmed">確定</span>
                </div>
                <p>{reservation.purpose}</p>
                <div className="reservation-time">
                  {new Date(reservation.start_time).toLocaleString()} - 
                  {new Date(reservation.end_time).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;