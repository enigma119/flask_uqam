import sqlite3
from database import Database


def reset_database():
    """Réinitialise la base de données en supprimant toutes les tables"""
    db = Database()
    db.reset_database()
    print("Base de données réinitialisée.")


def init_database(reset=False):
    if reset:
        reset_database()

    # Création de l'instance de la base de données
    db = Database()

    # Création des administrateurs de test
    admin_data = [
        {
            'name': 'Admin Principal',
            'email': 'admin@example.com',
            'password': 'admin123'
        },
        {
            'name': 'Modérateur',
            'email': 'moderator@example.com',
            'password': 'admin123'
        },
        {
            'name': 'Support',
            'email': 'support@example.com',
            'password': 'admin123'
        }
    ]

    for admin in admin_data:
        try:
            # Vérifier si l'administrateur existe déjà
            existing_admin = db.get_admin_by_email(admin['email'])
            if existing_admin:
                print(f"L'administrateur {admin['name']} existe déjà.")
                continue

            db.create_admin(
                name=admin['name'],
                email=admin['email'],
                password=admin['password']
            )
            print(f"Administrateur {admin['name']} créé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création de l'administrateur
                  {admin['name']}: {str(e)}")

    # Insertion des bénévoles de test
    volunteer_data = [
        {
            'name': 'Jean Dupont',
            'email': 'jean.dupont@example.com',
            'phone': '514-555-0123',
            'availability': 'Fins de semaine',
            'motivation':
            'Je souhaite contribuer à la protection de l\'environnement.',
            'status': 'active'
        },
        {
            'name': 'Marie Martin',
            'email': 'marie.martin@example.com',
            'phone': '514-555-0124',
            'availability': 'Soirées',
            'motivation': 'Je veux aider les enfants défavorisés.',
            'status': 'pending'
        },
        {
            'name': 'Pierre Tremblay',
            'email': 'pierre.tremblay@example.com',
            'phone': '514-555-0125',
            'availability': 'Journée',
            'motivation': 'Je suis retraité et j\'ai du temps à donner.',
            'status': 'active'
        },
        {
            'name': 'Sophie Lavoie',
            'email': 'sophie.lavoie@example.com',
            'phone': '514-555-0126',
            'availability': 'Variable',
            'motivation':
            'Je veux mettre mes compétences au service de la communauté.',
            'status': 'inactive'
        },
        {
            'name': 'Lucas Bouchard',
            'email': 'lucas.bouchard@example.com',
            'phone': '514-555-0127',
            'availability': 'Fins de semaine',
            'motivation':
            'Je souhaite partager mes connaissances en informatique.',
            'status': 'pending'
        }
    ]

    for volunteer in volunteer_data:
        try:
            # Vérifier si le bénévole existe déjà
            existing_volunteer = db.get_volunteer_by_email(volunteer['email'])
            if existing_volunteer:
                print(f"Le bénévole {volunteer['name']} existe déjà.")
                continue

            db.create_volunteer(
                name=volunteer['name'],
                email=volunteer['email'],
                phone=volunteer['phone'],
                availability=volunteer['availability'],
                motivation=volunteer['motivation'],
                status=volunteer['status']
            )
            print(f"Bénévole {volunteer['name']} créé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création du bénévole
                  {volunteer['name']}: {str(e)}")

    print("\nInitialisation de la base de données terminée.")


if __name__ == '__main__':
    import sys
    reset = '--reset' in sys.argv
    init_database(reset)
