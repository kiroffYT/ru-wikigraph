from huggingface_hub import HfApi
import os

def upload_to_hf(folder_path, repo_id, token):
    api = HfApi()
    # upload_folder автоматически сравнивает файлы и загружает только дельту
    api.upload_folder(
        folder_path=folder_path,
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
        commit_message=f"Auto-update wiki data: {os.path.basename(folder_path)}"
    )
