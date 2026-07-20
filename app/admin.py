from sqladmin import Admin, ModelView
from app.models.base import Base, User
from app.core.db import engine

def setup_admin(app):
    admin = Admin(app, engine=engine)

    # Register models for administration
    admin.add_view(UserView)

    return admin

class UserView(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.full_name, User.is_active, User.is_admin]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username]
    form_columns = [User.username, User.email, User.full_name, User.is_active, User.is_admin]
