from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
from PIL import Image

db = SQLAlchemy()

class Eleve(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))
    qr_code_path = db.Column(db.String(200))

    def generer_qr_code(self):
        data = f"{self.id}-{self.nom}-{self.prenom}"
        qr = qrcode.make(data)
        path = f"static/qr_codes/eleves/{self.id}.png"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        qr.save(path)
        self.qr_code_path = path

class Professeur(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(50))
    prenom = db.Column(db.String(50))

class Cours(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    nom = db.Column(db.String(100))
    professeur_id = db.Column(db.String(20), db.ForeignKey('professeur.id'))
    qr_code_path = db.Column(db.String(200))

    def generer_qr_code(self):
        data = f"cours-{self.id}"
        qr = qrcode.make(data)
        path = f"static/qr_codes/cours/{self.id}.png"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        qr.save(path)
        self.qr_code_path = path

class Seance(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    cours_id    = db.Column(db.String(20), db.ForeignKey('cours.id'))
    date        = db.Column(db.String(50))
    cloture     = db.Column(db.Boolean, default=False)  
class Presence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seance_id = db.Column(db.Integer, db.ForeignKey('seance.id'))
    eleve_id = db.Column(db.String(20), db.ForeignKey('eleve.id'))