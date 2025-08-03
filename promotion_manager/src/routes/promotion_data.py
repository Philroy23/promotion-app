from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, time
from src.main import db
from src.models.user import User
from src.models.campaign import Campaign
from src.models.promotion_data import PromotionData

promotion_data_bp = Blueprint('promotion_data', __name__, url_prefix='/api/promotion-data')

@promotion_data_bp.route('/', methods=['GET'])
@jwt_required()
def get_promotion_data():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Les promotrices ne voient que leurs propres données
        if user.is_promotrice():
            data = PromotionData.query.filter_by(promoter_id=current_user_id).all()
        else:
            # Les superviseurs et administrateurs voient toutes les données
            data = PromotionData.query.all()
        
        return jsonify({
            'promotion_data': [item.to_dict() for item in data]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@promotion_data_bp.route('/<int:data_id>', methods=['GET'])
@jwt_required()
def get_promotion_data_item(data_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        data_item = PromotionData.query.get(data_id)
        
        if not data_item:
            return jsonify({'error': 'Données non trouvées'}), 404
        
        # Les promotrices ne peuvent voir que leurs propres données
        if user.is_promotrice() and data_item.promoter_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        return jsonify({'promotion_data': data_item.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@promotion_data_bp.route('/', methods=['POST'])
@jwt_required()
def create_promotion_data():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        data = request.get_json()
        
        # Validation des données obligatoires
        required_fields = ['promoter_name', 'store_name', 'mission_date', 'campaign_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Vérifier que la campagne existe
        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return jsonify({'error': 'Campagne non trouvée'}), 404
        
        # Conversion des données
        try:
            mission_date = datetime.strptime(data['mission_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Format de date invalide (YYYY-MM-DD)'}), 400
        
        arrival_time = None
        departure_time = None
        
        if data.get('arrival_time'):
            try:
                arrival_time = datetime.strptime(data['arrival_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Format d\'heure d\'arrivée invalide (HH:MM)'}), 400
        
        if data.get('departure_time'):
            try:
                departure_time = datetime.strptime(data['departure_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Format d\'heure de départ invalide (HH:MM)'}), 400
        
        # Créer les nouvelles données promotionnelles
        promotion_data = PromotionData(
            promoter_name=data['promoter_name'],
            promoter_contact=data.get('promoter_contact'),
            store_name=data['store_name'],
            mission_date=mission_date,
            arrival_time=arrival_time,
            departure_time=departure_time,
            initial_stock=int(data.get('initial_stock', 0)),
            products_sold=int(data.get('products_sold', 0)),
            remaining_stock=int(data.get('remaining_stock', 0)),
            people_approached=int(data.get('people_approached', 0)),
            people_purchased=int(data.get('people_purchased', 0)),
            customer_comments=data.get('customer_comments'),
            gadgets_distributed=data.get('gadgets_distributed'),
            promoter_id=current_user_id,
            campaign_id=data['campaign_id']
        )
        
        db.session.add(promotion_data)
        db.session.commit()
        
        return jsonify({
            'message': 'Données promotionnelles créées avec succès',
            'promotion_data': promotion_data.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promotion_data_bp.route('/<int:data_id>', methods=['PUT'])
@jwt_required()
def update_promotion_data(data_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        data_item = PromotionData.query.get(data_id)
        if not data_item:
            return jsonify({'error': 'Données non trouvées'}), 404
        
        # Les promotrices ne peuvent modifier que leurs propres données
        if user.is_promotrice() and data_item.promoter_id != current_user_id:
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        data = request.get_json()
        
        # Mise à jour des champs
        if 'promoter_name' in data:
            data_item.promoter_name = data['promoter_name']
        if 'promoter_contact' in data:
            data_item.promoter_contact = data['promoter_contact']
        if 'store_name' in data:
            data_item.store_name = data['store_name']
        if 'mission_date' in data:
            data_item.mission_date = datetime.strptime(data['mission_date'], '%Y-%m-%d').date()
        if 'arrival_time' in data and data['arrival_time']:
            data_item.arrival_time = datetime.strptime(data['arrival_time'], '%H:%M').time()
        if 'departure_time' in data and data['departure_time']:
            data_item.departure_time = datetime.strptime(data['departure_time'], '%H:%M').time()
        if 'initial_stock' in data:
            data_item.initial_stock = int(data['initial_stock'])
        if 'products_sold' in data:
            data_item.products_sold = int(data['products_sold'])
        if 'remaining_stock' in data:
            data_item.remaining_stock = int(data['remaining_stock'])
        if 'people_approached' in data:
            data_item.people_approached = int(data['people_approached'])
        if 'people_purchased' in data:
            data_item.people_purchased = int(data['people_purchased'])
        if 'customer_comments' in data:
            data_item.customer_comments = data['customer_comments']
        if 'gadgets_distributed' in data:
            data_item.gadgets_distributed = data['gadgets_distributed']
        
        data_item.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Données promotionnelles mises à jour avec succès',
            'promotion_data': data_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promotion_data_bp.route('/<int:data_id>', methods=['DELETE'])
@jwt_required()
def delete_promotion_data(data_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        data_item = PromotionData.query.get(data_id)
        if not data_item:
            return jsonify({'error': 'Données non trouvées'}), 404
        
        # Seuls les administrateurs ou le propriétaire peuvent supprimer
        if not (user.is_administrateur() or user.is_super_administrateur()) and data_item.promoter_id != current_user_id:
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        db.session.delete(data_item)
        db.session.commit()
        
        return jsonify({'message': 'Données promotionnelles supprimées avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promotion_data_bp.route('/campaign/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_promotion_data_by_campaign(campaign_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Vérifier que la campagne existe
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return jsonify({'error': 'Campagne non trouvée'}), 404
        
        # Les promotrices ne voient que leurs propres données
        if user.is_promotrice():
            data = PromotionData.query.filter_by(campaign_id=campaign_id, promoter_id=current_user_id).all()
        else:
            # Les superviseurs et administrateurs voient toutes les données de la campagne
            data = PromotionData.query.filter_by(campaign_id=campaign_id).all()
        
        return jsonify({
            'promotion_data': [item.to_dict() for item in data],
            'campaign': campaign.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
