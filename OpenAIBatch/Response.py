from dotenv import load_dotenv
import openai
import time
import json
import os

# Ensure your API key is set as an environment variable for secure access

# For Summary target_endpoint = "/v1/chat/completions"
# For Vectorization target_endpoint = "/v1/embeddings"
load_dotenv()
client = openai.AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-12-01-preview",  # or the version you're using
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def execute_openai_batch_job(input_file_path: str, target_endpoint: str, model_for_job: str):
    """
    Executes an OpenAI Batch API job, including file upload, job creation, status monitoring,
    and output retrieval.

    Args:
        input_file_path (str): The local file path to the JSONL input file.
        target_endpoint (str): The OpenAI API endpoint for the batch (e.g., "/v1/chat/completions").
        model_for_job (str): The specific model to be used for the batch processing
                              (e.g., "gpt-4o", "text-embedding-ada-002").
    """
    try:
        print(f"Initiating file upload for: {input_file_path}...")

        # Step 1: Upload the input file to OpenAI
        with open(input_file_path, "rb") as f:
            file_response = client.files.create(
                file=f,
                purpose="batch" # The purpose must be 'batch' for batch API files
            )
        input_file_id = file_response.id
        print(f"Input file uploaded successfully. File ID: {input_file_id}")

        print("Creating new batch job...")
        
        # Step 2: Create the batch job
        batch_job = client.batches.create(
            input_file_id=input_file_id,
            endpoint=target_endpoint,
            completion_window="24h" # Specifies the maximum time allocated for job completion
        )
        batch_id = batch_job.id
        print(f"Batch job initiated. Batch ID: {batch_id}")
        print(f"Initial status: {batch_job.status}")
        print(batch_job.model_dump_json(indent=2))

        # Step 3: Monitor the job status until completion or failure
        while batch_job.status in ["validating", "in_progress", "queued"]:
            print(f"Job {batch_id} is currently {batch_job.status}. Awaiting completion...")
            time.sleep(30) # Pause for 30 seconds before re-checking status
            batch_job = client.batches.retrieve(batch_id) # Retrieve the latest job status

        print(f"Batch job {batch_id} concluded with status: {batch_job.status}")

        if batch_job.status == "completed":
            output_file_id = batch_job.output_file_id
            error_file_id = batch_job.error_file_id

            if output_file_id:
                print(f"Downloading output file (ID: {output_file_id})...")
                output_content = client.files.content(output_file_id).content
                output_data = output_content.decode('utf-8')

                # Save the output to a local file for further processing
                output_filename = f"batch_output_{batch_id}.jsonl"
                with open(output_filename, "w") as f:
                    f.write(output_data)
                print(f"Batch output saved to {output_filename}")


    except openai.OpenAIError as e:
        print(f"An OpenAI API specific error occurred: {e}")
    except FileNotFoundError:
        print(f"Error: The specified input file was not found at {input_file_path}")
    except Exception as e:
        print(f"An unexpected system error occurred: {e}")

