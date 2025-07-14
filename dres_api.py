import requests

BASE_URL = "https://vbs.videobrowsing.org"
LOGIN_URL = f"{BASE_URL}/api/v2/login"
EVAL_LIST_URL = f"{BASE_URL}/api/v2/client/evaluation/list"
SUBMIT_URL = f"{BASE_URL}/api/v2/submit/{{evaluationId}}"

class DresClient:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.username = username
        self.password = password
        self.evaluation_id = None

    def login(self):
        credentials = {"username": self.username, "password": self.password}
        response = self.session.post(LOGIN_URL, json=credentials, headers=self.headers)
        if response.status_code != 200:
            return False, f"Login failed: {response.status_code} {response.text}"
        # Get evaluation id
        evals = self.session.get(EVAL_LIST_URL, headers=self.headers).json()
        if not evals:
            return False, "No evaluations found."
        self.evaluation_id = evals[0]['id']
        return True, "Logged in and evaluation loaded."

    def submit(self, media_item_name, collection_name, start, end):
        if not self.evaluation_id:
            return False, "Not logged in or evaluation not set."
        submission = {
            "answerSets": [
                {
                    "answers": [
                        {
                            "mediaItemName": media_item_name,
                            "mediaItemCollectionName": collection_name,
                            "start": start,
                            "end": end
                        }
                    ]
                }
            ]
        }
        submit_url = SUBMIT_URL.format(evaluationId=self.evaluation_id)
        submit_response = self.session.post(submit_url, json=submission, headers=self.headers)
        if submit_response.status_code == 200:
            return True, "Submission successful!"
        else:
            return False, f"Submission failed: {submit_response.status_code} {submit_response.text}"