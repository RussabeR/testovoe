import asyncio
import asyncpg
import os
import sys
from datetime import datetime, timedelta, timezone
import random
import traceback


async def seed_database():
    try:

        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")

        if not all([user, password, database]):
            user = user or os.getenv("DB_USER")
            password = password or os.getenv("DB_PASS")
            database = database or os.getenv("DB_NAME")

        if not all([user, password, database]):
            print("❌ Ошибка: Не все переменные окружения заданы")
            print(f"POSTGRES_USER/DB_USER: {'✓' if user else '✗'}")
            print(f"POSTGRES_PASSWORD/DB_PASS: {'✓' if password else '✗'}")
            print(f"POSTGRES_DB/DB_NAME: {'✓' if database else '✗'}")
            return 1

        print(f"🔌 Подключаемся к БД: {database} как {user}")

        conn = await asyncpg.connect(
            user=user, password=password, database=database, host="db", port=5432
        )

        print("✅ Подключение к БД успешно")

        tables = await conn.fetch("""
                                  SELECT table_name
                                  FROM information_schema.tables
                                  WHERE table_schema = 'public'
                                  """)

        table_names = [table["table_name"] for table in tables]
        print(f"📊 Найденные таблицы: {table_names}")

        if "users" not in table_names:
            print("❌ Таблица 'users' не найдена. Возможно, миграции не выполнены?")
            await conn.close()
            return 1

        result = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"📊 Текущее количество пользователей: {result}")

        if result > 0:
            print("✅ База данных уже содержит данные, пропускаем заполнение")
            await conn.close()
            return 0

        print("🔄 Заполняем БД тестовыми данными...")

        async with conn.transaction():

            users = []

            usernames = [
                "alex",
                "masha",
                "dima",
                "anya",
                "serg",
                "lena",
                "vanya",
                "olga",
                "misha",
                "tanya",
                "kate",
                "petya",
                "nina",
                "igor",
                "sveta",
            ]

            domains = ["gmail.com", "yandex.ru", "mail.ru", "outlook.com"]

            for i in range(1, 11):
                try:

                    base_username = random.choice(usernames)
                    username = f"{base_username}{random.randint(1, 999)}"
                    username = username[:20]

                    email = f"{username}@{random.choice(domains)}"

                    is_active = random.random() < 0.9

                    created_at = datetime.now(timezone.utc) - timedelta(
                        days=random.randint(1, 90)
                    )

                    last_login = None
                    if is_active and random.random() < 0.7:
                        last_login = datetime.now(timezone.utc) - timedelta(
                            days=random.randint(0, 30)
                        )

                    user_id = await conn.fetchval(
                        """
                                                  INSERT INTO users (username, email, is_active, last_login, created_at,
                                                                     updated_at)
                                                  VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
                                                  """,
                        username,
                        email,
                        is_active,
                        last_login,
                        created_at,
                        created_at,
                    )
                    users.append(user_id)
                    print(
                        f"  ✓ Создан пользователь {username} (email: {email}, активен: {is_active})"
                    )

                except Exception as e:
                    print(f"  ✗ Ошибка при создании пользователя: {e}")
                    raise

            if "posts" not in table_names:
                print("⚠️ Таблица 'posts' не найдена, пропускаем создание постов")
            else:

                post_titles = [
                    "Моя первая запись в блоге",
                    "Размышления о программировании",
                    "Как я провел лето 2024",
                    "Обзор новых технологий",
                    "Путешествие в горы",
                    "Рецепт вкусного ужина",
                    "Спорт и здоровый образ жизни",
                    "Любимые книги месяца",
                    "Изучение английского языка",
                    "Как начать свой бизнес",
                ]

                post_contents = [
                    "Сегодня я хочу поделиться своими мыслями о современном программировании. Это очень интересная тема, которая требует глубокого изучения.",
                    "В этой статье я расскажу о своем опыте изучения новых технологий. За последний год я освоил несколько языков программирования.",
                    "Недавно я открыл для себя удивительный мир фотографии. Это хобби помогает мне расслабиться и увидеть красоту в обычных вещах.",
                    "Хочу обсудить важную тему, которая волнует многих разработчиков. Как сохранить баланс между работой и личной жизнью?",
                    "Делюсь впечатлениями от недавнего путешествия на Алтай. Это невероятное место с потрясающей природой и гостеприимными людьми.",
                    "После долгих экспериментов я наконец нашел идеальный рецепт пасты. Делюсь секретами приготовления итальянской кухни.",
                    "Тренировки изменили мою жизнь. Рассказываю, как начать заниматься спортом и не бросить через неделю.",
                    "Собрал список книг, которые должен прочитать каждый программист. Эти книги помогут вам стать лучше в профессии.",
                ]

                for user_id in users:

                    for j in range(random.randint(2, 6)):
                        try:

                            title = random.choice(post_titles)
                            if j > 0:
                                title = f"{title} (часть {j + 1})"
                            title = title[:100]

                            content = random.choice(post_contents)

                            if random.random() < 0.5:
                                content += " " + " ".join(
                                    ["слово"] * random.randint(5, 15)
                                )
                            content = content[:250]

                            await conn.execute(
                                """
                                               INSERT INTO posts (title, content, user_id)
                                               VALUES ($1, $2, $3)
                                               """,
                                title,
                                content,
                                user_id,
                            )
                        except Exception as e:
                            print(f"  ✗ Ошибка при создании поста: {e}")
                            raise
                    print(f"  ✓ Созданы посты для пользователя {user_id}")

            if "comments" in table_names and "posts" in table_names:

                post_ids = await conn.fetch("SELECT id FROM posts")
                post_id_list = [p["id"] for p in post_ids]

                if post_id_list:

                    comment_texts = [
                        "Отличный пост!",
                        "Спасибо, очень полезно",
                        "Интересное мнение",
                        "Полностью согласен",
                        "А я думаю иначе",
                        "Полезная информация",
                        "Жду продолжения",
                        "👍",
                        "Супер!",
                        "Классно написано",
                        "Спасибо за статью",
                    ]

                    comments_created = 0
                    for k in range(random.randint(20, 50)):
                        try:

                            await conn.execute(
                                """
                                               INSERT INTO comments (content, user_id, post_id)
                                               VALUES ($1, $2, $3)
                                               """,
                                random.choice(comment_texts),
                                random.choice(users),
                                random.choice(post_id_list),
                            )
                            comments_created += 1
                        except Exception as e:
                            print(f"  ✗ Ошибка при создании комментария: {e}")
                            continue
                    print(f"  ✓ Создано {comments_created} комментариев")

        users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        posts_count = (
            await conn.fetchval("SELECT COUNT(*) FROM posts")
            if "posts" in table_names
            else 0
        )
        comments_count = (
            await conn.fetchval("SELECT COUNT(*) FROM comments")
            if "comments" in table_names
            else 0
        )

        print("\n✅ База данных успешно заполнена тестовыми данными!")
        print("   📊 Статистика:")
        print(f"   👥 Пользователей: {users_count}")
        print(f"   📝 Постов: {posts_count}")
        print(f"   💬 Комментариев: {comments_count}")

        await conn.close()
        return 0

    except Exception as e:
        print(f"❌ Ошибка при заполнении БД: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(seed_database())
    sys.exit(exit_code)
