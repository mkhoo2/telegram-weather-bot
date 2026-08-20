import sqlite3

DATABASE = "weather_bot.db"


def get_connection():
    return sqlite3.connect(DATABASE)

def initialize_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE users (
            telegram_id INTEGER PRIMARY KEY,
            subscribed INTEGER NOT NULL DEFAULT 1,
            report_time TEXT NOT NULL DEFAULT '07:00',
            timezone TEXT NOT NULL DEFAULT 'Asia/Singapore',
            latitude REAL,
            longitude REAL,
            last_sent_date TEXT
        );
    """)

    connection.commit()
    connection.close()

def mark_report_sent(telegram_id, sent_date):
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE users
            SET last_sent_date = ?
            WHERE telegram_id = ?
            """,
            (sent_date, telegram_id)
        )

        connection.commit()

    finally:
        connection.close()

def subscribe_user(telegram_id):

    connection = get_connection()

    connection.execute("""
        INSERT INTO users (telegram_id)
        VALUES (?)
        ON CONFLICT(telegram_id)
        DO UPDATE SET subscribed = 1
    """, (telegram_id,))

    connection.commit()
    connection.close()

def unsubscribe_user(telegram_id):

    connection = get_connection()

    connection.execute("""
        UPDATE users
        SET subscribed = 0
        WHERE telegram_id = ?
    """, (telegram_id,))

    connection.commit()
    connection.close()

def set_report_time(telegram_id, report_time):

    connection = get_connection()

    connection.execute("""
        UPDATE users
        SET report_time = ?
        WHERE telegram_id = ?
    """, (report_time, telegram_id))

    connection.commit()
    connection.close()

def get_subscribed_users():

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT
                telegram_id,
                report_time,
                timezone,
                latitude,
                longitude,
                last_sent_date
            FROM users
            WHERE subscribed = 1
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

    finally:
        connection.close()