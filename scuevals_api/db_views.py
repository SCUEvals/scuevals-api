import sqlalchemy_views
from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable


class View(Table):
    is_view = True


class CreateView(sqlalchemy_views.CreateView):
    def __init__(self, view):
        super().__init__(view.__view__, view.__definition__)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    if hasattr(element.element, 'is_view') and element.element.is_view:
        return compiler.visit_drop_view(element)

    return compiler.visit_drop_table(element) + ' CASCADE'
