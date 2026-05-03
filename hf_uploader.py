from huggingface_hub import HfApi
import os

def upload_to_hf(folder_path, repo_id, token):
    api = HfApi()
    print("Начинаем загрузку в Hugging Face...")
    api.upload_folder(
        folder_path=folder_path,
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
        commit_message=f"Update dump {os.path.basename(folder_path)}"
    )
