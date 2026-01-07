#!/usr/bin/env python3
"""
Zeabur & Koyeb 鑷姩鐧诲綍鑴氭湰
閫氳繃 GitHub OAuth 鐧诲綍锛屼繚鎸佽处鎴锋椿璺?
"""

import os
import sys
import time
import asyncio
import requests
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 閰嶇疆
PLATFORMS = {
    "zeabur": {
        "name": "Zeabur",
        "login_url": "https://dash.zeabur.com/sign-in",
        "dashboard_url": "https://dash.zeabur.com/",
        "github_button_selector": "button:has-text('GitHub'), a:has-text('GitHub'), [data-testid='github-login']",
    },
    "koyeb": {
        "name": "Koyeb", 
        "login_url": "https://app.koyeb.com/auth/signin",
        "dashboard_url": "https://app.koyeb.com/",
        "github_button_selector": "button:has-text('GitHub'), a:has-text('GitHub'), [data-testid='github-login']",
    }
}

# 鐜鍙橀噺
GH_USERNAME = os.environ.get("GH_USERNAME", "")
GH_PASSWORD = os.environ.get("GH_PASSWORD", "")
GH_2FA_SECRET = os.environ.get("GH_2FA_SECRET", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def log(message: str):
    """鎵撳嵃甯︽椂闂存埑鐨勬棩蹇?""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def send_telegram_notification(message: str):
    """鍙戦€?Telegram 閫氱煡"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("Telegram 鏈厤缃紝璺宠繃閫氱煡")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            log("Telegram 閫氱煡鍙戦€佹垚鍔?)
            return True
        else:
            log(f"Telegram 閫氱煡鍙戦€佸け璐? {response.text}")
            return False
    except Exception as e:
        log(f"Telegram 閫氱煡寮傚父: {e}")
        return False


