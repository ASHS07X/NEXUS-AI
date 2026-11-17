
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "nexus.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            ai_analysis TEXT,
            resolution TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def create_ticket(data):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tickets (
            employee_name,
            title,
            description,
            category,
            priority,
            ai_analysis
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["employee_name"],
        data["title"],
        data["description"],
        data.get("category", "Other"),
        data.get("priority", "Medium"),
        data.get("ai_analysis", "")
    ))

    ticket_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return ticket_id


def get_all_tickets():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM tickets
        ORDER BY created_at DESC
    """)

    tickets = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return tickets


def update_ticket(ticket_id, status, resolution=None):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tickets
        SET status = ?,
            resolution = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, resolution, ticket_id))

    updated = cursor.rowcount

    connection.commit()
    connection.close()

    return updated > 0
