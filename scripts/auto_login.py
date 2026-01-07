#!/usr/bin/env python3
"""
Zeabur & Koyeb 自动登录脚本
通过 GitHub OAuth 登录，保持账户活跃
"""

import os
import sys
import time
import asyncio
import requests
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 配置
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

# 环境变量
GH_USERNAME = os.environ.get("GH_USERNAME", "")
GH_PASSWORD = os.environ.get("GH_PASSWORD", "")
GH_2FA_SECRET = os.environ.get("GH_2FA_SECRET", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def log(message: str):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def send_telegram_notification(message: str):
    """发送 Telegram 通知"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("Telegram 未配置，跳过通知")
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
            log("Telegram 通知发送成功")
            return True
        else:
            log(f"Telegram 通知发送失败: {response.text}")
            return False
    except Exception as e:
        log(f"Telegram 通知异常: {e}")
        return False


def get_totp_code(secret: str) -> str:
    """生成 TOTP 验证码"""
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.now()
    except ImportError:
        log("pyotp 未安装，无法生成 TOTP 验证码")
        return ""
    except Exception as e:
        log(f"生成 TOTP 验证码失败: {e}")
        return ""


async def handle_github_login(page):
    """处理 GitHub 登录流程"""
    log("开始 GitHub 登录流程...")
    
    # 等待 GitHub 登录页面加载
    try:
        await page.wait_for_selector('input[name="login"], input[id="login_field"]', timeout=10000)
    except PlaywrightTimeoutError:
        # 可能已经登录过，检查是否在授权页面
        if "github.com/login/oauth/authorize" in page.url:
            log("已在 OAuth 授权页面")
            authorize_btn = page.locator('button[name="authorize"], input[value="Authorize"]')
            if await authorize_btn.count() > 0:
                await authorize_btn.first.click()
                log("点击授权按钮")
            return True
        elif "github.com" not in page.url:
            log("可能已完成登录，当前URL: " + page.url)
            return True
        raise
    
    # 输入用户名
    log("输入 GitHub 用户名...")
    login_input = page.locator('input[name="login"], input[id="login_field"]').first
    await login_input.fill(GH_USERNAME)
    
    # 输入密码
    log("输入 GitHub 密码...")
    password_input = page.locator('input[name="password"], input[id="password"]').first
    await password_input.fill(GH_PASSWORD)
    
    # 点击登录按钮
    log("点击登录按钮...")
    submit_btn = page.locator('input[type="submit"], button[type="submit"]').first
    await submit_btn.click()
    
    # 等待页面响应
    await page.wait_for_timeout(3000)
    
    # 检查是否需要设备验证
    if "device-verification" in page.url or await page.locator('text=Device verification').count() > 0:
        log("⚠️ 需要设备验证，请在30秒内完成验证...")
        await page.wait_for_timeout(30000)
    
    # 检查是否需要 2FA
    if await page.locator('input[id="app_totp"], input[name="otp"]').count() > 0:
        log("检测到 2FA 验证...")
        if GH_2FA_SECRET:
            totp_code = get_totp_code(GH_2FA_SECRET)
            if totp_code:
                log(f"输入 TOTP 验证码...")
                otp_input = page.locator('input[id="app_totp"], input[name="otp"]').first
                await otp_input.fill(totp_code)
                await page.wait_for_timeout(2000)
        else:
            log("⚠️ 需要 2FA 但未配置 GH_2FA_SECRET，请手动完成验证...")
            await page.wait_for_timeout(60000)
    
    # 检查是否需要 OAuth 授权
    await page.wait_for_timeout(2000)
    if "github.com/login/oauth/authorize" in page.url:
        log("检测到 OAuth 授权页面...")
        authorize_btn = page.locator('button[name="authorize"], button:has-text("Authorize")')
        if await authorize_btn.count() > 0:
            await authorize_btn.first.click()
            log("点击授权按钮")
            await page.wait_for_timeout(3000)
    
    return True


async def login_to_platform(platform_key: str, browser):
    """登录到指定平台"""
    platform = PLATFORMS[platform_key]
    log(f"====== 开始登录 {platform['name']} ======")
    
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = await context.new_page()
    
    try:
        # 访问登录页面
        log(f"访问 {platform['login_url']}")
        await page.goto(platform['login_url'], wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 点击 GitHub 登录按钮
        log("寻找 GitHub 登录按钮...")
        github_btn = None
        
        # 尝试多种选择器
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
                    log(f"找到 GitHub 按钮: {selector}")
                    break
            except:
                continue
        
        if github_btn:
            await github_btn.click()
            log("已点击 GitHub 登录按钮")
            await page.wait_for_timeout(3000)
        else:
            log("⚠️ 未找到 GitHub 登录按钮，尝试直接访问...")
        
        # 如果跳转到 GitHub，处理登录
        if "github.com" in page.url:
            await handle_github_login(page)
        
        # 等待重定向回平台
        log("等待登录完成...")
        await page.wait_for_timeout(5000)
        
        # 验证登录成功
        current_url = page.url
        if platform["dashboard_url"] in current_url or "dashboard" in current_url.lower():
            log(f"✅ {platform['name']} 登录成功!")
            return True
        else:
            # 尝试访问 dashboard
            await page.goto(platform["dashboard_url"], wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            if "sign" not in page.url.lower() and "login" not in page.url.lower():
                log(f"✅ {platform['name']} 登录成功!")
                return True
            else:
                log(f"❌ {platform['name']} 登录可能失败，当前URL: {page.url}")
                return False
                
    except Exception as e:
        log(f"❌ {platform['name']} 登录异常: {e}")
        return False
    finally:
        await context.close()


async def main():
    """主函数"""
    log("=" * 50)
    log("Zeabur & Koyeb 自动登录脚本启动")
    log("=" * 50)
    
    # 验证必要的环境变量
    if not GH_USERNAME or not GH_PASSWORD:
        log("❌ 错误: 请设置 GH_USERNAME 和 GH_PASSWORD 环境变量")
        sys.exit(1)
    
    results = {}
    
    async with async_playwright() as p:
        log("启动浏览器...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        try:
            # 登录所有平台
            for platform_key in PLATFORMS:
                try:
                    success = await login_to_platform(platform_key, browser)
                    results[platform_key] = success
                except Exception as e:
                    log(f"❌ {platform_key} 登录失败: {e}")
                    results[platform_key] = False
                
                # 平台之间等待一下
                await asyncio.sleep(3)
                
        finally:
            await browser.close()
            log("浏览器已关闭")
    
    # 生成报告
    log("=" * 50)
    log("登录结果汇总:")
    success_count = 0
    report_lines = ["<b>🔐 自动登录报告</b>\n"]
    
    for platform_key, success in results.items():
        platform_name = PLATFORMS[platform_key]["name"]
        status = "✅ 成功" if success else "❌ 失败"
        log(f"  {platform_name}: {status}")
        report_lines.append(f"• {platform_name}: {status}")
        if success:
            success_count += 1
    
    report_lines.append(f"\n⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 发送通知
    send_telegram_notification("\n".join(report_lines))
    
    log("=" * 50)
    
    # 如果有任何失败，返回非零退出码
    if success_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
