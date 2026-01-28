"""向量库重建脚本：清空向量库，将 SQLite 的 keyword 重新向量化"""
import shutil
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import chromadb
from chromadb.config import Settings

from config import CHROMADB_PATH, COLLECTION_NAME, SQLITE_DB_PATH
from embedding_client import ZhipuAIEmbedding
from knowledge_db import KnowledgeDB


def rebuild_vector_db(batch_size: int = 10) -> int:
    """清空向量库并重新导入 SQLite 全部 keyword（索引层）"""
    if not SQLITE_DB_PATH.exists():
        print("[WARN] SQLite 数据库不存在")
        return 0

    knowledge_db = KnowledgeDB()
    total = knowledge_db.count()
    if total == 0:
        print("[WARN] SQLite 数据库为空")
        return 0

    print(f"[INFO] SQLite 中共有 {total} 条数据")

    # 清空向量库
    if CHROMADB_PATH.exists():
        shutil.rmtree(CHROMADB_PATH)
        print(f"[INFO] 已清空向量库")

    # 创建新向量库
    CHROMADB_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(CHROMADB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
    embedding_function = ZhipuAIEmbedding()
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "知识库索引"},
    )
    print(f"[OK] 创建新集合: {COLLECTION_NAME}")

    # 获取全部数据
    with knowledge_db._get_conn() as conn:
        cursor = conn.execute("SELECT id, keyword, content FROM web_knowledge ORDER BY id")
        all_data = [dict(row) for row in cursor.fetchall()]

    # 批量插入（keyword + content）
    synced_ids = []
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i : i + batch_size]
        collection.add(
            ids=[f"idx_{item['id']}" for item in batch],
            documents=[f"{item['keyword']}: {item['content']}" for item in batch],
            metadatas=[{"sqlite_id": item["id"], "keyword": item["keyword"]} for item in batch],
        )
        synced_ids.extend(item["id"] for item in batch)
        print(f"[INFO] 进度: {min(i + batch_size, len(all_data))}/{len(all_data)}")

    # 标记全部为已同步
    knowledge_db.mark_synced(synced_ids)

    print(f"[OK] 重建完成！共 {len(synced_ids)} 条索引")
    return len(synced_ids)


if __name__ == "__main__":
    print("=" * 50)
    print("[START] 重建向量索引")
    print("=" * 50)
    count = rebuild_vector_db()
    print("=" * 50)
    print(f"[DONE] 完成，共 {count} 条")
    print("=" * 50)
