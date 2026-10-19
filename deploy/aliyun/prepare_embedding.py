"""从原始模型生成低内存模型；在开发机运行，需要 onnx 和 onnxruntime。"""
from pathlib import Path
import base64
import json
import shutil

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper
from onnxruntime.quantization import QuantType, quantize_dynamic
from sentencepiece import sentencepiece_model_pb2 as sp_proto


root = Path(__file__).resolve().parents[2]
model_root = root / "backend/embedding/onnx"
source = model_root / "paraphrase-multilingual-MiniLM-L12-v2"
target = model_root / "paraphrase-multilingual-MiniLM-L12-v2-int8"
target.mkdir(exist_ok=True)

quantize_dynamic(
    str(source / "model.onnx"),
    str(target / "model.onnx"),
    per_channel=True,
    weight_type=QuantType.QInt8,
    op_types_to_quantize=["MatMul"],
)
model = onnx.load(str(target / "model.onnx"))
initializers = {value.name: value for value in model.graph.initializer}
replacements = {}
scales = {}
for node in model.graph.node:
    if node.op_type != "Gather" or node.input[0] not in initializers:
        continue
    weight = initializers[node.input[0]]
    # 仅处理所有消费者都按第 0 维索引的二维词向量表。
    consumers = [item for item in model.graph.node if weight.name in item.input]
    if weight.data_type != TensorProto.FLOAT or len(weight.dims) != 2:
        continue
    if not all(item.op_type == "Gather" and all(attr.i == 0 for attr in item.attribute if attr.name == "axis") for item in consumers):
        continue
    values = numpy_helper.to_array(weight)
    scale = np.maximum(np.abs(values).max(axis=1, keepdims=True) / 127, 1e-12).astype(np.float32)
    quantized = np.clip(np.rint(values / scale), -127, 127).astype(np.int8)
    replacements[weight.name] = numpy_helper.from_array(quantized, name=weight.name)
    scales[weight.name] = numpy_helper.from_array(scale, name=weight.name + ".row_scale")

for index, weight in enumerate(model.graph.initializer):
    if weight.name in replacements:
        model.graph.initializer[index].CopyFrom(replacements[weight.name])
model.graph.initializer.extend(scales.values())

nodes = []
for node in model.graph.node:
    if node.op_type != "Gather" or node.input[0] not in replacements:
        nodes.append(node)
        continue
    output = node.output[0]
    node.output[0] = output + "_int8"
    nodes.extend([
        node,
        helper.make_node("Gather", [node.input[0] + ".row_scale", node.input[1]], [output + "_scale"], name=node.name + "_scale", axis=0),
        helper.make_node("Cast", [output + "_int8"], [output + "_float32"], name=node.name + "_cast", to=TensorProto.FLOAT),
        helper.make_node("Mul", [output + "_float32", output + "_scale"], [output], name=node.name + "_dequantize"),
    ])
del model.graph.node[:]
model.graph.node.extend(nodes)
onnx.checker.check_model(model)
onnx.save(model, str(target / "model.onnx"))
options = ort.SessionOptions()
options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1
options.enable_cpu_mem_arena = False
options.enable_mem_pattern = False
options.optimized_model_filepath = str(target / "model.ort")
options.add_session_config_entry("session.save_model_format", "ORT")
ort.InferenceSession(str(target / "model.onnx"), options, providers=["CPUExecutionProvider"])
for name in ["tokenizer.json", "embedding_config.json"]:
    shutil.copy2(source / name, target / name)

# 使用相同的词表、分数和规范化规则，避免加载 Fast Tokenizer 的大型内存结构。
tokenizer_config = json.loads((source / "tokenizer.json").read_text())
tokenizer_model = sp_proto.ModelProto()
spec = tokenizer_model.trainer_spec
spec.model_type = sp_proto.TrainerSpec.UNIGRAM
spec.vocab_size = len(tokenizer_config["model"]["vocab"])
spec.unk_id, spec.bos_id, spec.eos_id, spec.pad_id = 3, 0, 2, 1
spec.unk_piece, spec.bos_piece, spec.eos_piece, spec.pad_piece = "<unk>", "<s>", "</s>", "<pad>"
normalizer = tokenizer_model.normalizer_spec
normalizer.name = "precompiled"
normalizer.precompiled_charsmap = base64.b64decode(tokenizer_config["normalizer"]["precompiled_charsmap"])
normalizer.add_dummy_prefix = True
normalizer.remove_extra_whitespaces = True
normalizer.escape_whitespaces = True
for index, (text, score) in enumerate(tokenizer_config["model"]["vocab"]):
    piece = tokenizer_model.pieces.add()
    piece.piece, piece.score = text, score
    if index == 3:
        piece.type = sp_proto.ModelProto.SentencePiece.UNKNOWN
    elif index in {0, 1, 2}:
        piece.type = sp_proto.ModelProto.SentencePiece.CONTROL
    elif text == "<mask>":
        piece.type = sp_proto.ModelProto.SentencePiece.USER_DEFINED
    else:
        piece.type = sp_proto.ModelProto.SentencePiece.NORMAL
(target / "tokenizer.model").write_bytes(tokenizer_model.SerializeToString())
print(f"低内存模型：{(target / 'model.onnx').stat().st_size / 1024 ** 2:.1f} MiB")
