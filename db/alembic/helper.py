from alembic import op


def execute_file(file):
    conn = op.get_bind()

    with open(file, 'r') as f:
        conn.execute(f.read())
