import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { campaignAPI, promotionDataAPI } from '../lib/api';

const DailyReport = () => {
  const { user } = useAuth();
  const [campaigns, setCampaigns] = useState([]);
  const [formData, setFormData] = useState({
    promoter_name: user?.username || '',
    promoter_contact: '',
    store_name: '',
    mission_date: new Date().toISOString().split('T')[0],
    arrival_time: '',
    departure_time: '',
    initial_stock: '',
    products_sold: '',
    remaining_stock: '',
    people_approached: '',
    people_purchased: '',
    customer_comments: '',
    gadgets_distributed: '',
    campaign_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const response = await campaignAPI.getCampaigns();
        setCampaigns(response.campaigns || []);
      } catch (err) {
        console.error('Erreur lors du chargement des campagnes:', err);
      }
    };

    fetchCampaigns();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Calcul automatique du stock restant
    if (name === 'initial_stock' || name === 'products_sold') {
      const initial = name === 'initial_stock' ? parseInt(value) || 0 : parseInt(formData.initial_stock) || 0;
      const sold = name === 'products_sold' ? parseInt(value) || 0 : parseInt(formData.products_sold) || 0;
      const remaining = initial - sold;
      
      if (name === 'initial_stock' || name === 'products_sold') {
        setFormData(prev => ({
          ...prev,
          [name]: value,
          remaining_stock: remaining >= 0 ? remaining.toString() : '0'
        }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    // Validation
    if (!formData.campaign_id) {
      setError('Veuillez sélectionner une campagne');
      setLoading(false);
      return;
    }

    if (!formData.store_name.trim()) {
      setError('Le nom du magasin est requis');
      setLoading(false);
      return;
    }

    try {
      const dataToSubmit = {
        ...formData,
        initial_stock: parseInt(formData.initial_stock) || 0,
        products_sold: parseInt(formData.products_sold) || 0,
        remaining_stock: parseInt(formData.remaining_stock) || 0,
        people_approached: parseInt(formData.people_approached) || 0,
        people_purchased: parseInt(formData.people_purchased) || 0
      };

      const response = await promotionDataAPI.createPromotionData(dataToSubmit);
      
      if (response.message) {
        setSuccess('Point journalier enregistré avec succès !');
        // Réinitialiser le formulaire
        setFormData({
          promoter_name: user?.username || '',
          promoter_contact: '',
          store_name: '',
          mission_date: new Date().toISOString().split('T')[0],
          arrival_time: '',
          departure_time: '',
          initial_stock: '',
          products_sold: '',
          remaining_stock: '',
          people_approached: '',
          people_purchased: '',
          customer_comments: '',
          gadgets_distributed: '',
          campaign_id: ''
        });
      }
    } catch (err) {
      console.error('Erreur lors de l\'enregistrement:', err);
      setError(err.response?.data?.error || 'Erreur lors de l\'enregistrement des données');
    } finally {
      setLoading(false);
    }
  };

  const activeCampaigns = campaigns.filter(c => c.is_active);

  return (
    <div>
      <h1 style={{ marginBottom: '30px', color: '#333' }}>
        Point journalier
      </h1>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          {success}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Saisie des données journalières</h3>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Informations de base */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div className="form-group">
              <label htmlFor="campaign_id" className="form-label">
                Campagne *
              </label>
              <select
                id="campaign_id"
                name="campaign_id"
                className="form-select"
                value={formData.campaign_id}
                onChange={handleChange}
                required
                disabled={loading}
              >
                <option value="">Sélectionner une campagne</option>
                {activeCampaigns.map(campaign => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="promoter_name" className="form-label">
                Nom et prénom *
              </label>
              <input
                type="text"
                id="promoter_name"
                name="promoter_name"
                className="form-input"
                value={formData.promoter_name}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="promoter_contact" className="form-label">
                Contact
              </label>
              <input
                type="text"
                id="promoter_contact"
                name="promoter_contact"
                className="form-input"
                value={formData.promoter_contact}
                onChange={handleChange}
                disabled={loading}
                placeholder="Téléphone ou email"
              />
            </div>
          </div>

          {/* Informations du magasin et mission */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div className="form-group">
              <label htmlFor="store_name" className="form-label">
                Magasin *
              </label>
              <input
                type="text"
                id="store_name"
                name="store_name"
                className="form-input"
                value={formData.store_name}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="mission_date" className="form-label">
                Date *
              </label>
              <input
                type="date"
                id="mission_date"
                name="mission_date"
                className="form-input"
                value={formData.mission_date}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="arrival_time" className="form-label">
                Heure d'arrivée
              </label>
              <input
                type="time"
                id="arrival_time"
                name="arrival_time"
                className="form-input"
                value={formData.arrival_time}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="departure_time" className="form-label">
                Heure de départ
              </label>
              <input
                type="time"
                id="departure_time"
                name="departure_time"
                className="form-input"
                value={formData.departure_time}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
          </div>

          {/* Gestion des stocks */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div className="form-group">
              <label htmlFor="initial_stock" className="form-label">
                Stock de départ
              </label>
              <input
                type="number"
                id="initial_stock"
                name="initial_stock"
                className="form-input"
                value={formData.initial_stock}
                onChange={handleChange}
                min="0"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="products_sold" className="form-label">
                Stock vendu
              </label>
              <input
                type="number"
                id="products_sold"
                name="products_sold"
                className="form-input"
                value={formData.products_sold}
                onChange={handleChange}
                min="0"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="remaining_stock" className="form-label">
                Stock restant
              </label>
              <input
                type="number"
                id="remaining_stock"
                name="remaining_stock"
                className="form-input"
                value={formData.remaining_stock}
                onChange={handleChange}
                min="0"
                disabled={loading}
                readOnly
                style={{ backgroundColor: '#f8f9fa' }}
              />
            </div>
          </div>

          {/* Performance commerciale */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div className="form-group">
              <label htmlFor="people_approached" className="form-label">
                Personnes approchées
              </label>
              <input
                type="number"
                id="people_approached"
                name="people_approached"
                className="form-input"
                value={formData.people_approached}
                onChange={handleChange}
                min="0"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="people_purchased" className="form-label">
                Personnes ayant acheté
              </label>
              <input
                type="number"
                id="people_purchased"
                name="people_purchased"
                className="form-input"
                value={formData.people_purchased}
                onChange={handleChange}
                min="0"
                disabled={loading}
              />
            </div>
          </div>

          {/* Informations complémentaires */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div className="form-group">
              <label htmlFor="gadgets_distributed" className="form-label">
                Gadgets à distribuer
              </label>
              <input
                type="text"
                id="gadgets_distributed"
                name="gadgets_distributed"
                className="form-input"
                value={formData.gadgets_distributed}
                onChange={handleChange}
                disabled={loading}
                placeholder="Ex: Stylos, T-shirts, Casquettes"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="customer_comments" className="form-label">
              Commentaires / Informations du client
            </label>
            <textarea
              id="customer_comments"
              name="customer_comments"
              className="form-textarea"
              value={formData.customer_comments}
              onChange={handleChange}
              disabled={loading}
              rows="4"
              placeholder="Observations, retours clients, difficultés rencontrées..."
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '15px', fontSize: '16px' }}
            disabled={loading}
          >
            {loading ? 'Enregistrement...' : 'Enregistrer le point journalier'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default DailyReport;
