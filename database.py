import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from security import hash_password, generate_salt


class Database:
    def __init__(self):
        self.db_path = os.path.join('db', 'ngo.db')
        self._create_tables()

    def _create_tables(self):
        """Crée les tables si elles n'existent pas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Table Administrateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS administrators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table Bénévoles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS volunteers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    availability TEXT,
                    areas_of_interest TEXT,
                    motivation TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table pour les tokens de réinitialisation de mot de passe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (admin_id) REFERENCES administrators(id)
                )
            ''')

            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query, params=None):
        """Exécute une requête avec des paramètres"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()

            if query.strip().upper().startswith('SELECT'):
                # Récupérer les noms des colonnes
                columns = [
                    description[0]
                    for description in cursor.description
                ]
                # Convertir les résultats en dictionnaires
                results = cursor.fetchall()
                return [
                    dict(zip(columns, row))
                    for row in results
                ]
            elif query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            return None

    # Méthodes pour les administrateurs
    def create_admin(self, name, email, password):
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        is_active = True
        created_at = datetime.now()
        query = '''
            INSERT INTO administrators (
                name, email, password_hash, salt, is_active, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (name, email, password_hash, salt, is_active, created_at)
        return self.execute_query(query, params)

    def get_all_admins(self):
        query = 'SELECT * FROM administrators ORDER BY created_at DESC'
        return self.execute_query(query)

    def get_admin_by_email(self, email):
        query = 'SELECT * FROM administrators WHERE email = ?'
        results = self.execute_query(query, (email,))
        return results[0] if results else None

    def verify_admin_credentials(self, email, password):
        admin = self.get_admin_by_email(email)
        print('admin+++', admin)

        if admin:
            if admin['is_active'] and admin['password_hash'] == hash_password(
                password, admin['salt']
            ):
                return {
                    'id': admin['id'],
                    'name': admin['name'],
                    'email': admin['email'],
                    'is_active': admin['is_active'],
                    'created_at': admin['created_at']
                }
        return None

    def get_admin_by_id(self, admin_id):
        query = 'SELECT * FROM administrators WHERE id = ?'
        results = self.execute_query(query, (admin_id,))
        return results[0] if results else None

    def update_admin(self, admin_id, name, email, password_hash,
                     salt, is_active):
        if password_hash is not None and salt is not None:
            query = '''
                UPDATE administrators
                SET name = ?, email = ?, password_hash = ?,
                    salt = ?, is_active = ?
                WHERE id = ?
            '''
            params = (name, email, password_hash, salt, is_active,
                      admin_id)
        else:
            query = '''
                UPDATE administrators
                SET name = ?, email = ?, is_active = ?
                WHERE id = ?
            '''
            params = (name, email, is_active, admin_id)
        return self.execute_query(query, params)

    def update_admin_status(self, admin_id, is_active):
        query = 'UPDATE administrators SET is_active = ? WHERE id = ?'
        return self.execute_query(query, (is_active, admin_id))

    def delete_admin(self, admin_id):
        query = 'DELETE FROM administrators WHERE id = ?'
        return self.execute_query(query, (admin_id,))

    # Méthodes pour les bénévoles
    def create_volunteer(
        self, name, email, phone, availability,
        motivation, status='pending'
    ):
        """Crée un nouveau bénévole"""
        query = '''
            INSERT INTO volunteers (
                name, email, phone, availability, motivation, status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (name, email, phone, availability, motivation, status)
        return self.execute_query(query, params)

    def get_all_volunteers(self):
        query = 'SELECT * FROM volunteers ORDER BY created_at DESC'
        return self.execute_query(query)

    def get_volunteer_by_id(self, volunteer_id):
        query = 'SELECT * FROM volunteers WHERE id = ?'
        results = self.execute_query(query, (volunteer_id,))
        return results[0] if results else None

    def update_volunteer_status(self, volunteer_id, status):
        query = 'UPDATE volunteers SET status = ? WHERE id = ?'
        return self.execute_query(query, (status, volunteer_id))

    # Méthodes pour la réinitialisation de mot de passe
    def create_password_reset_token(self, admin_id, token, expires_at):
        query = '''
            INSERT INTO password_reset_tokens (
                admin_id, token, expires_at
            )
            VALUES (?, ?, ?)
        '''
        params = (admin_id, token, expires_at)
        return self.execute_query(query, params)

    def get_valid_token(self, token):
        query = '''
            SELECT * FROM password_reset_tokens
            WHERE token = ?
            AND used = 0
            AND expires_at > datetime('now')
        '''
        results = self.execute_query(query, (token,))
        return results[0] if results else None

    def mark_token_as_used(self, token):
        query = 'UPDATE password_reset_tokens SET used = 1 WHERE token = ?'
        return self.execute_query(query, (token,))

    def reset_database(self):
        """Réinitialise la base de données en supprimant toutes les tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript('''
                DROP TABLE IF EXISTS administrators;
                DROP TABLE IF EXISTS volunteers;
                DROP TABLE IF EXISTS password_reset_tokens;
            ''')
            conn.commit()
            self._create_tables()

    def get_volunteer_by_email(self, email):
        """Récupère un bénévole par email"""
        query = 'SELECT * FROM volunteers WHERE email = ?'
        results = self.execute_query(query, (email,))
        return results[0] if results else None

    def create_reset_token(self, admin_id, token, expires_at):
        """Crée un nouveau token de réinitialisation de mot de passe"""
        query = '''
            INSERT INTO password_reset_tokens (
                admin_id, token, expires_at
            )
            VALUES (?, ?, ?)
        '''
        params = (admin_id, token, expires_at)
        return self.execute_query(query, params)

    def search_volunteers(self, status='', name='', email='', page=1,
                          per_page=5):
        """Recherche des bénévoles avec filtrage et pagination"""
        offset = (page - 1) * per_page

        query = '''
            SELECT * FROM volunteers
            WHERE 1=1
        '''
        params = []

        # Ajout des conditions de filtrage
        if status:
            query += ' AND status = ?'
            params.append(status)
        if name:
            query += ' AND LOWER(name) LIKE LOWER(?)'
            params.append(f'%{name}%')
        if email:
            query += ' AND LOWER(email) LIKE LOWER(?)'
            params.append(f'%{email}%')

        # Ajout de la pagination
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        volunteers = self.execute_query(query, params)

        count_query = '''
            SELECT COUNT(*) as total FROM volunteers WHERE 1=1
        '''
        count_params = []
        if name:
            count_query += ' AND LOWER(name) LIKE LOWER(?)'
            count_params.append(f'%{name}%')
        if email:
            count_query += ' AND LOWER(email) LIKE LOWER(?)'
            count_params.append(f'%{email}%')

        total = self.execute_query(count_query, count_params)[0]['total']

        return {
            'volunteers': volunteers,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }


# Instance globale de la base de données
db = Database()
