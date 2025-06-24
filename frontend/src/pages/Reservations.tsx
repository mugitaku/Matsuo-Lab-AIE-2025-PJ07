import React, { useEffect, useState } from 'react';
import { reservationAPI } from '../services/api';
import { Reservation } from '../types';
import './Reservations.css';

const Reservations: React.FC = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReservations();
  }, []);

  const fetchReservations = async () => {
    try {
      const data = await reservationAPI.getReservations();
      setReservations(data);
    } catch (err) {
      setError('予約の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (id: number) => {
    if (!window.confirm('この予約をキャンセルしますか？')) return;

    try {
      await reservationAPI.cancelReservation(id);
      await fetchReservations();
    } catch (err) {
      alert('キャンセルに失敗しました');
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      pending: '保留中',
      confirmed: '確定',
      rejected: '拒否',
      cancelled: 'キャンセル済',
      pending_rejection: '拒否確認待ち',
    };
    return labels[status] || status;
  };

  const getStatusClass = (status: string) => {
    const classes: { [key: string]: string } = {
      pending: 'status-pending',
      confirmed: 'status-confirmed',
      rejected: 'status-rejected',
      cancelled: 'status-cancelled',
      pending_rejection: 'status-warning',
    };
    return classes[status] || '';
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div className="reservations">
      <h1>予約一覧</h1>
      
      {reservations.length === 0 ? (
        <div className="no-reservations">
          <p>予約がありません</p>
        </div>
      ) : (
        <div className="reservation-grid">
          {reservations.map((reservation) => (
            <div key={reservation.id} className="reservation-card">
              <div className="reservation-header">
                <h3>{reservation.server.name}</h3>
                <span className={`status ${getStatusClass(reservation.status)}`}>
                  {getStatusLabel(reservation.status)}
                </span>
              </div>
              
              <div className="reservation-details">
                <div className="detail-item">
                  <strong>利用目的:</strong>
                  <p>{reservation.purpose || reservation.natural_language_request}</p>
                </div>
                
                <div className="detail-item">
                  <strong>開始時間:</strong>
                  <p>{new Date(reservation.start_time).toLocaleString()}</p>
                </div>
                
                <div className="detail-item">
                  <strong>終了時間:</strong>
                  <p>{new Date(reservation.end_time).toLocaleString()}</p>
                </div>
                
                <div className="detail-item">
                  <strong>優先度スコア:</strong>
                  <p>{reservation.priority_score}</p>
                </div>
                
                {reservation.ai_judgment_reason && (
                  <div className="detail-item">
                    <strong>AI判定理由:</strong>
                    <p>{reservation.ai_judgment_reason}</p>
                  </div>
                )}
              </div>
              
              {(reservation.status === 'confirmed' || reservation.status === 'pending') && (
                <button
                  className="btn btn-danger"
                  onClick={() => handleCancel(reservation.id)}
                >
                  キャンセル
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Reservations;