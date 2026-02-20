import argparse
from app import create_app
from extensions import db
from models import User


def create_admin(username: str, password: str, is_admin: bool = True):
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f'User "{username}" already exists (id={existing.id}).')
            return
        u = User(username=username, is_admin=is_admin)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        print(f'Created user "{username}" with id={u.id}.')


def main():
    parser = argparse.ArgumentParser(description='Seed admin user')
    parser.add_argument('--username', default='admin')
    parser.add_argument('--password', default='admin')
    parser.add_argument('--no-admin', action='store_true', help='Create a non-admin user')
    args = parser.parse_args()

    create_admin(args.username, args.password, is_admin=not args.no_admin)


if __name__ == '__main__':
    main()
