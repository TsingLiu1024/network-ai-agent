import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from config.settings import Settings
from rag.retriever import Retriever


class KeywordEmbedding:
    """Deterministic fixture, not a substitute for live embedding evaluation."""

    @staticmethod
    def vector(text):
        terms = [("DNS", "解析"), ("代理", "proxy"), ("WSL", "子系统")]
        vector = [float(any(word.lower() in text.lower() for word in group)) for group in terms]
        return vector + [float(not any(vector))]

    def embed_documents(self, texts):
        return [self.vector(t) for t in texts]

    def embed_query(self, text):
        return self.vector(text)


@pytest.fixture
def corpus(tmp_path):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    for name, text in [
        ("dns", "DNS 域名解析失败时先用 nslookup 查看返回地址。"),
        ("proxy", "代理 proxy 故障检查代理地址和端口。"),
        ("wsl", "WSL 子系统网络异常检查 resolv.conf。"),
    ]:
        (knowledge / f"{name}.md").write_text(text, encoding="utf-8")
    config = Settings(
        _env_file=None,
        KNOWLEDGE_PATH=knowledge,
        VECTOR_DB_PATH=tmp_path / "db",
        EMBEDDING_MODEL="fixture",
        RAG_MIN_SCORE=0.4,
    )
    return config


def test_empty_volume_builds_and_returns_source_and_score(corpus):
    corpus.VECTOR_DB_PATH.mkdir()
    retriever = Retriever(corpus, embedding=KeywordEmbedding())
    retriever.prepare()
    hits = retriever.search("域名解析失败")
    assert hits[0]["source"] == "dns.md"
    assert hits[0]["score"] == pytest.approx(1.0)
    assert "nslookup" in hits[0]["text"]
    assert retriever.search("打印机卡纸") == []


def test_corrupt_snapshot_is_rebuilt(corpus):
    retriever = Retriever(corpus, embedding=KeywordEmbedding())
    retriever.prepare()
    current = (corpus.VECTOR_DB_PATH / "CURRENT").read_text().strip()
    (corpus.VECTOR_DB_PATH / current).write_text("corrupt", encoding="utf-8")
    recovered = Retriever(corpus, embedding=KeywordEmbedding())
    recovered.prepare()
    assert recovered.search("DNS")[0]["source"] == "dns.md"


def test_changed_knowledge_rebuilds_on_prepare(corpus):
    retriever = Retriever(corpus, embedding=KeywordEmbedding())
    retriever.prepare()
    (corpus.KNOWLEDGE_PATH / "dns.md").write_text("DNS 新增证据：检查本地缓存。", encoding="utf-8")
    retriever.prepare()
    assert "新增证据" in retriever.search("DNS")[0]["text"]


def test_concurrent_builds_publish_complete_snapshot(corpus):
    def build(_):
        item = Retriever(corpus, embedding=KeywordEmbedding())
        item.prepare()
        return item.search("代理")[0]["source"]

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(build, range(4))) == ["proxy.md"] * 4
    pointer = (corpus.VECTOR_DB_PATH / "CURRENT").read_text().strip()
    data = json.loads((corpus.VECTOR_DB_PATH / pointer).read_text(encoding="utf-8"))
    assert len(data["documents"]) == len(data["vectors"]) == 3


def test_old_pickle_index_is_ignored(corpus):
    corpus.VECTOR_DB_PATH.mkdir()
    (corpus.VECTOR_DB_PATH / "index.pkl").write_bytes(b"untrusted legacy data")
    retriever = Retriever(corpus, embedding=KeywordEmbedding())
    retriever.prepare()
    assert retriever.search("WSL")[0]["source"] == "wsl.md"


def test_empty_knowledge_fails_without_fabricated_default(corpus):
    for path in corpus.KNOWLEDGE_PATH.iterdir():
        path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="knowledge"):
        Retriever(corpus, embedding=KeywordEmbedding()).prepare()


def test_oversized_knowledge_is_rejected(corpus):
    corpus.RAG_MAX_FILE_BYTES = 1
    with pytest.raises(ValueError, match="limit"):
        Retriever(corpus, embedding=KeywordEmbedding()).prepare()


def test_search_requires_preparation_and_never_downloads_model(corpus):
    retriever = Retriever(corpus, embedding=KeywordEmbedding())
    with pytest.raises(RuntimeError, match="prepared"):
        retriever.search("DNS")


