import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import json
import os


class Database:
    """SQLite database manager for restaurant searches"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data directory in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(project_root, 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'restaurants.db')

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create searches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                cuisine TEXT,
                price_range TEXT,
                sort_by TEXT,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results_count INTEGER
            )
        ''')

        # Create restaurants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER,
                place_id TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                rating REAL,
                price_level INTEGER,
                cuisine_type TEXT,
                distance REAL,
                url TEXT,
                phone TEXT,
                menu_items TEXT,
                lat REAL,
                lng REAL,
                FOREIGN KEY (search_id) REFERENCES searches (id)
            )
        ''')

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                place_id TEXT NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                rating REAL,
                price_level INTEGER,
                cuisine_type TEXT,
                distance REAL,
                url TEXT,
                phone TEXT,
                menu_items TEXT,
                lat REAL,
                lng REAL,
                opening_hours TEXT,
                ai_description TEXT,
                note TEXT,
                favorited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (user_id, place_id)
            )
        ''')

        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_date
            ON searches(search_date DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_place_id
            ON restaurants(place_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_username
            ON users(username)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_favorites
            ON favorites(user_id, favorited_at DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_place_lookup
            ON favorites(user_id, place_id)
        ''')

        conn.commit()
        conn.close()

    def save_search(
        self,
        location: str,
        cuisine: Optional[str],
        price_range: Optional[List[int]],
        sort_by: str,
        restaurants: List
    ) -> int:
        """
        Save a search and its results to the database

        Args:
            location: Search location (address)
            cuisine: Cuisine filter
            price_range: Price range filter
            sort_by: Sort method
            restaurants: List of Restaurant objects

        Returns:
            Search ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert price_range to string
        price_range_str = ','.join(map(str, price_range)) if price_range else None

        # Insert search record
        cursor.execute('''
            INSERT INTO searches (location, cuisine, price_range, sort_by, results_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (location, cuisine, price_range_str, sort_by, len(restaurants)))

        search_id = cursor.lastrowid

        # Insert restaurant records
        for restaurant in restaurants:
            menu_items_str = json.dumps(restaurant.menu_items) if restaurant.menu_items else None

            cursor.execute('''
                INSERT INTO restaurants (
                    search_id, place_id, name, address, rating, price_level,
                    cuisine_type, distance, url, phone, menu_items, lat, lng
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                search_id,
                restaurant.place_id,
                restaurant.name,
                restaurant.address,
                restaurant.rating,
                restaurant.price_level,
                restaurant.cuisine_type,
                restaurant.distance,
                restaurant.url,
                restaurant.phone,
                menu_items_str,
                restaurant.lat,
                restaurant.lng
            ))

        conn.commit()
        conn.close()

        return search_id

    def get_search_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent search history

        Args:
            limit: Maximum number of searches to return

        Returns:
            List of search dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, location, cuisine, price_range, sort_by,
                   search_date, results_count
            FROM searches
            ORDER BY search_date DESC
            LIMIT ?
        ''', (limit,))

        searches = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return searches

    def get_search_results(self, search_id: int) -> List[Dict]:
        """
        Get results for a specific search

        Args:
            search_id: Search ID

        Returns:
            List of restaurant dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT place_id, name, address, rating, price_level,
                   cuisine_type, distance, url, phone, menu_items, lat, lng
            FROM restaurants
            WHERE search_id = ?
        ''', (search_id,))

        restaurants = []
        for row in cursor.fetchall():
            restaurant = dict(row)
            # Parse menu_items JSON
            if restaurant['menu_items']:
                restaurant['menu_items'] = json.loads(restaurant['menu_items'])
            else:
                restaurant['menu_items'] = []
            restaurants.append(restaurant)

        conn.close()
        return restaurants

    def get_stats(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM searches')
        total_searches = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM restaurants')
        total_restaurants = cursor.fetchone()[0]

        cursor.execute('''
            SELECT cuisine, COUNT(*) as count
            FROM searches
            WHERE cuisine IS NOT NULL
            GROUP BY cuisine
            ORDER BY count DESC
            LIMIT 5
        ''')
        top_cuisines = cursor.fetchall()

        cursor.execute('''
            SELECT location, COUNT(*) as count
            FROM searches
            GROUP BY location
            ORDER BY count DESC
            LIMIT 5
        ''')
        top_locations = cursor.fetchall()

        conn.close()

        return {
            'total_searches': total_searches,
            'total_restaurants': total_restaurants,
            'top_cuisines': top_cuisines,
            'top_locations': top_locations
        }

    def clear_old_data(self, days: int = 30):
        """
        Clear searches older than specified days

        Args:
            days: Number of days to keep
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM restaurants
            WHERE search_id IN (
                SELECT id FROM searches
                WHERE search_date < datetime('now', '-' || ? || ' days')
            )
        ''', (days,))

        cursor.execute('''
            DELETE FROM searches
            WHERE search_date < datetime('now', '-' || ? || ' days')
        ''', (days,))

        conn.commit()
        deleted = cursor.rowcount
        conn.close()

        return deleted

    # ========== USER MANAGEMENT METHODS ==========

    def create_user(self, username: str, password: str) -> Optional[int]:
        """
        Create a new user account

        Args:
            username: Unique username
            password: Plain text password (will be hashed)

        Returns:
            User ID if successful, None if username exists
        """
        from app.models.user import User

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            user = User(username=username)
            user.set_password(password)

            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (username, user.password_hash))

            user_id = cursor.lastrowid
            conn.commit()
            return user_id

        except sqlite3.IntegrityError:
            # Username already exists
            return None
        finally:
            conn.close()

    def get_user_by_username(self, username: str):
        """
        Get user by username

        Args:
            username: Username to search for

        Returns:
            User object if found, None otherwise
        """
        from app.models.user import User

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, password_hash, created_at
            FROM users
            WHERE username = ?
        ''', (username,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                created_at=row['created_at']
            )
        return None

    def get_user_by_id(self, user_id: int):
        """
        Get user by ID (required by Flask-Login)

        Args:
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        from app.models.user import User

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, password_hash, created_at
            FROM users
            WHERE id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                created_at=row['created_at']
            )
        return None

    # ========== FAVORITES MANAGEMENT METHODS ==========

    def add_favorite(self, user_id: int, restaurant, note: Optional[str] = None) -> bool:
        """
        Add restaurant to user's favorites

        Args:
            user_id: User ID
            restaurant: Restaurant object with full data
            note: Optional user note

        Returns:
            True if added, False if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Serialize complex fields
            menu_items_json = json.dumps(restaurant.menu_items) if restaurant.menu_items else None
            opening_hours_json = json.dumps(restaurant.opening_hours) if restaurant.opening_hours else None

            cursor.execute('''
                INSERT INTO favorites (
                    user_id, place_id, name, address, rating, price_level,
                    cuisine_type, distance, url, phone, menu_items, lat, lng,
                    opening_hours, ai_description, note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                restaurant.place_id,
                restaurant.name,
                restaurant.address,
                restaurant.rating,
                restaurant.price_level,
                restaurant.cuisine_type,
                restaurant.distance,
                restaurant.url,
                restaurant.phone,
                menu_items_json,
                restaurant.lat,
                restaurant.lng,
                opening_hours_json,
                restaurant.ai_description,
                note
            ))

            conn.commit()
            return True

        except sqlite3.IntegrityError:
            # Already favorited
            return False
        finally:
            conn.close()

    def remove_favorite(self, user_id: int, place_id: str) -> bool:
        """
        Remove restaurant from user's favorites

        Args:
            user_id: User ID
            place_id: Google Places ID

        Returns:
            True if removed, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM favorites
            WHERE user_id = ? AND place_id = ?
        ''', (user_id, place_id))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def is_favorited(self, user_id: int, place_id: str) -> bool:
        """
        Check if restaurant is favorited by user

        Args:
            user_id: User ID
            place_id: Google Places ID

        Returns:
            True if favorited, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 1 FROM favorites
            WHERE user_id = ? AND place_id = ?
        ''', (user_id, place_id))

        exists = cursor.fetchone() is not None
        conn.close()

        return exists

    def get_user_favorites(self, user_id: int) -> List[Dict]:
        """
        Get all favorites for a user

        Args:
            user_id: User ID

        Returns:
            List of favorite dictionaries with full restaurant data
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, place_id, name, address, rating, price_level,
                   cuisine_type, distance, url, phone, menu_items, lat, lng,
                   opening_hours, ai_description, note, favorited_at
            FROM favorites
            WHERE user_id = ?
            ORDER BY favorited_at DESC
        ''', (user_id,))

        favorites = []
        for row in cursor.fetchall():
            fav = dict(row)
            # Parse JSON fields
            if fav['menu_items']:
                fav['menu_items'] = json.loads(fav['menu_items'])
            else:
                fav['menu_items'] = []

            if fav['opening_hours']:
                fav['opening_hours'] = json.loads(fav['opening_hours'])
            else:
                fav['opening_hours'] = None

            favorites.append(fav)

        conn.close()
        return favorites

    def update_favorite_note(self, user_id: int, place_id: str, note: str) -> bool:
        """
        Update note for a favorite

        Args:
            user_id: User ID
            place_id: Google Places ID
            note: New note text

        Returns:
            True if updated, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE favorites
            SET note = ?, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ? AND place_id = ?
        ''', (note, user_id, place_id))

        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated
