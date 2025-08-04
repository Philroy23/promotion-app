from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from main import db
from models.user import User

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if not (user.is_superviseur() or user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        if user.is_superviseur():
            users = User.query.filter_by(role='promotrice').all()
        else:
            users = User.query.all()
        
        return jsonify({
            'users': [u.to_dict() for u in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'Utilisateur cible non trouvé'}), 404
        
        if (current_user_id != user_id and 
            not (current_user.is_superviseur() or current_user.is_administrateur() or current_user.is_super_administrateur())):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        return jsonify({'user': target_user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'Utilisateur cible non trouvé'}), 404
        
        data = request.get_json()
        
        if current_user_id == user_id:
            if 'username' in data:
                existing_user = User.query.filter_by(username=data['username']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
                target_user.username = data['username']
            
            if 'email' in data:
                target_user.email = data['email']
            
            if 'password' in data and data['password']:
                target_user.set_password(data['password'])
            
            if 'role' in data and not (current_user.is_administrateur() or current_user.is_super_administrateur()):
                return jsonify({'error': 'Vous ne pouvez pas modifier votre rôle'}), 403
                
        elif current_user.is_administrateur() or current_user.is_super_administrateur():
            if 'username' in data:
                existing_user = User.query.filter_by(username=data['username']).first()
                if existing_user and existing_user.id != user_id:
                    return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
                target_user.username = data['username']
            
            if 'email' in data:
                target_user.email = data['email']
            
            if 'password' in data and data['password']:
                target_user.set_password(data['password'])
            
            if 'role' in data:
                if data['role'] == 'super_administrateur' and not current_user.is_super_administrateur():
                    return jsonify({'error': 'Seul le super administrateur peut créer d\'autres super administrateurs'}), 403
                target_user.role = data['role']
        else:
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        target_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Utilisateur mis à jour avec succès',
            'user': target_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if not (current_user.is_administrateur() or current_user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'Utilisateur cible non trouvé'}), 404
        
        if current_user_id == user_id:
            return jsonify({'error': 'Vous ne pouvez pas supprimer votre propre compte'}), 400
        
        if target_user.is_super_administrateur() and not current_user.is_super_administrateur():
            return jsonify({'error': 'Seul le super administrateur peut supprimer d\'autres super administrateurs'}), 403
        
        db.session.delete(target_user)
        db.session.commit()
        
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/promotrices', methods=['GET'])
@jwt_required()
def get_promotrices():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if not (user.is_superviseur() or user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        promotrices = User.query.filter_by(role='promotrice').all()
        
        return jsonify({
            'promotrices': [p.to_dict() for p in promotrices]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if not (user.is_superviseur() or user.is_administrateur() or user.is_super_administrateur()):
            return jsonify({'error': 'Permissions insuffisantes'}), 403
        
        stats = {
            'total_users': User.query.count(),
            'total_promotrices': User.query.filter_by(role='promotrice').count(),
            'total_superviseurs': User.query.filter_by(role='superviseur').count(),
            'total_administrateurs': User.query.filter_by(role='administrateur').count(),
            'total_super_administrateurs': User.query.filter_by(role='super_administrateur').count()
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