@pytest.mark.parametrize("payload", [[], None, {"fingerprint": "wrong"}])
def test_malformed_json_snapshot_recovers_without_startup_failure(corpus, payload):
    import hashlib

    retriever = Retriever(corpus, embedding=KeywordEmbedding())
    retriever.prepare()
    raw = json.dumps(payload).encode()
    generation = hashlib.sha256(raw).hexdigest() + ".json"
    (corpus.VECTOR_DB_PATH / generation).write_bytes(raw)
    (corpus.VECTOR_DB_PATH / "CURRENT").write_text(generation)
    recovered = Retriever(corpus, embedding=KeywordEmbedding()).prepare()
    assert recovered.search("DNS")[0]["source"] == "dns.md"


def test_reusing_snapshot_does_not_reembed_corpus(corpus):
    Retriever(corpus, embedding=KeywordEmbedding()).prepare()

    class Cached(KeywordEmbedding):
        def embed_documents(self, texts):
            raise AssertionError("Unchanged corpus was embedded again")

    recovered = Retriever(corpus, embedding=Cached()).prepare()
    assert recovered.search("DNS")[0]["source"] == "dns.md"


@pytest.mark.parametrize("value", [10**1000, "not numeric", None])
def test_invalid_vector_scalar_recovers_from_snapshot(corpus, value):
    import hashlib

    Retriever(corpus, embedding=KeywordEmbedding()).prepare()
    pointer = (corpus.VECTOR_DB_PATH / "CURRENT").read_text().strip()
    data = json.loads((corpus.VECTOR_DB_PATH / pointer).read_text(encoding="utf-8"))
    data["vectors"][0][0] = value
    raw = json.dumps(data).encode()
    generation = hashlib.sha256(raw).hexdigest() + ".json"
    (corpus.VECTOR_DB_PATH / generation).write_bytes(raw)
    (corpus.VECTOR_DB_PATH / "CURRENT").write_text(generation)
    recovered = Retriever(corpus, embedding=KeywordEmbedding()).prepare()
    assert recovered.search("DNS")[0]["source"] == "dns.md"


def test_nested_json_corruption_is_rebuilt(corpus):
    import hashlib

    corpus.VECTOR_DB_PATH.mkdir()
    raw = b"[" * 2000 + b"]" * 2000
    generation = hashlib.sha256(raw).hexdigest() + ".json"
    (corpus.VECTOR_DB_PATH / generation).write_bytes(raw)
    (corpus.VECTOR_DB_PATH / "CURRENT").write_text(generation)
    assert Retriever(corpus, embedding=KeywordEmbedding()).prepare().search("DNS")


def test_source_bearing_retrieval_reaches_diagnosis_prompt(corpus):
    from agents.core.manager import AgentManager

    class Model:
        prompts = []

        def chat(self, prompt, timeout=None):
            self.prompts.append(prompt)
            if "REPAIR_PLAN" in prompt:
                return json.dumps(
                    {"reason": "Need evidence", "steps": ["Check DNS"], "commands": []}
                )
            return "Evidence from dns.md; measurements still required"

    model = Model()
    corpus.COLLECT_LOCAL_EVIDENCE = False
    manager = AgentManager(
        corpus, llm=model, retriever=Retriever(corpus, embedding=KeywordEmbedding())
    )
    manager.prepare()
    result = manager.run("DNS 解析失败")
    assert result["stages"]["rag"]["data"]["documents"][0]["source"] == "dns.md"
    assert all("dns.md" in prompt and "nslookup" in prompt for prompt in model.prompts)


def test_optional_rag_failure_is_visible_in_readiness_and_diagnosis(corpus):
    from fastapi.testclient import TestClient

    from agents.core.manager import AgentManager
    from app import create_app

    class Broken:
        def prepare(self):
            raise RuntimeError("private model path")

    corpus.MODEL_PROVIDER = "demo"
    manager = AgentManager(corpus, retriever=Broken())
    with TestClient(create_app(corpus, manager)) as client:
        assert client.get("/ready").json()["rag"] == "degraded"
        response = client.post("/api/v1/diagnose", json={"question": "DNS"})
        assert response.json()["result"]["stages"]["rag"]["success"] is False
        assert "private model path" not in response.text
