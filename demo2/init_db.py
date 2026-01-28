"""知识库初始化脚本：将 JSON 数据向量化并存入 Chromadb"""
import io
import json
import shutil
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from config import CHROMADB_PATH, COLLECTION_NAME
from embedding_client import ZhipuAIEmbedding


def load_knowledge_data() -> list:
    """加载所有知识库数据"""
    data_dir = Path(__file__).parent / "data"
    all_data = []

    for json_file in sorted(data_dir.glob("knowledge_base_part*.json")):
        print(f"[INFO] 加载文件: {json_file.name}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_data.extend(data)

    print(f"[OK] 总共加载 {len(all_data)} 条知识")
    return all_data


def init_chromadb():
    """初始化 Chromadb 并插入数据"""
    if CHROMADB_PATH.exists():
        shutil.rmtree(CHROMADB_PATH)

    client = chromadb.PersistentClient(
        path=str(CHROMADB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )

    embedding_function = ZhipuAIEmbedding()

    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"[INFO] 删除旧集合: {COLLECTION_NAME}")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "通用知识库"},
    )
    print(f"[OK] 创建新集合: {COLLECTION_NAME}")

    knowledge_data = load_knowledge_data()

    ids = []
    documents = []
    metadatas = []

    for item in knowledge_data:
        ids.append(item["id"])
        doc_text = f"关键词: {item['keyword']}\n类别: {item['category']}\n内容: {item['content']}"
        documents.append(doc_text)
        metadatas.append({
            "keyword": item["keyword"],
            "category": item["category"],
            "tags": ",".join(item["tags"]),
        })

    batch_size = 10
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i : i + batch_size]
        batch_docs = documents[i : i + batch_size]
        batch_metas = metadatas[i : i + batch_size]

        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_metas,
        )
        print(f"[INFO] 插入进度: {min(i + batch_size, len(ids))}/{len(ids)}")

    print(f"[OK] 知识库初始化完成！共 {len(ids)} 条数据")

    count = collection.count()
    print(f"[INFO] 验证: 集合中共有 {count} 条数据")

    return collection


def test_query(collection) -> None:
    """测试查询功能"""
    print("\n" + "=" * 50)
    print("[TEST] 测试查询功能")
    print("=" * 50)

    test_keywords = ["AI大模型", "区块链", "云计算"]

    for keyword in test_keywords:
        print(f"\n[QUERY] 查询关键词: {keyword}")
        results = collection.query(
            query_texts=[keyword],
            n_results=3,
        )

        print(f"[RESULT] 找到 {len(results['ids'][0])} 条相关结果:")
        for i, (doc_id, doc, metadata, distance) in enumerate(
            zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ),
            1,
        ):
            print(f"\n  [{i}] ID: {doc_id}")
            print(f"      关键词: {metadata['keyword']}")
            print(f"      类别: {metadata['category']}")
            print(f"      相似度: {1 - distance:.4f}")
            print(f"      内容预览: {doc[:100]}...")


if __name__ == "__main__":
    print("[START] 开始初始化知识库...")
    print("=" * 50)

    db_collection = init_chromadb()

    # test_query(db_collection)

    print("\n" + "=" * 50)
    print("[DONE] 知识库初始化完成！")
    print("[INFO] 可以运行 python main.py 开始使用")
    print("=" * 50)
