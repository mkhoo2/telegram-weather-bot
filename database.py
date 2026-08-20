import sqlite3

DATABASE = "weather_bot.db"


def get_connection():
    return sqlite3.connect(DATABASE)

def initialize_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            subscribed INTEGER NOT NULL DEFAULT 1,
            report_time TEXT NOT NULL DEFAULT '07:00',
            timezone TEXT NOT NULL DEFAULT 'Asia/Singapore'
        )
    """)

    connection.commit()
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

    cursor = connection.execute("""
        SELECT telegram_id, report_time, timezone
        FROM users
        WHERE subscribed = 1
    """)

    users = cursor.fetchall()

    connection.close()

    return users