"""SQLite 知识库管理"""
import json
import sqlite3
from typing import Optional

from config import SQLITE_DB_PATH

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS web_knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    expanded_keywords TEXT,
    title TEXT,
    content TEXT NOT NULL,
    source_url TEXT,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_to_vector INTEGER DEFAULT 0
)
"""


class KnowledgeDB:
    """SQLite 知识库管理器"""

    def __init__(self):
        self.db_path = SQLITE_DB_PATH
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表"""
        with self._get_conn() as conn:
            conn.execute(_CREATE_TABLE_SQL)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_keyword ON web_knowledge(keyword)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_synced ON web_knowledge(synced_to_vector)")

    def save(
        self,
        keyword: str,
        content: str,
        expanded_keywords: Optional[list] = None,
        title: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> int:
        """保存搜索结果"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO web_knowledge (keyword, expanded_keywords, title, content, source_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    keyword,
                    json.dumps(expanded_keywords, ensure_ascii=False) if expanded_keywords else None,
                    title,
                    content,
                    source_url,
                ),
            )
            return cursor.lastrowid

    def get_unsynced(self, limit: int = 100) -> list:
        """获取未同步到向量库的记录"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM web_knowledge WHERE synced_to_vector = 0 ORDER BY search_time ASC LIMIT ?",
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_synced(self, ids: list):
        """标记为已同步"""
        if not ids:
            return
        with self._get_conn() as conn:
            placeholders = ",".join("?" * len(ids))
            conn.execute(
                f"UPDATE web_knowledge SET synced_to_vector = 1 WHERE id IN ({placeholders})",
                ids,
            )

    def count(self) -> int:
        """统计记录数"""
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM web_knowledge")
            return cursor.fetchone()[0]

    def get_by_id(self, record_id: int) -> Optional[dict]:
        """根据 ID 获取记录"""
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM web_knowledge WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
