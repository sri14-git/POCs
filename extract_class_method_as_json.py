import os
import re
import json

def split_camel_case(name):
    """Split camelCase and PascalCase into subtokens."""
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)

def extract_classes_and_methods(java_code):
    class_pattern = re.compile(r'\b(class|interface|enum)\s+(\w+)')
    method_pattern = re.compile(r'(?:public|protected|private|static|\s)+[\w\<\>\[\]]+\s+(\w+)\s*\([^;]*?\)\s*\{?')

    class_matches = class_pattern.findall(java_code)
    method_matches = method_pattern.findall(java_code)

    class_names = [match[1] for match in class_matches]
    method_names = [m for m in method_matches if len(m) > 2]  # Ignore short or noise names

    return class_names, method_names

def is_utility_class(class_name):
    """
    Skip any class that is purely infra or data:
     - persistence DAOs, DTOs/VOs
     - exceptions, filters
     - constants, helpers, utils
     - web‐service stubs/proxies
    """
    ignore_terms = [
        'util', 'utils', 'helper', 'base', 'common', 'abstract',
        'exception', 'filter','commons','bean','tempuri'
        'constant', 'proxy', 'stub'
    ]
    lower = class_name.lower()
    return any(term in lower for term in ignore_terms)

def scan_java_files(folder_path):
    class_methods_map = {}

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.java'):
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        java_code = f.read()

                    class_names, method_names = extract_classes_and_methods(java_code)

                    for class_name in class_names:
                        if is_utility_class(class_name):
                            continue

                        if class_name not in class_methods_map:
                            class_methods_map[class_name] = set()

                        for method in method_names:
                            tokens = split_camel_case(method)
                            class_methods_map[class_name].update(t.lower() for t in tokens if len(t) > 1)

                except Exception as e:
                    print(f"Error in {file}: {e}")

    # Convert sets to sorted lists
    return {cls: sorted(list(tokens)) for cls, tokens in class_methods_map.items()}

def chunk_json_by_classes(input_json, chunk_size=10):
    chunks = []
    items = list(input_json.items())
    
    for i in range(0, len(items), chunk_size):
        chunk_dict = dict(items[i:i + chunk_size])
        chunks.append(chunk_dict)

    return chunks


def write_to_json_file(class_methods_map, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(class_methods_map, f, indent=None, separators=(',', ': '))

def main():
    input_folder = input("Enter the path to the folder containing Java files: ").strip()
    output_file = "C:\\DMAP_AI_NEW\\Microservice\\DMAP-AI\\demo-app\\microservices\\ATel\\token_chunks\\tokens_cleansed.json"

    result = scan_java_files(input_folder)
    write_to_json_file(result, output_file)

    print(f"JSON output written to {output_file}")

    with open("C:\\DMAP_AI_NEW\\Microservice\\DMAP-AI\\demo-app\\microservices\\ATel\\token_chunks\\tokens_cleansed.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks = chunk_json_by_classes(data, chunk_size=10)

    # Optionally write each chunk to disk
    for i, chunk in enumerate(chunks):
        with open(f"C:\\DMAP_AI_NEW\\Microservice\\DMAP-AI\\demo-app\\microservices\\ATel\\token_chunks\\tokens_chunk_{i+1}.json", "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=2)
    return True

if __name__ == "__main__":
    main()
