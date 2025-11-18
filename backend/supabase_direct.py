"""
Direct Supabase Client using raw SQL queries
Works without supabase-py package by using direct SQL execution
"""
import os
import json
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def execute_sql_direct(query: str) -> Dict[str, Any]:
    """
    Execute SQL query directly using psycopg2 or similar
    This is a simplified version - in production, use proper connection pooling
    """
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("VITE_SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")

    if not url or not key:
        return {"data": [], "error": "Supabase credentials not configured"}

    try:
        # Try using psycopg2 if available
        import psycopg2
        import psycopg2.extras

        # Extract connection details from Supabase URL
        # Format: https://PROJECT.supabase.co
        project_ref = url.replace("https://", "").replace(".supabase.co", "")

        # Construct PostgreSQL connection string
        conn_str = f"postgresql://postgres.{project_ref}:postgres@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

        conn = psycopg2.connect(conn_str, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(query)

        if query.strip().upper().startswith('SELECT'):
            results = cur.fetchall()
            data = [dict(row) for row in results]
        else:
            conn.commit()
            results = cur.fetchall()
            data = [dict(row) for row in results] if results else []

        cur.close()
        conn.close()

        return {"data": data, "error": None}

    except ImportError:
        return {"data": [], "error": "psycopg2 not available"}
    except Exception as e:
        return {"data": [], "error": str(e)}


class DirectSupabaseClient:
    """
    Simplified Supabase client that mimics the supabase-py API
    but uses direct SQL queries instead
    """

    def __init__(self):
        self.url = os.getenv("VITE_SUPABASE_URL")
        self.key = os.getenv("VITE_SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")
        self.connected = bool(self.url and self.key)

    def table(self, table_name: str):
        """Get table query builder"""
        return TableQuery(table_name, self)

    async def execute_sql(self, query: str) -> Dict[str, Any]:
        """Execute raw SQL"""
        return execute_sql_direct(query)


class TableQuery:
    """Query builder for table operations"""

    def __init__(self, table_name: str, client: DirectSupabaseClient):
        self.table_name = table_name
        self.client = client
        self._select = "*"
        self._filters = []
        self._limit = None
        self._order = None
        self._single = False

    def select(self, columns: str = "*"):
        """Select columns"""
        self._select = columns
        return self

    def eq(self, column: str, value: Any):
        """Add equality filter"""
        self._filters.append((column, "=", value))
        return self

    def limit(self, count: int):
        """Limit results"""
        self._limit = count
        return self

    def order(self, column: str, desc: bool = False):
        """Order results"""
        direction = "DESC" if desc else "ASC"
        self._order = f"{column} {direction}"
        return self

    def maybeSingle(self):
        """Expect single result or None"""
        self._single = True
        self._limit = 1
        return self

    def insert(self, data: Dict[str, Any]):
        """Insert data"""
        return InsertQuery(self.table_name, data, self.client)

    def update(self, data: Dict[str, Any]):
        """Update data"""
        return UpdateQuery(self.table_name, data, self.client, self._filters)

    def delete(self):
        """Delete data"""
        return DeleteQuery(self.table_name, self.client, self._filters)

    async def execute(self):
        """Execute SELECT query"""
        # Build WHERE clause
        where_parts = []
        for col, op, val in self._filters:
            if val is None:
                where_parts.append(f"{col} IS NULL")
            elif isinstance(val, str):
                escaped = val.replace("'", "''")
                where_parts.append(f"{col} {op} '{escaped}'")
            else:
                where_parts.append(f"{col} {op} {val}")

        where_clause = " AND ".join(where_parts) if where_parts else ""

        # Build query
        query = f"SELECT {self._select} FROM {self.table_name}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if self._order:
            query += f" ORDER BY {self._order}"

        if self._limit:
            query += f" LIMIT {self._limit}"

        # Execute
        result = await self.client.execute_sql(query)

        # Format response
        if self._single:
            data = result["data"][0] if result["data"] else None
        else:
            data = result["data"]

        return QueryResponse(data, result.get("error"))


class InsertQuery:
    """Insert query builder"""

    def __init__(self, table_name: str, data: Dict[str, Any], client: DirectSupabaseClient):
        self.table_name = table_name
        self.data = data
        self.client = client

    async def execute(self):
        """Execute INSERT"""
        columns = []
        values = []

        for key, val in self.data.items():
            columns.append(key)

            if val is None:
                values.append("NULL")
            elif isinstance(val, (dict, list)):
                json_str = json.dumps(val).replace("'", "''")
                values.append(f"'{json_str}'::jsonb")
            elif isinstance(val, str):
                escaped = val.replace("'", "''")
                values.append(f"'{escaped}'")
            elif isinstance(val, bool):
                values.append("TRUE" if val else "FALSE")
            else:
                values.append(str(val))

        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(values)})
            RETURNING *
        """

        result = await self.client.execute_sql(query)
        return QueryResponse(result["data"], result.get("error"))


class UpdateQuery:
    """Update query builder"""

    def __init__(self, table_name: str, data: Dict[str, Any], client: DirectSupabaseClient, filters: List):
        self.table_name = table_name
        self.data = data
        self.client = client
        self.filters = filters

    def eq(self, column: str, value: Any):
        """Add filter"""
        self.filters.append((column, "=", value))
        return self

    async def execute(self):
        """Execute UPDATE"""
        set_parts = []

        for key, val in self.data.items():
            if val is None:
                set_parts.append(f"{key} = NULL")
            elif isinstance(val, (dict, list)):
                json_str = json.dumps(val).replace("'", "''")
                set_parts.append(f"{key} = '{json_str}'::jsonb")
            elif isinstance(val, str):
                escaped = val.replace("'", "''")
                set_parts.append(f"{key} = '{escaped}'")
            elif isinstance(val, bool):
                set_parts.append(f"{key} = {'TRUE' if val else 'FALSE'}")
            else:
                set_parts.append(f"{key} = {val}")

        where_parts = []
        for col, op, val in self.filters:
            if isinstance(val, str):
                escaped = val.replace("'", "''")
                where_parts.append(f"{col} {op} '{escaped}'")
            else:
                where_parts.append(f"{col} {op} {val}")

        where_clause = " AND ".join(where_parts) if where_parts else "1=1"

        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_parts)}
            WHERE {where_clause}
            RETURNING *
        """

        result = await self.client.execute_sql(query)
        return QueryResponse(result["data"], result.get("error"))


