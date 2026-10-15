import asyncio
from db import db

async def main():
    await db.connect()
    print('✅ БД подключена')
    print('✅ Таблицы созданы')
    await db.close()
    print('✅ Пул закрыт')

if __name__ == '__main__':
    asyncio.run(main())