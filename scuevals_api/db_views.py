from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable


class View(Table):
    is_view = True


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    if hasattr(element.element, 'is_view') and element.element.is_view:
        return compiler.visit_drop_view(element)

    return compiler.visit_drop_table(element) + ' CASCADE'
