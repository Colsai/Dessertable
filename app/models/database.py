"""
Database module supporting both SQLite (development) and PostgreSQL (production).

MIGRATION STATUS: ✅ COMPLETE
- ✅ Infrastructure: DB type detection, connection pooling, helper methods
- ✅ Schema: Both SQLite and PostgreSQL table creation implemented
- ✅ All methods migrated to use database-agnostic helpers

HELPER METHODS:
- self.get_connection() - Get DB connection with proper row factory
- self.placeholder() - Get '?' or '%s' based on DB type
- self.execute_insert(cursor, query, params) - INSERT with ID return
- self.date_interval(days) - Get DB-specific date arithmetic
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import json
import os

try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class Database:
    """Database manager supporting both SQLite (development) and PostgreSQL (production)"""

    def __init__(self, db_path: str = None):
        # Check for PostgreSQL connection string
        database_url = os.getenv('DATABASE_URL')

        if database_url and POSTGRES_AVAILABLE:
            # Render provides postgres:// but psycopg2 needs postgresql://
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)

            self.db_type = 'postgresql'
            self.db_url = database_url
            self._init_database_postgres()
        else:
            # SQLite for local development
            self.db_type = 'sqlite'
            if db_path is None:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                data_dir = os.path.join(project_root, 'data')
                os.makedirs(data_dir, exist_ok=True)
                db_path = os.path.join(data_dir, 'restaurants.db')

            self.db_path = db_path
            self._init_database_sqlite()

    def get_connection(self):
        """Get database connection based on type"""
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        else:  # postgresql
            conn = psycopg2.connect(self.db_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            return conn

    def placeholder(self):
        """Return appropriate placeholder for database type"""
        return '?' if self.db_type == 'sqlite' else '%s'

    def execute_insert(self, cursor, query, params):
        """Execute INSERT and return the inserted ID, handling database differences"""
        if self.db_type == 'sqlite':
            cursor.execute(query, params)
            return cursor.lastrowid
        else:  # postgresql - use RETURNING id
            # Modify query to add RETURNING id if not present
            if 'RETURNING' not in query.upper():
                query = query.rstrip(';').rstrip() + ' RETURNING id'
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['id'] if result else None

    def date_interval(self, days: int) -> str:
        """Return SQL expression for 'now minus N days' based on database type"""
        if self.db_type == 'sqlite':
            return f"datetime('now', '-{days} days')"
        else:
            return f"NOW() - INTERVAL '{days} days'"

    def _init_database_sqlite(self):
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

    def _init_database_postgres(self):
        """Initialize PostgreSQL database tables"""
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()

        # Create searches table (change AUTOINCREMENT to SERIAL)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS searches (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
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

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_date ON searches(search_date DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_place_id ON restaurants(place_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_favorites ON favorites(user_id, favorited_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_place_lookup ON favorites(user_id, place_id)')

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
        conn = self.get_connection()
        cursor = conn.cursor()

        # Convert price_range to string
        price_range_str = ','.join(map(str, price_range)) if price_range else None

        ph = self.placeholder()
        # Insert search record
        search_id = self.execute_insert(
            cursor,
            f'INSERT INTO searches (location, cuisine, price_range, sort_by, results_count) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})',
            (location, cuisine, price_range_str, sort_by, len(restaurants))
        )

        # Insert restaurant records
        for restaurant in restaurants:
            menu_items_str = json.dumps(restaurant.menu_items) if restaurant.menu_items else None

            cursor.execute(f'''
                INSERT INTO restaurants (
                    search_id, place_id, name, address, rating, price_level,
                    cuisine_type, distance, url, phone, menu_items, lat, lng
                )
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
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
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT id, location, cuisine, price_range, sort_by,
                   search_date, results_count
            FROM searches
            ORDER BY search_date DESC
            LIMIT {ph}
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
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT place_id, name, address, rating, price_level,
                   cuisine_type, distance, url, phone, menu_items, lat, lng
            FROM restaurants
            WHERE search_id = {ph}
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
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as cnt FROM searches')
        total_searches = cursor.fetchone()['cnt']

        cursor.execute('SELECT COUNT(*) as cnt FROM restaurants')
        total_restaurants = cursor.fetchone()['cnt']

        cursor.execute('''
            SELECT cuisine, COUNT(*) as count
            FROM searches
            WHERE cuisine IS NOT NULL
            GROUP BY cuisine
            ORDER BY count DESC
            LIMIT 5
        ''')
        top_cuisines = [(row['cuisine'], row['count']) for row in cursor.fetchall()]

        cursor.execute('''
            SELECT location, COUNT(*) as count
            FROM searches
            GROUP BY location
            ORDER BY count DESC
            LIMIT 5
        ''')
        top_locations = [(row['location'], row['count']) for row in cursor.fetchall()]

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
        conn = self.get_connection()
        cursor = conn.cursor()

        date_threshold = self.date_interval(days)

        cursor.execute(f'''
            DELETE FROM restaurants
            WHERE search_id IN (
                SELECT id FROM searches
                WHERE search_date < {date_threshold}
            )
        ''')

        cursor.execute(f'''
            DELETE FROM searches
            WHERE search_date < {date_threshold}
        ''')

        conn.commit()
        deleted = cursor.rowcount
        conn.close()

        return deleted

    # ========== ADMIN ANALYTICS METHODS ==========

    def get_admin_analytics(self) -> Dict:
        """
        Get comprehensive analytics for admin dashboard

        Returns:
            Dictionary with various analytics metrics
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        analytics = {}

        # Date thresholds
        date_7_days = self.date_interval(7)
        date_30_days = self.date_interval(30)

        # Date function for extracting date part
        date_func = "DATE" if self.db_type == 'sqlite' else "DATE"

        # User statistics
        cursor.execute('SELECT COUNT(*) as cnt FROM users')
        analytics['total_users'] = cursor.fetchone()['cnt']

        cursor.execute(f'''
            SELECT COUNT(*) as cnt FROM users
            WHERE created_at >= {date_7_days}
        ''')
        analytics['users_last_7_days'] = cursor.fetchone()['cnt']

        cursor.execute(f'''
            SELECT COUNT(*) as cnt FROM users
            WHERE created_at >= {date_30_days}
        ''')
        analytics['users_last_30_days'] = cursor.fetchone()['cnt']

        # Search statistics
        cursor.execute('SELECT COUNT(*) as cnt FROM searches')
        analytics['total_searches'] = cursor.fetchone()['cnt']

        cursor.execute(f'''
            SELECT COUNT(*) as cnt FROM searches
            WHERE search_date >= {date_7_days}
        ''')
        analytics['searches_last_7_days'] = cursor.fetchone()['cnt']

        cursor.execute(f'''
            SELECT COUNT(*) as cnt FROM searches
            WHERE search_date >= {date_30_days}
        ''')
        analytics['searches_last_30_days'] = cursor.fetchone()['cnt']

        # Average results per search
        cursor.execute('SELECT AVG(results_count) as avg FROM searches')
        avg_results = cursor.fetchone()['avg']
        analytics['avg_results_per_search'] = round(avg_results, 1) if avg_results else 0

        # Favorite statistics
        cursor.execute('SELECT COUNT(*) as cnt FROM favorites')
        analytics['total_favorites'] = cursor.fetchone()['cnt']

        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) as cnt FROM favorites
        ''')
        analytics['users_with_favorites'] = cursor.fetchone()['cnt']

        # Top locations (last 30 days)
        cursor.execute(f'''
            SELECT location, COUNT(*) as count
            FROM searches
            WHERE search_date >= {date_30_days}
            GROUP BY location
            ORDER BY count DESC
            LIMIT 10
        ''')
        analytics['top_locations_30d'] = [dict(row) for row in cursor.fetchall()]

        # Recent searches with location details
        cursor.execute('''
            SELECT location, search_date, results_count
            FROM searches
            ORDER BY search_date DESC
            LIMIT 20
        ''')
        analytics['recent_searches'] = [dict(row) for row in cursor.fetchall()]

        # Search trend by day (last 30 days)
        cursor.execute(f'''
            SELECT
                {date_func}(search_date) as date,
                COUNT(*) as count
            FROM searches
            WHERE search_date >= {date_30_days}
            GROUP BY {date_func}(search_date)
            ORDER BY date DESC
        ''')
        analytics['search_trend'] = [dict(row) for row in cursor.fetchall()]

        # User registration trend (last 30 days)
        cursor.execute(f'''
            SELECT
                {date_func}(created_at) as date,
                COUNT(*) as count
            FROM users
            WHERE created_at >= {date_30_days}
            GROUP BY {date_func}(created_at)
            ORDER BY date DESC
        ''')
        analytics['user_trend'] = [dict(row) for row in cursor.fetchall()]

        # Most active users (by search count)
        cursor.execute('''
            SELECT
                u.username,
                COUNT(DISTINCT f.id) as favorite_count
            FROM users u
            LEFT JOIN favorites f ON f.user_id = u.id
            GROUP BY u.id, u.username
            ORDER BY favorite_count DESC
            LIMIT 10
        ''')
        analytics['active_users'] = [dict(row) for row in cursor.fetchall()]

        # Popular cuisines (all time)
        cursor.execute('''
            SELECT cuisine, COUNT(*) as count
            FROM searches
            WHERE cuisine IS NOT NULL AND cuisine != ''
            GROUP BY cuisine
            ORDER BY count DESC
            LIMIT 10
        ''')
        analytics['popular_cuisines'] = [dict(row) for row in cursor.fetchall()]

        # Database size metrics
        cursor.execute('SELECT COUNT(*) as cnt FROM restaurants')
        analytics['total_restaurants_cached'] = cursor.fetchone()['cnt']

        conn.close()
        return analytics

    def get_all_users(self, limit: int = 100) -> List[Dict]:
        """
        Get list of all users with their statistics

        Args:
            limit: Maximum number of users to return

        Returns:
            List of user dictionaries with stats
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT
                u.id,
                u.username,
                u.created_at,
                COUNT(DISTINCT f.id) as favorite_count
            FROM users u
            LEFT JOIN favorites f ON f.user_id = u.id
            GROUP BY u.id, u.username, u.created_at
            ORDER BY u.created_at DESC
            LIMIT {ph}
        ''', (limit,))

        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

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

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            user = User(username=username)
            user.set_password(password)

            ph = self.placeholder()
            user_id = self.execute_insert(
                cursor,
                f'INSERT INTO users (username, password_hash) VALUES ({ph}, {ph})',
                (username, user.password_hash)
            )

            conn.commit()
            return user_id

        except (sqlite3.IntegrityError, psycopg2.IntegrityError if POSTGRES_AVAILABLE else Exception):
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

        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT id, username, password_hash, created_at
            FROM users
            WHERE username = {ph}
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

        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT id, username, password_hash, created_at
            FROM users
            WHERE id = {ph}
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
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Serialize complex fields
            menu_items_json = json.dumps(restaurant.menu_items) if restaurant.menu_items else None
            opening_hours_json = json.dumps(restaurant.opening_hours) if restaurant.opening_hours else None

            ph = self.placeholder()
            cursor.execute(f'''
                INSERT INTO favorites (
                    user_id, place_id, name, address, rating, price_level,
                    cuisine_type, distance, url, phone, menu_items, lat, lng,
                    opening_hours, ai_description, note
                )
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
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

        except (sqlite3.IntegrityError, psycopg2.IntegrityError if POSTGRES_AVAILABLE else Exception):
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
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            DELETE FROM favorites
            WHERE user_id = {ph} AND place_id = {ph}
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
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT 1 FROM favorites
            WHERE user_id = {ph} AND place_id = {ph}
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
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            SELECT id, place_id, name, address, rating, price_level,
                   cuisine_type, distance, url, phone, menu_items, lat, lng,
                   opening_hours, ai_description, note, favorited_at
            FROM favorites
            WHERE user_id = {ph}
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
        conn = self.get_connection()
        cursor = conn.cursor()

        ph = self.placeholder()
        cursor.execute(f'''
            UPDATE favorites
            SET note = {ph}, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = {ph} AND place_id = {ph}
        ''', (note, user_id, place_id))

        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return updated
