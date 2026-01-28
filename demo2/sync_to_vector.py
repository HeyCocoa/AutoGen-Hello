"""同步脚本：将 SQLite 中的 keyword 向量化存入 Chromadb（索引层）"""
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import chromadb
from chromadb.config import Settings

from config import CHROMADB_PATH, COLLECTION_NAME
from embedding_client import ZhipuAIEmbedding
from knowledge_db import KnowledgeDB


def sync_to_vector(batch_size: int = 10) -> int:
    """将 SQLite 的 keyword 向量化存入 Chromadb（只存索引，不存内容）"""
    knowledge_db = KnowledgeDB()
    unsynced = knowledge_db.get_unsynced(limit=100)

    if not unsynced:
        return 0

    print(f"[INFO] 发现 {len(unsynced)} 条未同步数据")

    # 确保目录存在
    CHROMADB_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMADB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
    embedding_function = ZhipuAIEmbedding()

    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_function)
    except Exception:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function,
            metadata={"description": "知识库索引"},
        )
        print(f"[INFO] 创建新集合: {COLLECTION_NAME}")

    synced_ids = []
    for i in range(0, len(unsynced), batch_size):
        batch = unsynced[i : i + batch_size]

        # keyword + content 一起向量化
        collection.add(
            ids=[f"idx_{item['id']}" for item in batch],
            documents=[f"{item['keyword']}: {item['content']}" for item in batch],
            metadatas=[{"sqlite_id": item["id"], "keyword": item["keyword"]} for item in batch],
        )

        synced_ids.extend(item["id"] for item in batch)
        print(f"[INFO] 同步进度: {min(i + batch_size, len(unsynced))}/{len(unsynced)}")

    knowledge_db.mark_synced(synced_ids)
    print(f"[OK] 同步完成，共 {len(synced_ids)} 条")
    return len(synced_ids)


if __name__ == "__main__":
    print("=" * 50)
    print("[START] 同步 SQLite keyword -> Chromadb 索引")
    print("=" * 50)
    count = sync_to_vector()
    print("=" * 50)
    print(f"[DONE] 同步完成，共 {count} 条")
    print("=" * 50)
