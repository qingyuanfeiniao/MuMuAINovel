"""在开发机验证低内存模型和原分词路径，避免在小服务器加载两份模型。"""
import gc
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "backend"))
from app.services.onnx_embedding import OnnxEmbeddingModel  # noqa: E402

model_root = root / "backend/embedding/onnx"
original_dir = model_root / "paraphrase-multilingual-MiniLM-L12-v2"
compact_dir = model_root / "paraphrase-multilingual-MiniLM-L12-v2-int8"
samples = [
    "沈砚修复古籍时发现雁回关的军籍缺页。",
    "裴映秋追查被篡改的历史和消失的记忆。",
    "为了保护门派，主角必须保守师父的秘密。",
    "图书馆收藏了大量古代文献。",
    "今天去市场购买蔬菜。",
]
edge_cases = ["hello world! 123 你好　世界", "第一段\n第二段\tA  B", "  多个   空格  ", "ＡＢＣ ① ﬁ ß café", "日本語とEnglish。🙂", "", "长篇小说" * 100]
base = {"ONNX_EMBEDDING_THREADS": "1", "ONNX_EMBEDDING_LOW_MEMORY": "true"}
with patch.dict(os.environ, base):
    original = OnnxEmbeddingModel(original_dir)
    reference = original.encode(samples)
    del original
    gc.collect()
with patch.dict(os.environ, {**base, "ONNX_EMBEDDING_MODEL_FILE": "model.ort"}):
    fast_model = OnnxEmbeddingModel(compact_dir)
    fast_vectors = fast_model.encode(samples + edge_cases)
    del fast_model
    gc.collect()
with patch.dict(os.environ, {**base, "ONNX_EMBEDDING_MODEL_FILE": "model.ort", "ONNX_EMBEDDING_TOKENIZER": "sentencepiece"}):
    native_model = OnnxEmbeddingModel(compact_dir)
    native_vectors = native_model.encode(samples + edge_cases)

assert native_vectors.shape == (len(samples + edge_cases), 384)
assert np.isfinite(native_vectors).all()
assert np.allclose(fast_vectors, native_vectors, rtol=1e-5, atol=1e-5)
compact = native_vectors[:len(samples)]
cosines = (reference * compact).sum(axis=1) / (np.linalg.norm(reference, axis=1) * np.linalg.norm(compact, axis=1))
assert float(cosines.min()) > 0.98
result = {"cosine_min": float(cosines.min()), "cosine_mean": float(cosines.mean()), "tokenizer_equivalent_samples": len(samples + edge_cases), "embedding_dimension": 384}
(root / "deploy/aliyun/model-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
