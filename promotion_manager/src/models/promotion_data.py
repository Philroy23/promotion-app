from src.database import db # Import db from main.py
from datetime import datetime, date

class PromotionData(db.Model):
    __tablename__ = 'promotion_data'

    id = db.Column(db.Integer, primary_key=True)
    
    # Informations de base de la promotrice
    promoter_name = db.Column(db.String(100), nullable=False)
    promoter_contact = db.Column(db.String(50), nullable=True)
    
    # Informations du magasin et de la mission
    store_name = db.Column(db.String(100), nullable=False)
    mission_date = db.Column(db.Date, nullable=False)
    arrival_time = db.Column(db.Time, nullable=True)
    departure_time = db.Column(db.Time, nullable=True)
    
    # Gestion des stocks
    initial_stock = db.Column(db.Integer, default=0)
    products_sold = db.Column(db.Integer, default=0)
    remaining_stock = db.Column(db.Integer, default=0)
    
    # Performance commerciale
    people_approached = db.Column(db.Integer, default=0)
    people_purchased = db.Column(db.Integer, default=0)
    
    # Informations complémentaires
    customer_comments = db.Column(db.Text, nullable=True)
    gadgets_distributed = db.Column(db.String(200), nullable=True)
    
    # Relations avec les autres modèles
    promoter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_conversion_rate(self):
        """Calcule le taux de conversion pour cette entrée"""
        if self.people_approached == 0:
            return 0
        return round((self.people_purchased / self.people_approached) * 100, 2)

    def get_sales_percentage(self):
        """Calcule le pourcentage de ventes par rapport au stock initial"""
        if self.initial_stock == 0:
            return 0
        return round((self.products_sold / self.initial_stock) * 100, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'promoter_name': self.promoter_name,
            'promoter_contact': self.promoter_contact,
            'store_name': self.store_name,
            'mission_date': self.mission_date.isoformat() if self.mission_date else None,
            'arrival_time': self.arrival_time.strftime('%H:%M') if self.arrival_time else None,
            'departure_time': self.departure_time.strftime('%H:%M') if self.departure_time else None,
            'initial_stock': self.initial_stock,
            'products_sold': self.products_sold,
            'remaining_stock': self.remaining_stock,
            'people_approached': self.people_approached,
            'people_purchased': self.people_purchased,
            'customer_comments': self.customer_comments,
            'gadgets_distributed': self.gadgets_distributed,
            'promoter_id': self.promoter_id,
            'campaign_id': self.campaign_id,
            'conversion_rate': self.get_conversion_rate(),
            'sales_percentage': self.get_sales_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'promoter': self.promoter.to_dict() if self.promoter else None,
            'campaign': self.campaign.to_dict() if self.campaign else None
        }

    def __repr__(self):
        return f'<PromotionData {self.promoter_name} - {self.store_name}>'
