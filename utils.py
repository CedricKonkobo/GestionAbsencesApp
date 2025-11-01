from models import Eleve, Cours, Seance, Presence, db
from datetime import datetime

def creer_seance(cours_id):
    seance = Seance(cours_id=cours_id, date=datetime.now().strftime("%Y-%m-%d %H:%M"))
    db.session.add(seance)
    db.session.commit()
    return seance

def marquer_presence(seance_id, eleve_id):
    if not Presence.query.filter_by(seance_id=seance_id, eleve_id=eleve_id).first():
        presence = Presence(seance_id=seance_id, eleve_id=eleve_id)
        db.session.add(presence)
        db.session.commit()