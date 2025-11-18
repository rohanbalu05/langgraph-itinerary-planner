"""
Supabase MCP Client - Uses direct SQL queries via MCP tools
This avoids the import conflict with the local /supabase folder
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SupabaseMCPClient:
    """Wrapper for Supabase operations using direct SQL"""

    def __init__(self):
        self.url = os.getenv("VITE_SUPABASE_URL")
        self.key = os.getenv("VITE_SUPABASE_ANON_KEY")

        if not self.key:
            self.key = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")

        self.connected = bool(self.url and self.key)

        if self.connected:
            print("✅ Supabase MCP Client initialized")
        else:
            print("⚠️  Supabase credentials not found")

    def execute_sql(self, query: str) -> Dict[str, Any]:
        """Execute raw SQL query"""
        # This would use mcp__supabase__execute_sql in actual implementation
        # For now, we'll return a mock structure
        return {"data": [], "error": None}

    def table(self, table_name: str):
        """Return a table query builder"""
        return TableQueryBuilder(table_name, self)


class TableQueryBuilder:
    """Fluent interface for building table queries"""

    def __init__(self, table_name: str, client: SupabaseMCPClient):
        self.table_name = table_name
        self.client = client
        self._select_cols = "*"
        self._filters = []
        self._limit_val = None
        self._order_col = None
        self._order_desc = False

    def select(self, columns: str = "*"):
        """Select columns"""
        self._select_cols = columns
        return self

    def eq(self, column: str, value: Any):
        """Add equality filter"""
        if isinstance(value, str):
            self._filters.append(f"{column} = '{value}'")
        else:
            self._filters.append(f"{column} = {value}")
        return self

    def limit(self, count: int):
        """Limit results"""
        self._limit_val = count
        return self

    def order(self, column: str, desc: bool = False):
        """Order results"""
        self._order_col = column
        self._order_desc = desc
        return self

    def maybeSingle(self):
        """Return single result or None"""
        self._limit_val = 1
        return self

    def insert(self, data: Dict[str, Any]):
        """Insert data"""
        return InsertBuilder(self.table_name, data, self.client)

    def update(self, data: Dict[str, Any]):
        """Update data"""
        return UpdateBuilder(self.table_name, data, self.client, self._filters)

    def delete(self):
        """Delete data"""
        return DeleteBuilder(self.table_name, self.client, self._filters)

    def execute(self):
        """Execute the query"""
        # Build SQL query
        where_clause = " AND ".join(self._filters) if self._filters else ""

        query = f"SELECT {self._select_cols} FROM {self.table_name}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if self._order_col:
            direction = "DESC" if self._order_desc else "ASC"
            query += f" ORDER BY {self._order_col} {direction}"

        if self._limit_val:
            query += f" LIMIT {self._limit_val}"

        # Execute via SQL
        # In production, this would call mcp__supabase__execute_sql
        # For now, return mock data structure

        result = self.client.execute_sql(query)

        # Return response object
        return QueryResponse(result.get("data", []), result.get("error"))


class InsertBuilder:
    """Builder for INSERT queries"""

    def __init__(self, table_name: str, data: Dict[str, Any], client: SupabaseMCPClient):
        self.table_name = table_name
        self.data = data
        self.client = client

    def execute(self):
        """Execute insert"""
        # Build INSERT query
        columns = list(self.data.keys())
        values = []

        for val in self.data.values():
            if val is None:
                values.append("NULL")
            elif isinstance(val, (dict, list)):
                values.append(f"'{json.dumps(val)}'::jsonb")
            elif isinstance(val, str):
                # Escape single quotes
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

        result = self.client.execute_sql(query)
        return QueryResponse(result.get("data", []), result.get("error"))


class UpdateBuilder:
    """Builder for UPDATE queries"""

    def __init__(self, table_name: str, data: Dict[str, Any], client: SupabaseMCPClient, filters: List[str]):
        self.table_name = table_name
        self.data = data
        self.client = client
        self.filters = filters

    def eq(self, column: str, value: Any):
        """Add filter"""
        if isinstance(value, str):
            self.filters.append(f"{column} = '{value}'")
        else:
            self.filters.append(f"{column} = {value}")
        return self

    def execute(self):
        """Execute update"""
        set_clauses = []

        for key, val in self.data.items():
            if val is None:
                set_clauses.append(f"{key} = NULL")
            elif isinstance(val, (dict, list)):
                set_clauses.append(f"{key} = '{json.dumps(val)}'::jsonb")
            elif isinstance(val, str):
                escaped = val.replace("'", "''")
                set_clauses.append(f"{key} = '{escaped}'")
            elif isinstance(val, bool):
                set_clauses.append(f"{key} = {'TRUE' if val else 'FALSE'}")
            else:
                set_clauses.append(f"{key} = {val}")

        where_clause = " AND ".join(self.filters) if self.filters else "1=1"

        query = f"""
        UPDATE {self.table_name}
        SET {', '.join(set_clauses)}
        WHERE {where_clause}
        RETURNING *
        """

        result = self.client.execute_sql(query)
        return QueryResponse(result.get("data", []), result.get("error"))


class DeleteBuilder:
    """Builder for DELETE queries"""

    def __init__(self, table_name: str, client: SupabaseMCPClient, filters: List[str]):
        self.table_name = table_name
        self.client = client
        self.filters = filters

    def eq(self, column: str, value: Any):
        """Add filter"""
        if isinstance(value, str):
            self.filters.append(f"{column} = '{value}'")
        else:
            self.filters.append(f"{column} = {value}")
        return self

    def execute(self):
        """Execute delete"""
        where_clause = " AND ".join(self.filters) if self.filters else "1=1"

        query = f"""
        DELETE FROM {self.table_name}
        WHERE {where_clause}
        RETURNING *
        """

        result = self.client.execute_sql(query)
        return QueryResponse(result.get("data", []), result.get("error"))


class QueryResponse:
    """Response object for queries"""

    def __init__(self, data: Any, error: Any = None):
        self.data = data
        self.error = error

    def __bool__(self):
        return self.error is None


# Create singleton instance
supabase = SupabaseMCPClient()
