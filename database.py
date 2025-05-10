import sqlite3
from typing import Dict, List


def init_db():
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            user_id INTEGER PRIMARY KEY,
            cart_data TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_user_cart(user_id: int) -> Dict[str, int]:
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    cursor.execute('SELECT cart_data FROM carts WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        import json
        return json.loads(result[0])
    return {}


def update_user_cart(user_id: int, cart_data: Dict[str, int]):
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    import json
    cart_json = json.dumps(cart_data)
    cursor.execute('''
        INSERT OR REPLACE INTO carts (user_id, cart_data)
        VALUES (?, ?)
    ''', (user_id, cart_json))
    conn.commit()
    conn.close()


def clear_user_cart(user_id: int):
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM carts WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()