import asyncio
from app.database import engine, AsyncSessionLocal
from app.models import Brand, SerialRange
from sqlalchemy.ext.asyncio import AsyncSession


async def fill_database():
    async with AsyncSessionLocal() as session:
        # Иностранные бренды
        steinway = Brand(name="Steinway & Sons", country="Germany/USA", type="foreign", info="Премиальные рояли")
        session.add(steinway)
        await session.flush()

        yamaha = Brand(name="Yamaha", country="Japan", type="foreign", info="Японские фортепиано")
        session.add(yamaha)
        await session.flush()

        kawai = Brand(name="Kawai", country="Japan", type="foreign", info="Японские фортепиано")
        session.add(kawai)
        await session.flush()

        # Российские бренды
        red_october = Brand(name="Красный Октябрь", country="Russia", type="russian", info="Советские фортепиано")
        session.add(red_october)
        await session.flush()

        # Диапазоны для Steinway
        session.add_all([
            SerialRange(brand_id=steinway.id, serial_start=1, serial_end=1000, year=1850),
            SerialRange(brand_id=steinway.id, serial_start=1001, serial_end=2000, year=1860),
            SerialRange(brand_id=steinway.id, serial_start=2001, serial_end=3000, year=1870),
            SerialRange(brand_id=steinway.id, serial_start=3001, serial_end=4000, year=1880),
            SerialRange(brand_id=steinway.id, serial_start=4001, serial_end=5000, year=1890),
            SerialRange(brand_id=steinway.id, serial_start=5001, serial_end=6000, year=1900),
        ])

        # Диапазоны для Yamaha
        session.add_all([
            SerialRange(brand_id=yamaha.id, serial_start=1, serial_end=1000, year=1900),
            SerialRange(brand_id=yamaha.id, serial_start=1001, serial_end=2000, year=1910),
            SerialRange(brand_id=yamaha.id, serial_start=2001, serial_end=3000, year=1920),
            SerialRange(brand_id=yamaha.id, serial_start=3001, serial_end=4000, year=1930),
        ])

        # Диапазоны для Красный Октябрь
        session.add_all([
            SerialRange(brand_id=red_october.id, serial_start=1, serial_end=500, year=1920),
            SerialRange(brand_id=red_october.id, serial_start=501, serial_end=1000, year=1930),
            SerialRange(brand_id=red_october.id, serial_start=1001, serial_end=1500, year=1940),
        ])

        await session.commit()
        print("✅ Тестовые данные добавлены!")


if __name__ == "__main__":
    asyncio.run(fill_database())