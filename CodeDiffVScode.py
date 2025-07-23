import difflib

def generate_diff_file(original_file, modified_file, output_file="diff_output.diff"):
    # Read both files
    with open(original_file, 'r', encoding='utf-8') as f1, open(modified_file, 'r', encoding='utf-8') as f2:
        original_lines = f1.readlines()
        modified_lines = f2.readlines()

    # Generate the unified diff
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=original_file,
        tofile=modified_file,
        lineterm=''  # Avoid double newlines
    )

    # Write to output .diff file
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in diff:
            f.write(line + '\n')

    print(f"✅ Diff written to: {output_file}")
import subprocess

# def launch_vscode_diff(file1, file2):
#     command = f'code --diff "{file1}" "{file2}"'
#     try:
#         subprocess.run(["powershell", "-Command", command], check=True)
#         print("VS Code diff launched via PowerShell.")
#     except Exception as e:
#         print(f"Error: {e}")

if __name__ == "__main__":
    generate_diff_file("C:\\Users\\srivarshan\\Desktop\\OpenAIBatchAPI\\StreamingAndRag\\whitepaper.txt","C:\\DMAP_AI_NEW\\DMAP-AI\\kafka-openai-dmap\\testFiles\\customer-service\\src\\main\\java\\com\\example\\customerservice\\service\\TransactionServiceImpl.java")
    # launch_vscode_diff("C:\\Users\\srivarshan\\Desktop\\OpenAIBatchAPI\\StreamingAndRag\\whitepaper.txt","C:\\DMAP_AI_NEW\\DMAP-AI\\kafka-openai-dmap\\testFiles\\customer-service\\src\\main\\java\\com\\example\\customerservice\\service\\TransactionServiceImpl.java")
