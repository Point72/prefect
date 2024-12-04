"""Add block schema indexes

Revision ID: 9e2a1c08c6f1
Revises: 2d900af9cd07
Create Date: 2022-06-17 20:45:30.744575

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9e2a1c08c6f1"
down_revision = "2d900af9cd07"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f("ix_block_schema__block_type_id"),
        "block_schema",
        ["block_type_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_block_schema__created"), "block_schema", ["created"], unique=False
    )

    # there is already a unique index on this column, so this btree index is redundant
    op.drop_index(op.f("ix_block_schema__checksum"), table_name="block_schema")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_block_schema__created"), table_name="block_schema")
    op.drop_index(op.f("ix_block_schema__block_type_id"), table_name="block_schema")
    op.create_index(
        op.f("ix_block_schema__checksum"), "block_schema", ["checksum"], unique=False
    )
    # ### end Alembic commands ###