import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { campaignAPI, promotionDataAPI, userAPI } from '../lib/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [promotionData, setPromotionData] = useState([]);
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');

        // Charger les campagnes
        const campaignsResponse = await campaignAPI.getCampaigns();
        setCampaigns(campaignsResponse.campaigns || []);

        // Charger les données promotionnelles
        const dataResponse = await promotionDataAPI.getPromotionData();
        setPromotionData(dataResponse.promotion_data || []);

        // Charger les statistiques utilisateurs (pour superviseurs et administrateurs)
        if (user?.role !== 'promotrice') {
          try {
            const statsResponse = await userAPI.getUserStats();
            setUserStats(statsResponse.stats);
          } catch (err) {
            console.log('Pas de statistiques disponibles');
          }
        }

      } catch (err) {
        console.error('Erreur lors du chargement des données:', err);
        setError('Erreur lors du chargement des données');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <p>Chargement du tableau de bord...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error">
        {error}
      </div>
    );
  }

  // Calculs pour les statistiques
  const activeCampaigns = campaigns.filter(c => c.is_active);
  const myData = user?.role === 'promotrice' 
    ? promotionData.filter(d => d.promoter_id === user.id)
    : promotionData;

  const totalSales = myData.reduce((sum, d) => sum + (d.products_sold || 0), 0);
  const totalApproached = myData.reduce((sum, d) => sum + (d.people_approached || 0), 0);
  const totalPurchased = myData.reduce((sum, d) => sum + (d.people_purchased || 0), 0);
  const conversionRate = totalApproached > 0 ? ((totalPurchased / totalApproached) * 100).toFixed(1) : 0;

  return (
    <div>
      <h1 style={{ marginBottom: '30px', color: '#333' }}>
        Tableau de bord - {user?.role}
      </h1>

      {/* Statistiques principales */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{activeCampaigns.length}</div>
          <div className="stat-label">Campagnes actives</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{totalSales}</div>
          <div className="stat-label">Produits vendus</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{totalApproached}</div>
          <div className="stat-label">Personnes approchées</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{conversionRate}%</div>
          <div className="stat-label">Taux de conversion</div>
        </div>

        {userStats && (
          <div className="stat-card">
            <div className="stat-value">{userStats.total_promotrices}</div>
            <div className="stat-label">Promotrices actives</div>
          </div>
        )}
      </div>

      {/* Campagnes actives */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Campagnes actives</h3>
        </div>
        
        {activeCampaigns.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            Aucune campagne active pour le moment.
          </p>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {activeCampaigns.map(campaign => (
              <div key={campaign.id} style={{
                padding: '15px',
                border: '1px solid #eee',
                borderRadius: '6px',
                backgroundColor: '#f9f9f9'
              }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>
                  {campaign.name}
                </h4>
                <p style={{ margin: '0 0 10px 0', color: '#666' }}>
                  {campaign.description}
                </p>
                <div style={{ display: 'flex', gap: '20px', fontSize: '14px', color: '#666' }}>
                  <span>📅 Du {campaign.start_date} au {campaign.end_date}</span>
                  {campaign.available_gadgets && (
                    <span>🎁 Gadgets: {campaign.available_gadgets}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Données récentes */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            {user?.role === 'promotrice' ? 'Mes dernières saisies' : 'Dernières données saisies'}
          </h3>
        </div>
        
        {myData.length === 0 ? (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            Aucune donnée saisie pour le moment.
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Magasin</th>
                  {user?.role !== 'promotrice' && <th>Promotrice</th>}
                  <th>Produits vendus</th>
                  <th>Personnes approchées</th>
                  <th>Taux de conversion</th>
                </tr>
              </thead>
              <tbody>
                {myData.slice(0, 5).map(data => (
                  <tr key={data.id}>
                    <td>{data.mission_date}</td>
                    <td>{data.store_name}</td>
                    {user?.role !== 'promotrice' && <td>{data.promoter_name}</td>}
                    <td>{data.products_sold}</td>
                    <td>{data.people_approached}</td>
                    <td>{data.conversion_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Message d'accueil pour les promotrices */}
      {user?.role === 'promotrice' && (
        <div className="alert alert-info">
          <strong>Bienvenue !</strong> Utilisez le menu "Point journalier" pour saisir vos données quotidiennes.
        </div>
      )}
    </div>
  );
};

export default Dashboard;
