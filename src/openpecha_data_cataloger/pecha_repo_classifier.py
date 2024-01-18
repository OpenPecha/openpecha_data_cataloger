from dataclasses import dataclass

import requests


@dataclass
class PechaRepoClassifier:
    token: str
    organization: str = "OpenPecha-Data"

    def __init__(self, token: str):
        self.token = token

    def get_pechas_labels(self, pecha_ids: list):
        """Classify the pechas based on their repository contents."""
        pechas_labels = {}
        num_of_pechas = len(pecha_ids)
        for num, pecha_id in enumerate(pecha_ids):
            print(f"[{num+1}/{num_of_pechas}] Classifying pecha: {pecha_id} ")
            pechas_labels[pecha_id] = self.get_pecha_label(pecha_id)
        return pechas_labels

    def get_pecha_label(self, pecha_id: str):
        """Classify the pecha based on its repository content."""
        headers = {"Authorization": f"token {self.token}"}
        repo_url = (
            f"https://api.github.com/repos/{self.organization}/{pecha_id}/contents"
        )
        response = requests.get(repo_url, headers=headers)
        if response.status_code != 200:
            return "Error: Unable to access repository"

        repo_contents = response.json()
        if any(item["name"].endswith(".opf") for item in repo_contents):
            return "OPF"
        elif any(item["name"].endswith(".opa") for item in repo_contents):
            return "OPA"
        elif any(item["name"].endswith(".opc") for item in repo_contents):
            return "OPC"
        else:
            return "Other"


pecha_clr = PechaRepoClassifier(token="github_token")
print(
    pecha_clr.get_pechas_labels(
        ["P000216", "AB3CAED2A", "45c913cafa4b48ad9db66456bd5477e1"]
    )
)
