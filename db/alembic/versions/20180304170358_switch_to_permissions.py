"""Switch to permissions

Revision ID: 75b3de1db013
Revises: bd5bc783b2c0
Create Date: 2018-03-04 17:03:58.195924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75b3de1db013'
down_revision = 'bd5bc783b2c0'
branch_labels = None
depends_on = None


def upgrade():

    op.rename_table('roles', 'permissions')
    op.rename_table('user_role', 'user_permission')

    op.alter_column('user_permission', 'role_id', new_column_name='permission_id')

    op.create_unique_constraint(op.f('uq_permissions_name'), 'permissions', ['name'])
    op.drop_constraint('uq_roles_name', 'permissions', type_='unique')
    op.create_unique_constraint(op.f('uq_user_permission_user_id'), 'user_permission', ['user_id', 'permission_id'])
    op.drop_constraint('uq_user_role_user_id', 'user_permission', type_='unique')

    conn = op.get_bind()

    conn.execute("""
alter table user_permission rename constraint "fk_user_role_role_id" to "fk_user_permission_permission_id";
alter table user_permission rename constraint "fk_user_role_user_id_users" to "fk_user_permission_user_id_users";
alter table permissions rename constraint "roles_pkey" to "pk_permissions";
alter sequence "roles_id_seq" rename to "permissions_id_seq";
                 """)


def downgrade():
    pass
