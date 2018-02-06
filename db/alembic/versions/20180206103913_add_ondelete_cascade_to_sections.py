"""Add ondelete cascade to sections

Revision ID: 3e029d844940
Revises: 9b53dd8832b6
Create Date: 2018-02-06 10:39:13.315878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e029d844940'
down_revision = '9b53dd8832b6'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('section_professor_section_id_fkey', 'section_professor', type_='foreignkey')
    op.create_foreign_key(
        op.f('fk_section_professor_section_id_sections'), 'section_professor', 'sections',
        ['section_id'], ['id'], ondelete='cascade'
    )


def downgrade():
    op.drop_constraint(op.f('fk_section_professor_section_id_sections'), 'section_professor', type_='foreignkey')
    op.create_foreign_key('section_professor_section_id_fkey', 'section_professor', 'sections', ['section_id'], ['id'])
