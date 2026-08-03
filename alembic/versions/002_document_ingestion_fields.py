"""Add ingestion tracking fields to documents table."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_document_ingestion"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
    )
    op.add_column("documents", sa.Column("chunk_count", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("error_message", sa.String(length=1024), nullable=True))
    op.add_column(
        "documents",
        sa.Column(
            "index_name",
            sa.String(length=128),
            nullable=False,
            server_default="vector_db_index",
        ),
    )
    op.create_index("ix_documents_status", "documents", ["status"])


def downgrade() -> None:
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_column("documents", "index_name")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "chunk_count")
    op.drop_column("documents", "status")
