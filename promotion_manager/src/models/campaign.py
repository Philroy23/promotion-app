from database import db
from datetime import datetime, date

class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    available_gadgets = db.Column(db.Text, nullable=True)
    target_audience = db.Column(db.String(200), nullable=True)
    budget = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    promotion_data = db.relationship('PromotionData', backref='campaign', lazy=True)

    def is_current(self):
        today = date.today()
        return self.start_date <= today <= self.end_date

    def is_upcoming(self):
        today = date.today()
        return self.start_date > today

    def is_past(self):
        today = date.today()
        return self.end_date < today

    def get_total_sales(self):
        total = 0
        for data in self.promotion_data:
            total += data.products_sold or 0
        return total

    def get_total_people_approached(self):
        total = 0
        for data in self.promotion_data:
            total += data.people_approached or 0
        return total

    def get_total_people_purchased(self):
        total = 0
        for data in self.promotion_data:
            total += data.people_purchased or 0
        return total

    def get_campaign_conversion_rate(self):
        approached = self.get_total_people_approached()
        purchased = self.get_total_people_purchased()
        if approached > 0:
            return round((purchased / approached) * 100, 2)
        return 0

    def get_promoters_performance(self):
        performance = {}
        for data in self.promotion_data:
            promoter_name = data.promoter_name
            if promoter_name not in performance:
                performance[promoter_name] = {
                    'total_sales': 0,
                    'total_approached': 0,
                    'total_purchased': 0,
                    'missions_count': 0
                }
            
            performance[promoter_name]['total_sales'] += data.products_sold or 0
            performance[promoter_name]['total_approached'] += data.people_approached or 0
            performance[promoter_name]['total_purchased'] += data.people_purchased or 0
            performance[promoter_name]['missions_count'] += 1

        for promoter in performance:
            approached = performance[promoter]['total_approached']
            purchased = performance[promoter]['total_purchased']
            if approached > 0:
                performance[promoter]['conversion_rate'] = round((purchased / approached) * 100, 2)
            else:
                performance[promoter]['conversion_rate'] = 0

        return performance

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
            'is_current': self.is_current(),
            'is_upcoming': self.is_upcoming(),
            'is_past': self.is_past()
        }

    def __repr__(self):
        return f'<Campaign {self.name}>'
