import React, { useEffect, useState } from 'react';
import { reservationAPI } from '../services/api';
import { Reservation } from '../types';
import './PendingRejections.css';

const PendingRejections: React.FC = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPendingRejections();
  }, []);

  const fetchPendingRejections = async () => {
    try {
      const data = await reservationAPI.getReservations(true);
      setReservations(data);
    } catch (err) {
      setError('データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmRejection = async (id: number, confirm: boolean) => {
    try {
      await reservationAPI.confirmRejection(id, {
        confirm,
        reason: confirm ? 'ユーザーが承認しました' : 'ユーザーが拒否しました',
      });
      await fetchPendingRejections();
    } catch (err) {
      alert('処理に失敗しました');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div className="pending-rejections">
      <h1>拒否確認待ち</h1>
      <p className="description">
        他の予約との競合により、あなたの予約がキャンセル候補となっています。
        確認して対応してください。
      </p>

      {reservations.length === 0 ? (
        <div className="no-pending">
          <p>確認が必要な予約はありません</p>
        </div>
      ) : (
        <div className="rejection-list">
          {reservations.map((reservation) => (
            <div key={reservation.id} className="rejection-card">
              <div className="rejection-header">
                <h3>{reservation.server.name}</h3>
                <span className="priority-score">
                  優先度スコア: {reservation.priority_score}
                </span>
              </div>

              <div className="rejection-details">
                <div className="detail-row">
                  <strong>利用目的:</strong>
                  <p>{reservation.purpose || reservation.natural_language_request}</p>
                </div>

                <div className="detail-row">
                  <strong>予約時間:</strong>
                  <p>
                    {new Date(reservation.start_time).toLocaleString()} 〜{' '}
                    {new Date(reservation.end_time).toLocaleString()}
                  </p>
                </div>

                {reservation.ai_judgment_reason && (
                  <div className="ai-judgment">
                    <strong>AI判定理由:</strong>
                    <p>{reservation.ai_judgment_reason}</p>
                  </div>
                )}
              </div>

              <div className="action-buttons">
                <button
                  className="btn btn-danger"
                  onClick={() => handleConfirmRejection(reservation.id, true)}
                >
                  キャンセルを承認
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleConfirmRejection(reservation.id, false)}
                >
                  キャンセルを拒否
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PendingRejections;