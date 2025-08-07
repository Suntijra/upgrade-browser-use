import os
from browser_use.llm import ChatOllama,ChatGoogle

from browser_use import Agent, BrowserSession
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page
import asyncio
import time

load_dotenv()

async def main():
    try:
        # ใช้ LLM ที่เสียงคง
        # llm = ChatOllama(
        #     model="qwen2.5vl:7b", 
        #     host="https://bai-ap.jts.co.th:10602",
        #     timeout=60  # เพิ่ม timeout
        # )
        
        llm= ChatGoogle(model="gemini-2.5-flash")
        
        # สร้าง agent
        agent = Agent(
            task="เข้าไปที่ dooball66n.com และหา match เพื่อเปิด video stream ให้ฉันดู ถ้ามีโฆษณาให้ข้ามไป ให้หาจนกว่าจะเจอวิดีโอที่ streaming football ถ้า",
            llm=llm,
            use_vision=True,
            max_failures=3,
            retry_delay=2,
            browser_config={
                'headless': False,
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        
        print("🚀 เริ่มต้นการทำงาน...")
        result = await agent.run(max_steps=30)
        print(f"✅ เสร็จสิ้น: {result.final_result}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        print("กำลังลองใหม่...")
        
        # ลองอีกครั้งโดยไม่ใช้ vision
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                        headless=False, channel="chrome-beta",
                        args=[
                            '--start-fullscreen',
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--autoplay-policy=no-user-gesture-required',
                            '--disable-features=TrackingProtection3pcd,BlockThirdPartyCookies,SameSiteByDefaultCookies',
                            '--disable-web-security',
                        ]
                    )
                context = await browser.new_context(
                    locale='th-TH',
                    timezone_id='Asia/Bangkok',
                    record_video_dir='./recordings',
                    record_video_size={'width': 1920, 'height': 1080},
                    has_touch=True,
                    highlight_elements=True,
                    wait_for_network_idle_page_load_time=3.0,
                    user_agent=os.getenv(
                        'USER_AGENT',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.100 Safari/537.36'
                    ),
                      user_data_dir='~/.config/browseruse/profiles/default'
                    ,
                    extra_http_headers={'Accept-Language': 'th-TH,th;q=0.9'}
                )
                page = await context.new_page()
                session = BrowserSession(page=page, record_video_dir='./recordings')
                agent = Agent(
                    task="เข้าไปที่ dooball66n.com และหา match เรอัล มายอร์ก้า vs ปาร์ม่า เพื่อเปิด video stream",
                    llm=llm,
                    use_vision=True,
                    vision_detail_level='auto',
                    save_conversation_path="/tmp/conversation.json",
                    browser_session=session,
                    # stealth=True,
                )
                result = await agent.run()
                print(f"✅ เสร็จสิ้น (รอบ 2): {result.final_result}")
        except Exception as e2:
            print(f"❌ ยังคงมีปัญหา: {e2}")

if __name__ == "__main__":
    asyncio.run(main())