from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)
from database import db
from security import (
    generate_reset_token,
    hash_password,
    validate_password,
    validate_email,
    sanitize_input,
    generate_salt,
    login_required,
    admin_required
)
from datetime import datetime, timedelta
from flask_json_schema import JsonSchema, JsonValidationError
from schema import volunteer_schema
app = Flask(__name__)
schema = JsonSchema(app)
app.secret_key = 'my_super_secret_key'

# Configuration de la session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        pays = request.form.get('pays')
        montant = request.form.get('montant')
        message = request.form.get('message')

        print("Nouveau don reçu:")
        print(f"Nom: {nom}")
        print(f"Email: {email}")
        print(f"Pays: {pays}")
        print(f"Montant: {montant}$")
        print(f"Message: {message}")

        flash('Merci pour votre don ! '
              'Nous vous enverrons un reçu par email.', 'success')
        return redirect(url_for('donate'))
    return render_template('donate.html')


@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        availability = request.form.get('availability')
        motivation = request.form.get('motivation')

        existing_volunteer = db.get_volunteer_by_email(email)
        if existing_volunteer:
            flash('Vous êtes déjà inscrit.', 'danger')
            return redirect(url_for('volunteer'))

        db.create_volunteer(name, email, phone, availability, motivation)

        flash('Merci pour votre inscription ! '
              'Nous vous contacterons bientôt pour discuter '
              'des opportunités de bénévolat.', 'success')
        return redirect(url_for('volunteer'))
    return render_template('volunteer.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        sujet = request.form.get('sujet')
        message = request.form.get('message')

        print(f"Nom: {nom}")
        print(f"Email: {email}")
        print(f"Sujet: {sujet}")
        print(f"Message: {message}")

        flash(
            'Votre message a été envoyé avec succès. '
            'Nous vous répondrons dans les plus brefs délais.',
            'success'
        )
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        password = request.form.get('password')

        if not validate_email(email):
            flash('Email invalide.', 'danger')
            return redirect(url_for('admin_login'))
        admin = db.verify_admin_credentials(email, password)
        if admin:
            if not admin['is_active']:
                flash('Votre compte est désactivé.', 'danger')
                return redirect(url_for('admin_login'))

            # Création de la session
            session.permanent = True
            session['user_id'] = admin['id']
            session['user_email'] = admin['email']
            session['is_admin'] = True

            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Email ou mot de passe incorrect.', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    # flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('home'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Récupération des statistiques pour le tableau de bord
    stats = {
        'total_volunteers': len(db.get_all_volunteers()),
        'total_admins': len(db.get_all_admins()),
        'active_volunteers': len([
            v for v in db.get_all_volunteers()
            if v['status'] == 'active'
        ]),
        'pending_volunteers': len([
            v for v in db.get_all_volunteers()
            if v['status'] == 'pending'
        ]),
    }

    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/volunteers')
@admin_required
def admin_volunteers():
    volunteers = db.get_all_volunteers()
    return render_template('admin/volunteers.html', volunteers=volunteers)


@app.route('/admin/volunteers/<int:volunteer_id>', methods=['GET', 'POST'])
@admin_required
def admin_volunteer_details(volunteer_id):
    volunteer = db.get_volunteer_by_id(volunteer_id)
    if not volunteer:
        flash('Bénévole non trouvé.', 'danger')
        return redirect(url_for('admin_volunteers'))

    if request.method == 'POST':
        status = request.form.get('status')
        if status in ['pending', 'active', 'inactive']:
            db.update_volunteer_status(volunteer_id, status)
            flash('Statut du bénévole mis à jour avec succès.', 'success')
            return redirect(url_for('admin_volunteers'))

    return render_template('admin/volunteer_details.html', volunteer=volunteer)


@app.route('/admin/volunteers/filter', methods=['GET'])
@admin_required
def admin_filter_volunteers():
    status = request.args.get('status')
    volunteers = db.get_all_volunteers()

    if status:
        volunteers = [v for v in volunteers if v['status'] == status]

    return render_template('admin/volunteers.html', volunteers=volunteers)


@app.route(
    '/admin/volunteers/<int:volunteer_id>/edit',
    methods=['GET', 'POST']
)
@admin_required
def admin_update_volunteer(volunteer_id):
    volunteer = db.get_volunteer_by_id(volunteer_id)
    if not volunteer:
        flash('Bénévole non trouvé.', 'danger')
        return redirect(url_for('admin_volunteers'))

    if request.method == 'POST':
        status = request.form.get('status')
        if status in ['pending', 'active', 'inactive']:
            db.update_volunteer_status(volunteer_id, status)
            flash('Statut du bénévole mis à jour avec succès.', 'success')
            return redirect(url_for('admin_volunteers'))

    return render_template('admin/volunteer_details.html', volunteer=volunteer)


@app.route('/admin/administrators')
@admin_required
def admin_administrators():
    admins = db.get_all_admins()
    return render_template('admin/admins.html', admins=admins)


@app.route('/admin/administrators/new', methods=['GET', 'POST'])
@admin_required
def admin_new_administrator():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        password = request.form.get('password')
        name = sanitize_input(request.form.get('name'))

        if not validate_email(email):
            flash('Email invalide.', 'danger')
            return redirect(url_for('admin_administrators'))

        if not validate_password(password):
            flash('Le mot de passe doit contenir au moins 8 caractères.',
                  'danger')
            return redirect(url_for('admin_administrators'))

        if db.get_admin_by_email(email):
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('admin_administrators'))

        admin_id = db.create_admin(name, email, password)
        if admin_id:
            flash('Administrateur créé avec succès.', 'success')
            return redirect(url_for('admin_administrators'))

        flash('Erreur lors de la création de l\'administrateur.', 'danger')
        return redirect(url_for('admin_administrators'))

    return render_template('admin/admins.html')


