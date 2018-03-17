"""Add flagging

Revision ID: a6c8efa2274c
Revises: 5e1a65b96e72
Create Date: 2018-03-14 22:08:09.912322

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a6c8efa2274c'
down_revision = '5e1a65b96e72'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('reasons',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_reasons'))
                    )
    op.create_table('flags',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('flag_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
                    sa.Column('read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
                    sa.Column('comment', sa.Text(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('accused_student_id', sa.Integer(), nullable=False),
                    sa.Column('evaluation_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['accused_student_id'], ['students.id'],
                                            name=op.f('fk_flags_accused_student_id_students'), ondelete='cascade'),
                    sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'],
                                            name=op.f('fk_flags_evaluation_id_evaluations'), ondelete='set null'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_flags_user_id_users'),
                                            ondelete='set null'),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_flags')),
                    sa.UniqueConstraint('user_id', 'evaluation_id', name=op.f('uq_flags_user_id'))
                    )
    op.create_table('flag_reason',
                    sa.Column('flag_id', sa.Integer(), nullable=True),
                    sa.Column('reason_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['flag_id'], ['flags.id'], name=op.f('fk_flag_reason_flag_id_flags'),
                                            ondelete='cascade'),
                    sa.ForeignKeyConstraint(['reason_id'], ['reasons.id'],
                                            name=op.f('fk_flag_reason_reason_id_reasons')),
                    sa.UniqueConstraint('flag_id', 'reason_id', name=op.f('uq_flag_reason_flag_id'))
                    )


def downgrade():
    op.drop_table('flag_reason')
    op.drop_table('flags')
    op.drop_table('reasons')
