from src.database import db # Import db from main.py
from datetime import datetime, date

class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Nouveaux champs pour les campagnes
    available_gadgets = db.Column(db.Text, nullable=True) # Ex: "Stylos, T-shirts, Casquettes"
    target_audience = db.Column(db.String(200), nullable=True) # Public cible
    budget = db.Column(db.Float, nullable=True) # Budget de la campagne

    # Relationships
    promotion_data = db.relationship('PromotionData', backref='campaign', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'available_gadgets': self.available_gadgets,
            'target_audience': self.target_audience,
            'budget': self.budget,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'conversion_rate': self.get_campaign_conversion_rate(),
            'promoters_performance': self.get_promoters_performance()
        }

    def get_total_sales(self):
        """Calcule le total des ventes pour cette campagne"""
        total = 0
        for data in self.promotion_data:
            total += data.products_sold
        return total

    def get_total_people_approached(self):
        """Calcule le total des personnes approchées pour cette campagne"""
        total = 0
        for data in self.promotion_data:
            total += data.people_approached
        return total

    def get_total_people_purchased(self):
        """Calcule le total des personnes ayant acheté pour cette campagne"""
        total = 0
        for data in self.promotion_data:
            total += data.people_purchased
        return total

    def get_campaign_conversion_rate(self):
        """Calcule le taux de conversion global de la campagne"""
        total_approached = self.get_total_people_approached()
        total_purchased = self.get_total_people_purchased()
        if total_approached == 0:
            return 0
        return round((total_purchased / total_approached) * 100, 2)

    def get_promoters_performance(self):
        """Retourne les performances de chaque promotrice pour cette campagne"""
        performance = {}
        for data in self.promotion_data:
            promoter_id = data.promoter_id
            if promoter_id not in performance:
                performance[promoter_id] = {
                    'name': data.promoter.username if data.promoter else 'Inconnu',
                    'total_sales': 0,
                    'total_approached': 0,
                    'total_purchased': 0,
                    'total_initial_stock': 0
                }
            
            performance[promoter_id]['total_sales'] += data.products_sold
            performance[promoter_id]['total_approached'] += data.people_approached
            performance[promoter_id]['total_purchased'] += data.people_purchased
            performance[promoter_id]['total_initial_stock'] += data.initial_stock

        # Calcul des pourcentages
        for promoter_id in performance:
            p = performance[promoter_id]
            if p['total_approached'] > 0:
                p['conversion_rate'] = round((p['total_purchased'] / p['total_approached']) * 100, 2)
            else:
                p['conversion_rate'] = 0
            
            if p['total_initial_stock'] > 0:
                p['sales_percentage'] = round((p['total_sales'] / p['total_initial_stock']) * 100, 2)
            else:
                p['sales_percentage'] = 0

        return performance

    def __repr__(self):
        return f'<Campaign {self.name}>'
