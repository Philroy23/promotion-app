from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from src.main import db
from src.models.user import User
from src.models.campaign import Campaign

campaign_bp = Blueprint('campaign', __name__, url_prefix='/api/campaigns')

@campaign_bp.route('/', methods=['GET'])
@jwt_required()
def get_campaigns():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Les promotrices ne voient que les campagnes actives
        if user.is_promotrice():
            campaigns = Campaign.query.filter_by(is_active=True).all()
        else:
            # Les superviseurs et administrateurs voient toutes les campagnes
            campaigns = Campaign.query.all()
        
        return jsonify({
            'campaigns': [campaign.to_dict() for campaign in campaigns]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    try:
        campaign = Campaign.query.get(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campagne non trouvée'}), 404
        
        return jsonify({'campaign': campaign.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/', methods=['POST'])
@jwt_required()
def create_campaign():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Seuls les superviseurs et administrateurs peuvent créer des campagnes
        if not (user.is_superviseur() or user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        data = request.get_json()
        
        # Validation des données
        if not data.get('name') or not data.get('start_date') or not data.get('end_date'):
            return jsonify({'error': 'Nom, date de début et date de fin requis'}), 400
        
        # Conversion des dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide (YYYY-MM-DD)'}), 400
        
        if start_date > end_date:
            return jsonify({'error': 'La date de début doit être antérieure à la date de fin'}), 400
        
        # Créer la nouvelle campagne
        campaign = Campaign(
            name=data['name'],
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            available_gadgets=data.get('available_gadgets'),
            target_audience=data.get('target_audience'),
            budget=data.get('budget'),
            created_by=current_user_id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        return jsonify({
            'message': 'Campagne créée avec succès',
            'campaign': campaign.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Seuls les superviseurs et administrateurs peuvent modifier des campagnes
        if not (user.is_superviseur() or user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campagne non trouvée'}), 404
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'start_date' in data:
            campaign.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            campaign.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'is_active' in data:
            campaign.is_active = data['is_active']
        if 'available_gadgets' in data:
            campaign.available_gadgets = data['available_gadgets']
        if 'target_audience' in data:
            campaign.target_audience = data['target_audience']
        if 'budget' in data:
            campaign.budget = data['budget']
        
        campaign.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Campagne mise à jour avec succès',
            'campaign': campaign.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Seuls les administrateurs peuvent supprimer des campagnes
        if not (user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campagne non trouvée'}), 404
        
        db.session.delete(campaign)
        db.session.commit()
        
        return jsonify({'message': 'Campagne supprimée avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>/stats', methods=['GET'])
@jwt_required()
def get_campaign_stats(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Seuls les superviseurs et administrateurs peuvent voir les statistiques détaillées
        if not (user.is_superviseur() or user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campagne non trouvée'}), 404
        
        stats = {
            'campaign_info': campaign.to_dict(),
            'total_sales': campaign.get_total_sales(),
            'total_people_approached': campaign.get_total_people_approached(),
            'total_people_purchased': campaign.get_total_people_purchased(),
            'conversion_rate': campaign.get_campaign_conversion_rate(),
            'promoters_performance': campaign.get_promoters_performance()
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
