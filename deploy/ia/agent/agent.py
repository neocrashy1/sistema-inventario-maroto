import os
import time
import json
import requests
from git import Repo

TGW_URL = os.environ.get('TGW_URL', 'http://localhost:7860')
AUTONOMOUS = os.environ.get('AUTONOMOUS', 'false').lower() in ('1','true','yes')
PROJECT_PATH = '/workspace/project'


def wait_for_tgw(url, timeout=120):
    start = time.time()
    health = f"{url}/api/prompt"
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def ask_tgw(prompt):
    # text-generation-webui supports a /api/prompt endpoint for programmatic prompts
    url = f"{TGW_URL}/api/prompt"
    payload = {"prompt": prompt, "max_new_tokens": 512}
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json().get('results', [{}])[0].get('text', '')
    except Exception as e:
        return f"ERROR: {e}"


def main():
    print("Agent starting. TGW at:", TGW_URL, "AUTONOMOUS=", AUTONOMOUS)
    ok = wait_for_tgw(TGW_URL, timeout=180)
    if not ok:
        print("text-generation-webui not available at", TGW_URL)
        return

    prompt = (
        "You are an offline code assistant. Inspect the repository mounted at /workspace/project and produce up to 5 concrete improvement suggestions in JSON. "
        "For each suggestion, include: path (file to change, or directory), description, and a unified diff patch (if possible) or steps to fix. "
        "Respond ONLY with valid JSON."
    )

    print("Asking TGW for suggestions...")
    response = ask_tgw(prompt)
    # Try to parse JSON from response
    suggestions = response
    try:
        # sanitize and parse
        obj = json.loads(response)
    except Exception:
        # fallback: wrap free text under 'raw'
        obj = {"raw": response}

    out_path = os.path.join(PROJECT_PATH, 'ia_suggestions.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    print("Suggestions written to", out_path)

    if AUTONOMOUS:
        try:
            repo = Repo(PROJECT_PATH)
            branch = 'ai-suggestions-1'
            repo.git.checkout('-b', branch)
            repo.index.add([out_path])
            repo.index.commit('chore: add IA suggestions report')
            print('Committed suggestions to branch', branch)
        except Exception as e:
            print('Failed to commit suggestions:', e)


if __name__ == '__main__':
    main()
