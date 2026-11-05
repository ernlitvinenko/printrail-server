"""Tests for the audit-log model and Alembic trigger-generation logic.

The PostgreSQL trigger SQL itself cannot run on SQLite, but the Python logic
that generates it (create_trigger / drop_trigger / process_revision_directives)
is pure and is tested here directly.
"""

from alembic.operations import ops
from alembic.runtime.migration import MigrationContext
from alembic.script.revision import RevisionMap

from core.models.database import Base
from core.models.database.migrations.audit_injection import (
    _TRIGGER_PREFIX,
    create_trigger,
    drop_trigger,
    process_revision_directives,
)


class TestTriggerSQL:
    def test_create_trigger_sql_targets_table(self):
        stmts = create_trigger("account")
        joined = "\n".join(stmts)
        assert f"DROP TRIGGER IF EXISTS {_TRIGGER_PREFIX}account ON account" in joined
        assert (
            f"CREATE TRIGGER {_TRIGGER_PREFIX}account" in joined
        )
        assert "AFTER INSERT OR" in joined
        assert "EXECUTE FUNCTION" in joined

    def test_drop_trigger_sql(self):
        sql = drop_trigger("employee")
        assert f"DROP TRIGGER IF EXISTS {_TRIGGER_PREFIX}employee ON employee" in sql


class TestMigrationDirectiveHook:
    def _run_hook(self, table_infos: dict[str, bool]):
        """Build a migration with CreateTableOps for real metadata tables and run the hook."""

        from sqlalchemy import Column, Integer, Table

        metadata = Base.metadata
        tables = []
        for name, has_trigger in table_infos.items():
            if name not in metadata.tables:
                tbl = Table(
                    name,
                    metadata,
                    Column("id", Integer, primary_key=True),
                    info={"has_audit_trigger": has_trigger},
                )
            else:
                tbl = metadata.tables[name]
                tbl.info = {"has_audit_trigger": has_trigger}
            tables.append(tbl)

        upgrade_ops = ops.UpgradeOps(
            ops=[ops.CreateTableOp(table_name=t.name, columns=list(t.columns)) for t in tables]
        )
        downgrade_ops = ops.DowngradeOps(ops=[])
        script = type("MigrationScript", (object,), {})()
        script.upgrade_ops = upgrade_ops
        script.downgrade_ops = downgrade_ops

        process_revision_directives(None, None, [script])
        return upgrade_ops, downgrade_ops

    def test_audited_table_gets_trigger_ops(self):
        upgrade_ops, downgrade_ops = self._run_hook({"audit_target": True})
        sql_texts = [op.target_text for op in upgrade_ops.ops if hasattr(op, "target_text")]
        appended = [str(getattr(op, "sqltext", "")) for op in upgrade_ops.ops]
        joined = "\n".join(appended)
        assert f"{_TRIGGER_PREFIX}audit_target" in joined

        # Downgrade should contain the drop as the FIRST op.
        assert len(downgrade_ops.ops) >= 1
        first_drop = str(getattr(downgrade_ops.ops[0], "sqltext", ""))
        assert f"DROP TRIGGER IF EXISTS {_TRIGGER_PREFIX}audit_target" in first_drop

    def test_non_audited_table_is_skipped(self):
        upgrade_ops, downgrade_ops = self._run_hook({"plain_table": False})
        joined = "\n".join(str(getattr(op, "sqltext", "")) for op in upgrade_ops.ops)
        assert _TRIGGER_PREFIX in joined or joined == ""
        # nothing was appended for the plain table
        assert len(downgrade_ops.ops) == 0
