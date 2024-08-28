import alembic.script
import sqlalchemy as sa


def generate_ordered_migration_name(context) -> str:
    head_revision = alembic.script.ScriptDirectory.from_config(context.config).get_current_head()
    if head_revision is None:
        new_rev_id = 1
    else:
        try:
            last_rev_id = int(head_revision.lstrip("0"))
        except ValueError:
            last_rev_id = 100
        new_rev_id = last_rev_id + 1

    return f"{new_rev_id:04d}"


def process_revision_directives(context, revision, directives):
    rev_id = generate_ordered_migration_name(context)
    for directive in directives:
        directive.rev_id = rev_id


def run_migrations_offline(context, target_metadata: sa.MetaData):
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(context, target_metadata: sa.MetaData):
    connectable = sa.engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=sa.pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )
        with context.begin_transaction():
            context.run_migrations()
