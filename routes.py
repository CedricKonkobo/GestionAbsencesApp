from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import *
from utils import *
from datetime import datetime

bp = Blueprint('routes', __name__)

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "adminpass"

SEANCE_ACTUELLE = None
# ---------- cloturer ----------
@bp.route('/cloturer-seance')
def cloturer_seance():
    seance_id = session.get('seance_actuelle')
    if seance_id:
        seance = Seance.query.get(seance_id)
        if seance:
            seance.cloture = True
            db.session.commit()
    session.pop('seance_actuelle', None)
    flash("Séance clôturée.")
    return redirect(url_for('routes.scan_prof'))


# ---------- dashboard ----------
@bp.route('/prof-dashboard')
def prof_dashboard():
    cours_nom = request.args.get('cours')
    seance_id = request.args.get('seance_id', type=int)

    cours = Cours.query.filter_by(nom=cours_nom).first()
    if not cours:
        flash("Cours inconnu.")
        return redirect(url_for('routes.login_prof'))

    seances = (Seance.query.filter_by(cours_id=cours.id)
                       .order_by(Seance.id.asc())   # asc = ancien → récent
                       .all())

    if not seances:
        presents, absents, seance_courante = [], [], None
    else:
        seance_courante = Seance.query.get(seance_id) if seance_id else seances[0]
        presents_ids = [p.eleve_id for p in Presence.query.filter_by(seance_id=seance_courante.id)]
        presents   = Eleve.query.filter(Eleve.id.in_(presents_ids)).all()
        absents    = Eleve.query.filter(Eleve.id.notin_(presents_ids)).all()

    return render_template('prof_dashboard.html',
                           cours=cours,
                           seances=seances,
                           seance_actuelle=seance_courante,
                           presents=presents,
                           absents=absents)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/scan-prof')
def scan_prof():
    return render_template('scan_prof.html')

@bp.route('/scan-cours', methods=['POST'])
def scan_cours():
    global SEANCE_ACTUELLE
    data = request.form['qr_data']
    if data.startswith("cours-"):
        cours_id = data.split("-")[1]
        cours = Cours.query.get(cours_id)
        if cours:
            seance = creer_seance(cours_id)
            SEANCE_ACTUELLE = seance.id
            return redirect(url_for('routes.session_created'))
    flash("QR code invalide.")
    return redirect(url_for('routes.scan_prof'))

@bp.route('/session-created')
def session_created():
    return render_template('session_created.html')

@bp.route('/scan-eleve')
def scan_eleve():
    return render_template('scan_eleve.html')

@bp.route('/marquer-presence', methods=['POST'])
def marquer_presence_route():
    global SEANCE_ACTUELLE
    data = request.form['qr_data']
    if data and SEANCE_ACTUELLE:
        eleve_id = data.split("-")[0]
        marquer_presence(SEANCE_ACTUELLE, eleve_id)
    return redirect(url_for('routes.scan_eleve'))

@bp.route('/login-prof', methods=['GET', 'POST'])
def login_prof():
    if request.method == 'POST':
        code = request.form['code']
        cours_nom = request.form['cours']
        cours = Cours.query.filter_by(nom=cours_nom).first()
        if cours and cours.professeur_id == code:
            seance = Seance.query.filter_by(cours_id=cours.id).order_by(Seance.id.desc()).first()
            return redirect(url_for('routes.prof_dashboard', cours=cours.nom))
    return render_template('login_prof.html')

@bp.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if login == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            return redirect(url_for('routes.admin_dashboard'))
        flash("Identifiants incorrects.")
    return render_template('login_admin.html')

@bp.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        type_ = request.form['type']
        if type_ == 'eleve':
            e = Eleve(id=request.form['id'], nom=request.form['nom'], prenom=request.form['prenom'])
            e.generer_qr_code()
            db.session.add(e)
        elif type_ == 'prof':
            p = Professeur(id=request.form['id'], nom=request.form['nom'], prenom=request.form['prenom'])
            db.session.add(p)
        elif type_ == 'cours':
            c = Cours(id=request.form['id'], nom=request.form['nom'], professeur_id=request.form['prof_id'])
            c.generer_qr_code()
            db.session.add(c)
        db.session.commit()
    eleves = Eleve.query.all()
    profs = Professeur.query.all()
    cours = Cours.query.all()
    return render_template('admin_dashboard.html', eleves=eleves, profs=profs, cours=cours)