def get_totp_code(secret: str) -> str:
    """鐢熸垚 TOTP 楠岃瘉鐮?""
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.now()
    except ImportError:
        log("pyotp 鏈畨瑁咃紝鏃犳硶鐢熸垚 TOTP 楠岃瘉鐮?)
        return ""
    except Exception as e:
        log(f"鐢熸垚 TOTP 楠岃瘉鐮佸け璐? {e}")
        return ""


async def handle_github_login(page):
    """澶勭悊 GitHub 鐧诲綍娴佺▼"""
    log("寮€濮?GitHub 鐧诲綍娴佺▼...")
    
    # 绛夊緟 GitHub 鐧诲綍椤甸潰鍔犺浇
    try:
        await page.wait_for_selector('input[name="login"], input[id="login_field"]', timeout=10000)
    except PlaywrightTimeoutError:
        # 鍙兘宸茬粡鐧诲綍杩囷紝妫€鏌ユ槸鍚﹀湪鎺堟潈椤甸潰
        if "github.com/login/oauth/authorize" in page.url:
            log("宸插湪 OAuth 鎺堟潈椤甸潰")
            authorize_btn = page.locator('button[name="authorize"], input[value="Authorize"]')
            if await authorize_btn.count() > 0:
                await authorize_btn.first.click()
                log("鐐瑰嚮鎺堟潈鎸夐挳")
            return True
        elif "github.com" not in page.url:
            log("鍙兘宸插畬鎴愮櫥褰曪紝褰撳墠URL: " + page.url)
            return True
        raise
    
    # 杈撳叆鐢ㄦ埛鍚?
    log("杈撳叆 GitHub 鐢ㄦ埛鍚?..")
    login_input = page.locator('input[name="login"], input[id="login_field"]').first
    await login_input.fill(GH_USERNAME)
    
    # 杈撳叆瀵嗙爜
    log("杈撳叆 GitHub 瀵嗙爜...")
    password_input = page.locator('input[name="password"], input[id="password"]').first
    await password_input.fill(GH_PASSWORD)
    
    # 鐐瑰嚮鐧诲綍鎸夐挳
    log("鐐瑰嚮鐧诲綍鎸夐挳...")
    submit_btn = page.locator('input[type="submit"], button[type="submit"]').first
    await submit_btn.click()
    
    # 绛夊緟椤甸潰鍝嶅簲
    await page.wait_for_timeout(3000)
    
    # 妫€鏌ユ槸鍚﹂渶瑕佽澶囬獙璇?
    if "device-verification" in page.url or await page.locator('text=Device verification').count() > 0:
        log("鈿狅笍 闇€瑕佽澶囬獙璇侊紝璇峰湪30绉掑唴瀹屾垚楠岃瘉...")
        await page.wait_for_timeout(30000)
    
    # 妫€鏌ユ槸鍚﹂渶瑕?2FA
    if await page.locator('input[id="app_totp"], input[name="otp"]').count() > 0:
        log("妫€娴嬪埌 2FA 楠岃瘉...")
        if GH_2FA_SECRET:
            totp_code = get_totp_code(GH_2FA_SECRET)
            if totp_code:
                log(f"杈撳叆 TOTP 楠岃瘉鐮?..")
                otp_input = page.locator('input[id="app_totp"], input[name="otp"]').first
                await otp_input.fill(totp_code)
                await page.wait_for_timeout(2000)
        else:
            log("鈿狅笍 闇€瑕?2FA 浣嗘湭閰嶇疆 GH_2FA_SECRET锛岃鎵嬪姩瀹屾垚楠岃瘉...")
            await page.wait_for_timeout(60000)
    
    # 妫€鏌ユ槸鍚﹂渶瑕?OAuth 鎺堟潈
    await page.wait_for_timeout(2000)
    if "github.com/login/oauth/authorize" in page.url:
        log("妫€娴嬪埌 OAuth 鎺堟潈椤甸潰...")
        authorize_btn = page.locator('button[name="authorize"], button:has-text("Authorize")')
        if await authorize_btn.count() > 0:
            await authorize_btn.first.click()
            log("鐐瑰嚮鎺堟潈鎸夐挳")
            await page.wait_for_timeout(3000)
    
    return True


async def login_to_platform(platform_key: str, browser):
    """鐧诲綍鍒版寚瀹氬钩鍙?""
    platform = PLATFORMS[platform_key]
    log(f"====== 寮€濮嬬櫥褰?{platform['name']} ======")
    
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = await context.new_page()
    
    try:
        # 璁块棶鐧诲綍椤甸潰
        log(f"璁块棶 {platform['login_url']}")
        await page.goto(platform['login_url'], wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 鐐瑰嚮 GitHub 鐧诲綍鎸夐挳
        log("瀵绘壘 GitHub 鐧诲綍鎸夐挳...")
        github_btn = None
        
        # 灏濊瘯澶氱閫夋嫨鍣?
        selectors = [
            "button:has-text('GitHub')",
            "a:has-text('GitHub')",
            "button:has-text('Continue with GitHub')",
            "a:has-text('Continue with GitHub')",
            "[data-testid='github-login']",
            ".github-login",
            "button:has-text('Sign in with GitHub')",
            "a:has-text('Sign in with GitHub')",
        ]
        
        for selector in selectors:
            try:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    github_btn = btn.first
                    log(f"鎵惧埌 GitHub 鎸夐挳: {selector}")
                    break
            except:
                continue
        
        if github_btn:
            await github_btn.click()
            log("宸茬偣鍑?GitHub 鐧诲綍鎸夐挳")
            await page.wait_for_timeout(3000)
        else:
            log("鈿狅笍 鏈壘鍒?GitHub 鐧诲綍鎸夐挳锛屽皾璇曠洿鎺ヨ闂?..")
        
        # 濡傛灉璺宠浆鍒?GitHub锛屽鐞嗙櫥褰?
        if "github.com" in page.url:
            await handle_github_login(page)
        
        # 绛夊緟閲嶅畾鍚戝洖骞冲彴
        log("绛夊緟鐧诲綍瀹屾垚...")
        await page.wait_for_timeout(5000)
        
        # 楠岃瘉鐧诲綍鎴愬姛
        current_url = page.url
        if platform["dashboard_url"] in current_url or "dashboard" in current_url.lower():
            log(f"鉁?{platform['name']} 鐧诲綍鎴愬姛!")
            return True
        else:
            # 灏濊瘯璁块棶 dashboard
            await page.goto(platform["dashboard_url"], wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            if "sign" not in page.url.lower() and "login" not in page.url.lower():
                log(f"鉁?{platform['name']} 鐧诲綍鎴愬姛!")
                return True
            else:
                log(f"鉂?{platform['name']} 鐧诲綍鍙兘澶辫触锛屽綋鍓峌RL: {page.url}")
                return False
                
    except Exception as e:
        log(f"鉂?{platform['name']} 鐧诲綍寮傚父: {e}")
        return False
    finally:
        await context.close()


async def main():
    """涓诲嚱鏁?""
    log("=" * 50)
    log("Zeabur & Koyeb 鑷姩鐧诲綍鑴氭湰鍚姩")
    log("=" * 50)
    
    # 楠岃瘉蹇呰鐨勭幆澧冨彉閲?
    if not GH_USERNAME or not GH_PASSWORD:
        log("鉂?閿欒: 璇疯缃?GH_USERNAME 鍜?GH_PASSWORD 鐜鍙橀噺")
        sys.exit(1)
    
    results = {}
    
    async with async_playwright() as p:
        log("鍚姩娴忚鍣?..")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        try:
            # 鐧诲綍鎵€鏈夊钩鍙?
            for platform_key in PLATFORMS:
                try:
                    success = await login_to_platform(platform_key, browser)
                    results[platform_key] = success
                except Exception as e:
                    log(f"鉂?{platform_key} 鐧诲綍澶辫触: {e}")
                    results[platform_key] = False
                
                # 骞冲彴涔嬮棿绛夊緟涓€涓?
                await asyncio.sleep(3)
                
        finally:
            await browser.close()
            log("娴忚鍣ㄥ凡鍏抽棴")
    
    # 鐢熸垚鎶ュ憡
    log("=" * 50)
    log("鐧诲綍缁撴灉姹囨€?")
    success_count = 0
    report_lines = ["<b>馃攼 鑷姩鐧诲綍鎶ュ憡</b>\n"]
    
    for platform_key, success in results.items():
        platform_name = PLATFORMS[platform_key]["name"]
        status = "鉁?鎴愬姛" if success else "鉂?澶辫触"
        log(f"  {platform_name}: {status}")
        report_lines.append(f"鈥?{platform_name}: {status}")
        if success:
            success_count += 1
    
    report_lines.append(f"\n鈴?鏃堕棿: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 鍙戦€侀€氱煡
    send_telegram_notification("\n".join(report_lines))
    
    log("=" * 50)
    
    # 濡傛灉鏈変换浣曞け璐ワ紝杩斿洖闈為浂閫€鍑虹爜
    if success_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
