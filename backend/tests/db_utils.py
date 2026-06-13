from sqlalchemy import text


async def drop_enum_types(conn) -> None:
    """Drop all custom PostgreSQL ENUM types before create_all.

    SQLAlchemy 2.0.50 + Python 3.13: drop_all does not remove ENUM types,
    causing UniqueViolationError on the next create_all.
    """
    result = await conn.execute(text(
        "SELECT typname FROM pg_type "
        "WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public') "
        "AND typtype = 'e'"
    ))
    for (typename,) in result:
        await conn.execute(text(f'DROP TYPE IF EXISTS "{typename}" CASCADE'))
