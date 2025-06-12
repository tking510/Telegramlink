from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SlotUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    slot_type = db.Column(db.String(10), nullable=False, default=\'A\') # A or B
    played_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f\'<SlotUser {self.user_id}>\'

class WinRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    win_type = db.Column(db.String(20), nullable=False) # jackpot, bigWin, smallWin, lose
    code = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f\'<WinRecord {self.user_id} - {self.win_type}>\'
