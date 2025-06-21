from app import crud, models, schemas
from app.database import SessionLocal, engine

def create_super_user():
    print("Создание таблиц в базе данных...")
    # Эта строка создаст все таблицы (agencies, realtors, и т.д.)
    models.Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы.")

    db = SessionLocal()
    try:
        # 1. Убедимся, что существует агентство для администраторов
        agency_name = "SuperAdmin Agency"
        agency = crud.get_agency_by_name(db, name=agency_name)
        if not agency:
            print(f"Создается агентство: {agency_name}")
            agency_data = schemas.AgencyCreate(name=agency_name, description="Агентство для системных администраторов")
            agency = crud.create_agency(db=db, agency=agency_data)
            print("Агентство создано.")
        else:
            print(f"Используется существующее агентство: {agency_name}")

        # 2. Проверяем, существует ли уже суперпользователь
        user_email = "superuser"
        user = crud.get_realtor_by_email(db, email=user_email)
        if not user:
            print(f"Создается суперпользователь '{user_email}'...")
            
            # Создаем пользователя с ролью админа
            # Я предполагаю, что ваша схема RealtorCreate принимает эти поля
            user_data = schemas.RealtorCreate(
                email=user_email,
                password="superuser",
                full_name="Super User",
                is_active=True,
                role=models.RealtorRoleEnum.admin # <-- Это ключевой момент
            )
            crud.create_realtor(db=db, realtor=user_data, agency_id=agency.id)
            print("\n--- Суперпользователь успешно создан! ---")
            print(f"Логин: superuser")
            print(f"Пароль: superuser")
            print("---------------------------------------")
        else:
            print(f"Пользователь '{user_email}' уже существует. Никаких действий не предпринято.")

    finally:
        db.close()

if __name__ == "__main__":
    create_super_user() 