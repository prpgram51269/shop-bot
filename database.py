import asyncpg


class Database:
    def __init__(self, url):
        self.url = url
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.url)
        await self._create_tables()

    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    role TEXT DEFAULT 'client',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.execute('''
                 CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2),
                    content_url	TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                 )
             ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id	SERIAL PRIMARY KEY,
                    user_id	BIGINT NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    total NUMERIC(10, 2) NOT NULL,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def add_user(self, telegram_id, username):
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''INSERT INTO users (telegram_id, username) 
                VALUES ($1, $2)
                ON CONFLICT (telegram_id) DO NOTHING''',
                telegram_id, username
            )

    async def get_user(self, telegram_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                '''SELECT * FROM users WHERE telegram_id = $1''',
                telegram_id
            )

    async def set_role(self, role, telegram_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''UPDATE users SET role = $1 WHERE telegram_id = $2''',
                role, telegram_id
            )

    async def add_product(self, name, description, price, content_url):
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''INSERT INTO products (name, description, price, content_url)
                VALUES ($1, $2, $3, $4)''',
                name, description, price, content_url
            )

    async def get_products(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''SELECT id, name, price FROM products  WHERE is_active = TRUE ORDER BY id'''
            )

    async def get_product(self, product_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                '''SELECT * FROM products WHERE id = $1''',
                product_id
            )

    async def create_order(self, user_id, product_id, quantity, total):
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''INSERT INTO orders (user_id, product_id, quantity, total) VALUES($1, $2, $3, $4)''',
                user_id, product_id, quantity, total
            )

    async def get_orders(self, status):
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                '''SELECT id, user_id, product_id, total, status, created_at
                              FROM orders
                              WHERE status = $1
                              ORDER BY id DESC''',
                status
            )

    async def update_order_status(self, order_id, status):
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''UPDATE orders
                   SET status = $1, updated_at = CURRENT_TIMESTAMP
                   WHERE id = $2''',
                status, order_id
            )
