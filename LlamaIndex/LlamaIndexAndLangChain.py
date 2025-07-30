import importlib
from tree_sitter import Language, Parser
import os
import json
from llama_index.core.readers.file.base import SimpleDirectoryReader
from llama_index.core.node_parser import CodeSplitter

# ─── dynamic loader ─────────────────────────────────────────────────────────
# _LANGUAGE_PACKAGES = {
#     "python":     "tree_sitter_python",
#     "java":       "tree_sitter_java",
#     "javascript": "tree_sitter_javascript",
# }

# def make_ts_parser(lang_name: str) -> Parser:
#     pkg = _LANGUAGE_PACKAGES.get(lang_name.lower())
#     if pkg is None:
#         raise ValueError(f"Unsupported language: {lang_name}")
#     ts_mod = importlib.import_module(pkg)     # e.g. tree_sitter_java
#     lang   = Language(ts_mod.language())      # one‑arg blob
#     return Parser(lang)                       # pass lang in constructor

# ─── build parser & splitter ─────────────────────────────────────────────────
# lang_parser = make_ts_parser(selected_lang)


# ─── user input ──────────────────────────────────────────────────────────────
project_path  = r"C:\Users\srivarshan\Desktop\Temp\dev25-07-2025\DMAP-AI\demo-app\java-agent-services\customer-service/src/main/java"
selected_lang = "java"
OUTPUT_PATH=r"C:\Users\srivarshan\Desktop\Temp\dev25-07-2025\DMAP-AI\demo-app\microservices\ATel\output"
os.makedirs(OUTPUT_PATH,exist_ok=True)

# splitter = CodeSplitter.from_defaults(
#     language      = selected_lang,
#     chunk_lines   = 40,
#     chunk_lines_overlap   = 10,
#     parser        = lang_parser
# )

splitter = CodeSplitter(
    language      = selected_lang,include_metadata=True,include_prev_next_rel=True
    )

# ─── load & split ────────────────────────────────────────────────────────────
docs  = SimpleDirectoryReader(input_dir=project_path, recursive=True,required_exts = [".java"]).load_data()
nodes = splitter.get_nodes_from_documents(docs)
n1=nodes[1]
print(dir(n1))
total_chunks=1
for i, node in enumerate(nodes):
    # print(dir(node))
    total_chunks= total_chunks+1
    out_path = os.path.join(OUTPUT_PATH, f"chunk_{i}.json")
    # with open(out_path, "w", encoding="utf-8") as f:
        # raw Java source:
        # f.write(node.dict())
    # print(f"----------------chunk{i}----------------------")
    print(node.dict().get("metadata").get("file_name"))
    # print(node.child_by_field_name("name").text.decode())
    # print(f"----------------------------------------------")
        # — or, if you prefer JSON wrappers:
        # import json
        # print(node.dict().get("relationships"))
        # json.dump(node.dict().get("relationships"), f, indent=2)
print("-------------------------------------------------")
print(total_chunks)
print("-------------------------------------------------")
