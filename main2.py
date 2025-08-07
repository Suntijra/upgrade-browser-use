import argparse
import os
import requests
from bs4 import BeautifulSoup


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def fetch_text(url: str) -> str:
    """ดึงข้อมูลจากเว็บไซต์และคืนค่าเป็นข้อความรวม"""
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return " ".join(s.strip() for s in soup.stripped_strings)


def build_prompt(article: str, team: str) -> str:
    """สร้างพรอมต์สำหรับให้ LLM เขียนสคริปต์วิดีโอ"""
    return (
        f"วิเคราะห์ข้อมูลต่อไปนี้และเขียนสคริปต์วิดีโอภาษาไทยเกี่ยวกับทีม {team} "
        "ความยาวประมาณ 700-800 คำ ประกอบด้วย: เกริ่นนำ, ประเด็นสำคัญ, สรุปตอนท้าย.\n\n"
        f"ข้อมูลบทความ:\n{article}"
    )


def generate_with_ollama(prompt: str) -> str:
    """เรียก Ollama API เพื่อสร้างสคริปต์"""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()


def main() -> None:
    """สคริปต์บรรทัดคำสั่งสำหรับสร้างสคริปต์วิดีโอ"""
    parser = argparse.ArgumentParser(
        description="Generate a 5-minute football video script from an article URL"
    )
    parser.add_argument("url", help="URL ของบทความ")
    parser.add_argument("team", help="ชื่อทีมฟุตบอล")
    args = parser.parse_args()

    try:
        article_text = fetch_text(args.url)
        if len(article_text) > 8000:
            article_text = article_text[:8000]
        prompt = build_prompt(article_text, args.team)
        script = generate_with_ollama(prompt)
        print(script)
    except Exception as exc:
        raise SystemExit(f"เกิดข้อผิดพลาด: {exc}")


if __name__ == "__main__":
    main()