@app.route(
        '/admin/administrators/<int:admin_id>/edit',
        methods=['GET', 'POST']
)
def admin_edit_administrator(admin_id):
    admin = db.get_admin_by_id(admin_id)
    if not admin:
        flash('Administrateur non trouvé.', 'danger')
        return redirect(url_for('admin_admins'))

    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))
        is_active = request.form.get('is_active') == '1'

        if not validate_email(email):
            flash('Email invalide.', 'danger')
            return redirect(url_for('admin_administrators', admin_id=admin_id))

        # Vérifier si l'email est déjà utilisé par un autre admin
        existing_admin = db.get_admin_by_email(email)
        if existing_admin and existing_admin['id'] != admin_id:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('admin_administrators', admin_id=admin_id))

        db.update_admin(admin_id, name, email, None, None, is_active)

        flash('Administrateur mis à jour avec succès.', 'success')
        return redirect(url_for('admin_administrators'))

    return render_template('admin/admins.html', admin=admin)


@app.route('/admin/administrators/<int:admin_id>/delete', methods=['POST'])
def admin_delete_admin(admin_id):
    db.delete_admin(admin_id)
    flash('Administrateur supprimé avec succès.', 'success')
    return redirect(url_for('admin_administrators'))


@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    admin = db.get_admin_by_id(session['user_id'])
    if not admin:
        flash('Administrateur non trouvé.', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin/profile.html', admin=admin)


@app.route('/admin/update_profile', methods=['POST'])
@admin_required
def admin_update_profile():
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))

        """ recuperer l'admin """
        admin = db.get_admin_by_id(session['user_id'])
        if not admin:
            flash('Administrateur non trouvé.', 'danger')
            return redirect(url_for('admin_login'))

        # Vérifier si l'email est déjà utilisé par un autre admin
        existing_admin = db.get_admin_by_email(email)

        if existing_admin and existing_admin['id'] != session['user_id']:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('admin_profile'))

        db.update_admin(session['user_id'], name, email,
                        None, None, admin['is_active'])
        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('admin_profile'))


