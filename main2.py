from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from playwright.sync_api import sync_playwright

# ─── เตรียม Playwright ────────────────────────────────────────────────────
play = sync_playwright().start()
browser = play.chromium.launch(headless=True)
page = browser.new_page()

def navigate_to(url: str) -> str:
    page.goto(url)
    return f"Navigated to {url}"

def click_element(selector: str) -> str:
    page.click(selector)
    return f"Clicked element {selector}"

tools = [
    Tool(name="navigate_to", func=navigate_to, description="Navigate to the given URL"),
    Tool(name="click_element", func=click_element, description="Click a page element by CSS selector"),
]

# ─── สร้าง LLM + Agent ────────────────────────────────────────────────────
llm = Ollama(
    model="your-model-name",           # เปลี่ยนเป็นชื่อโมเดลของคุณ
    base_url="http://localhost:11434",
    verbose=False,
)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
)

# ─── สร้าง FastAPI App ───────────────────────────────────────────────────
app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run-agent")
async def run_agent(req: PromptRequest):
    try:
        result = agent.run(req.prompt)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── รันด้วย Uvicorn ─────────────────────────────────────────────────────
# ใช้คำสั่งด้านล่างจากเทอร์มินัลเพื่อติดตั้งเซิร์ฟเวอร์
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
