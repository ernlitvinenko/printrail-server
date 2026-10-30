from alembic.operations import MigrationScript, ops
from alembic.runtime.migration import MigrationContext

from .. import Base

_TRIGGER_PREFIX = "trg_audit_"
PROCESS_AUDIT_LOG_FNAME = "process_audit_log()"


def create_trigger(table_name: str) -> list[str]:
    return f"""
DROP TRIGGER IF EXISTS {_TRIGGER_PREFIX}{table_name} ON {table_name};
CREATE TRIGGER {_TRIGGER_PREFIX}{table_name}
                       AFTER INSERT OR
                   UPDATE OR
                   DELETE
                   ON {table_name}
                       FOR EACH ROW EXECUTE FUNCTION {PROCESS_AUDIT_LOG_FNAME};
""".split(";")


def drop_trigger(table_name: str) -> str:
    return f"""
DROP TRIGGER IF EXISTS {_TRIGGER_PREFIX}{table_name} ON {table_name};
"""


def process_revision_directives(
    context: MigrationContext, revision, directives: list[MigrationScript]
):
    script = directives[0]
    upgrade_ops = script.upgrade_ops
    downgrade_ops = script.downgrade_ops

    affected_tables = set()

    for op in upgrade_ops.ops:
        if isinstance(op, ops.CreateTableOp) and Base.metadata.tables.get(
            op.table_name
        ).info.get("has_audit_trigger"):
            affected_tables.add(op.table_name)

    for table_name in affected_tables:
        for command in create_trigger(table_name):
            upgrade_ops.ops.append(ops.ExecuteSQLOp(command))
        downgrade_ops.ops.insert(0, ops.ExecuteSQLOp(drop_trigger(table_name)))
