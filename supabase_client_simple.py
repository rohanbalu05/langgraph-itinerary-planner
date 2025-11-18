"""
Simple Supabase client using in-memory storage as fallback
This provides a compatible API without requiring the supabase-py package
"""
import os
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class InMemoryStore:
    """In-memory storage as fallback when Supabase unavailable"""

    def __init__(self):
        self.tables = {
            "itineraries": [],
            "chat_sessions": [],
            "itinerary_edits": []
        }

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert record"""
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        if "created_at" not in data:
            data["created_at"] = datetime.now().isoformat()

        self.tables[table].append(data.copy())
        return data

    def select(self, table: str, filters: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Select records"""
        results = self.tables[table]

        if filters:
            results = [r for r in results if all(r.get(k) == v for k, v in filters.items())]

        if limit:
            results = results[:limit]

        return results

    def update(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update records"""
        data["updated_at"] = datetime.now().isoformat()

        updated = []
        for record in self.tables[table]:
            if all(record.get(k) == v for k, v in filters.items()):
                record.update(data)
                updated.append(record)

        return updated

    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Delete records"""
        to_delete = [r for r in self.tables[table] if all(r.get(k) == v for k, v in filters.items())]
        self.tables[table] = [r for r in self.tables[table] if r not in to_delete]
        return to_delete


# Global in-memory store
_store = InMemoryStore()


class QueryResponse:
    """Response wrapper"""

    def __init__(self, data: Any, error: Any = None):
        self.data = data
        self.error = error

    def __bool__(self):
        return self.error is None


class TableQuery:
    """Table query builder"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self._select_cols = "*"
        self._filters = {}
        self._limit = None
        self._order_by = None
        self._single = False

    def select(self, columns: str = "*"):
        """Select columns"""
        self._select_cols = columns
        return self

    def eq(self, column: str, value: Any):
        """Add equality filter"""
        self._filters[column] = value
        return self

    def limit(self, count: int):
        """Limit results"""
        self._limit = count
        return self

    def order(self, column: str, desc: bool = False):
        """Order results"""
        self._order_by = (column, desc)
        return self

    def maybeSingle(self):
        """Expect single result or None"""
        self._single = True
        self._limit = 1
        return self

    def insert(self, data: Dict[str, Any]):
        """Insert data"""
        return InsertQuery(self.table_name, data)

    def update(self, data: Dict[str, Any]):
        """Update data"""
        return UpdateQuery(self.table_name, data, self._filters)

    def delete(self):
        """Delete data"""
        return DeleteQuery(self.table_name, self._filters)

    def execute(self):
        """Execute SELECT query"""
        try:
            results = _store.select(self.table_name, self._filters, self._limit)

            if self._order_by:
                col, desc = self._order_by
                results = sorted(results, key=lambda x: x.get(col, ""), reverse=desc)

            if self._single:
                data = results[0] if results else None
            else:
                data = results

            return QueryResponse(data, None)

        except Exception as e:
            return QueryResponse(None, str(e))


class InsertQuery:
    """Insert query builder"""

    def __init__(self, table_name: str, data: Dict[str, Any]):
        self.table_name = table_name
        self.data = data

    def execute(self):
        """Execute INSERT"""
        try:
            result = _store.insert(self.table_name, self.data)
            return QueryResponse([result], None)
        except Exception as e:
            return QueryResponse(None, str(e))


class UpdateQuery:
    """Update query builder"""

    def __init__(self, table_name: str, data: Dict[str, Any], filters: Dict[str, Any]):
        self.table_name = table_name
        self.data = data
        self.filters = filters

    def eq(self, column: str, value: Any):
        """Add filter"""
        self.filters[column] = value
        return self

    def execute(self):
        """Execute UPDATE"""
        try:
            results = _store.update(self.table_name, self.filters, self.data)
            return QueryResponse(results, None)
        except Exception as e:
            return QueryResponse(None, str(e))


class DeleteQuery:
    """Delete query builder"""

    def __init__(self, table_name: str, filters: Dict[str, Any]):
        self.table_name = table_name
        self.filters = filters

    def eq(self, column: str, value: Any):
        """Add filter"""
        self.filters[column] = value
        return self

    def execute(self):
        """Execute DELETE"""
        try:
            results = _store.delete(self.table_name, self.filters)
            return QueryResponse(results, None)
        except Exception as e:
            return QueryResponse(None, str(e))


class SimpleSupabaseClient:
    """Simple Supabase-compatible client"""

    def __init__(self):
        self.url = os.getenv("VITE_SUPABASE_URL")
        self.key = os.getenv("VITE_SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")
        print("✅ Simple Supabase client initialized (using in-memory storage)")

    def table(self, table_name: str):
        """Get table query builder"""
        return TableQuery(table_name)


# Singleton instance
supabase = SimpleSupabaseClient()


# For compatibility
class Client:
    pass


def create_client(url: str, key: str):
    """Create client"""
    return SimpleSupabaseClient()
