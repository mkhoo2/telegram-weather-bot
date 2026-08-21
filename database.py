import os
import psycopg

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL)


def initialize_database():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                subscribed BOOLEAN NOT NULL DEFAULT TRUE,
                report_time TEXT NOT NULL DEFAULT '07:00',
                timezone TEXT NOT NULL DEFAULT 'Asia/Singapore',
                latitude DOUBLE PRECISION NOT NULL DEFAULT 1.3521,
                longitude DOUBLE PRECISION NOT NULL DEFAULT 103.8198,
                last_sent_date TEXT
            );
        """)


def get_user(telegram_id):

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT
                telegram_id,
                subscribed,
                report_time,
                timezone,
                latitude,
                longitude,
                last_sent_date
            FROM users
            WHERE telegram_id = %s
        """, (telegram_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "telegram_id": row[0],
            "subscribed": row[1],
            "report_time": row[2],
            "timezone": row[3],
            "latitude": row[4],
            "longitude": row[5],
            "last_sent_date": row[6]
        }


def mark_report_sent(telegram_id, sent_date):

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE users
            SET last_sent_date = %s
            WHERE telegram_id = %s
            """,
            (sent_date, telegram_id)
        )


def subscribe_user(telegram_id):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO users (telegram_id)
            VALUES (%s)
            ON CONFLICT (telegram_id)
            DO UPDATE SET subscribed = TRUE
        """, (telegram_id,))


def unsubscribe_user(telegram_id):

    with get_connection() as connection:

        connection.execute("""
            UPDATE users
            SET subscribed = FALSE
            WHERE telegram_id = %s
        """, (telegram_id,))


def set_report_time(telegram_id, report_time):

    with get_connection() as connection:

        connection.execute("""
            UPDATE users
            SET report_time = %s
            WHERE telegram_id = %s
        """, (report_time, telegram_id))


def get_subscribed_users():

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT
                telegram_id,
                report_time,
                timezone,
                latitude,
                longitude,
                last_sent_date
            FROM users
            WHERE subscribed = TRUE
        """)

        return [
            {
                "telegram_id": row[0],
                "report_time": row[1],
                "timezone": row[2],
                "latitude": row[3],
                "longitude": row[4],
                "last_sent_date": row[5]
            }
            for row in cursor.fetchall()
        ]