class DeleteQuery:
    """Delete query builder"""

    def __init__(self, table_name: str, client: DirectSupabaseClient, filters: List):
        self.table_name = table_name
        self.client = client
        self.filters = filters

    def eq(self, column: str, value: Any):
        """Add filter"""
        self.filters.append((column, "=", value))
        return self

    async def execute(self):
        """Execute DELETE"""
        where_parts = []
        for col, op, val in self.filters:
            if isinstance(val, str):
                escaped = val.replace("'", "''")
                where_parts.append(f"{col} {op} '{escaped}'")
            else:
                where_parts.append(f"{col} {op} {val}")

        where_clause = " AND ".join(where_parts) if where_parts else "1=1"

        query = f"""
            DELETE FROM {self.table_name}
            WHERE {where_clause}
            RETURNING *
        """

        result = await self.client.execute_sql(query)
        return QueryResponse(result["data"], result.get("error"))


class QueryResponse:
    """Response object"""

    def __init__(self, data: Any, error: Any = None):
        self.data = data
        self.error = error

    def __bool__(self):
        return self.error is None


# Create singleton
supabase = DirectSupabaseClient()

# For backwards compatibility
Client = DirectSupabaseClient


def create_client(url: str, key: str):
    """Create Supabase client"""
    client = DirectSupabaseClient()
    client.url = url
    client.key = key
    client.connected = True
    return client
