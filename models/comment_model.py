from extensions import db
import datetime

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }