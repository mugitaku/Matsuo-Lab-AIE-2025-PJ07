import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reservationAPI } from '../services/api';
import './NewReservation.css';

const NewReservation: React.FC = () => {
  const [request, setRequest] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await reservationAPI.createReservation({
        natural_language_request: request,
      });
      setSuccess(true);
      setTimeout(() => navigate('/reservations'), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || '予約の作成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="new-reservation">
      <h1>新規予約作成</h1>
      <p className="description">
        自然言語でGPUサーバーの利用予定を入力してください。
        AIが内容を解析し、適切な予約を作成します。
      </p>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && (
        <div className="alert alert-success">
          予約を作成しました。予約一覧ページに移動します...
        </div>
      )}

      <form onSubmit={handleSubmit} className="reservation-form">
        <div className="form-group">
          <label htmlFor="request">予約内容</label>
          <textarea
            id="request"
            className="form-control"
            rows={6}
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            placeholder="例: 明日の午後2時から4時間、深層学習モデルの学習でGPUを使いたいです。論文の締め切りが近いので優先度は高めです。"
            required
          />
        </div>

        <div className="example-section">
          <h3>入力例：</h3>
          <ul>
            <li>今週金曜日の10時から、画像認識モデルの学習で8時間GPUを使用したい</li>
            <li>明日の夕方から2時間、実験用にGPUサーバーを予約したいです</li>
            <li>来週月曜日の朝9時から夕方6時まで、卒業研究のためにGPUを使いたい</li>
          </ul>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? '作成中...' : '予約を作成'}
        </button>
      </form>
    </div>
  );
};

export default NewReservation;