@app.route('/admin/change_password', methods=['POST'])
@admin_required
def admin_change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('admin_profile'))

        if not validate_password(new_password):
            flash(
                'Le mot de passe doit contenir au moins 8 caractères.',
                'danger'
            )
            return redirect(url_for('admin_profile'))

        """ recuperer l'admin """
        admin = db.get_admin_by_id(session['user_id'])
        if not admin:
            flash('Administrateur non trouvé.', 'danger')
            return redirect(url_for('admin_login'))

        if admin['password_hash'] != hash_password(current_password,
                                                   admin['salt']):
            flash('Mot de passe actuel incorrect.', 'danger')
            return redirect(url_for('admin_profile'))

        salt = generate_salt()
        password_hash = hash_password(new_password, salt)
        db.update_admin(admin['id'], admin['name'],
                        admin['email'], password_hash, salt,
                        admin['is_active'])

        flash('Mot de passe modifié avec succès.', 'success')
        return redirect(url_for('admin_profile'))


@app.route('/admin/reset_password', methods=['GET', 'POST'])
def admin_reset_password():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email'))
        if not validate_email(email):
            flash('Email invalide.', 'danger')
            return redirect(url_for('admin_reset_password'))

        admin = db.get_admin_by_email(email)
        if not admin:
            flash('Administrateur non trouvé.', 'danger')
            return redirect(url_for('admin_reset_password'))

        expires_at = datetime.utcnow() + timedelta(hours=1)
        token = generate_reset_token()
        db.create_reset_token(admin['id'], token, expires_at)

        reset_url = url_for('admin_reset_password',
                            token=token, _external=True)
        print('reset_url', reset_url)
        # send_reset_email(email, reset_url)

        flash('Un lien de réinitialisation a été envoyé à votre email.',
              'success')
        return redirect(url_for('admin_login'))

    return render_template('admin/reset_password.html')

@app.route('/api/volunteers', methods=['POST'])
@schema.validate(volunteer_schema)
def create_volunteer():
    data = request.get_json()
    db.create_volunteer(data['name'], data['email'], data['phone'],
                        data['availability'], data['motivation'])
    return jsonify({'message': 'Volontariat créé avec succès.'}), 201

@app.route('/api/volunteers', methods=['GET'])
def get_volunteers():
    volunteers = db.get_all_volunteers()
    return jsonify(volunteers), 200

@app.route('/api/volunteers/<int:volunteer_id>', methods=['GET'])
def get_volunteer(volunteer_id):
    volunteer = db.get_volunteer_by_id(volunteer_id)
    if not volunteer:
        return jsonify({'error': 'Volontariat non trouvé.'}), 404
    return jsonify(volunteer), 200

# update volunteer
@app.route('/api/volunteers/<int:volunteer_id>', methods=['PUT'])
@schema.validate(volunteer_schema)
def update_volunteer(volunteer_id):
    data = request.get_json()
    db.update_volunteer(volunteer_id, data)
    return jsonify({'message': 'Volontariat mis à jour avec succès.'}), 200

# delete volunteer
@app.route('/api/volunteers/<int:volunteer_id>', methods=['DELETE'])
def delete_volunteer(volunteer_id):
    db.delete_volunteer(volunteer_id)
    return jsonify({'message': 'Volontariat supprimé avec succès.'}), 200

@app.route('/api/volunteers/search', methods=['GET'])
def filter_volunteers():
    name = request.args.get('name', '')
    email = request.args.get('email', '')
    page = request.args.get('page', '1')
    
    try:
        page = int(page)
    except ValueError:
        page = 1
        
    result = db.search_volunteers(name=name, email=email, page=page)
    return jsonify(result), 200

@app.route('/api/doc', methods=['GET'])
def doc():
    return render_template('doc.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    return jsonify({'error': e.message, 'errors': errors}), 400


if __name__ == '__main__':
    app.run(debug=True)
