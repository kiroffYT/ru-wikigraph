from huggingface_hub import HfApi
import os

def upload_to_hf(folder_path, repo_id, token):
    api = HfApi()
    # upload_folder сам проверит хэши и загрузит только измененное
    api.upload_folder(
        folder_path=folder_path,
        repo_id=repo_id,
        repo_type="dataset",
        token=token,
        commit_message=f"Auto-update: {os.path.basename(folder_path)}"
    )
