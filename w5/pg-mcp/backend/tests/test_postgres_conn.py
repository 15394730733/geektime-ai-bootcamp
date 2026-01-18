import asyncio
import asyncpg

async def test_postgres():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123456@localhost:5432/test_db')
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        print('Tables:', [t['tablename'] for t in tables])
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_postgres())
