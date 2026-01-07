# Zeabur & Koyeb 自动登录

自动登录 Zeabur 和 Koyeb 平台，保持账户活跃。通过 GitHub Actions 每 10 天自动运行一次。

## 🚀 快速开始

### 1. Fork 仓库

点击右上角 **Fork** 按钮，将此仓库 Fork 到你的账户。

### 2. 配置 Secrets

在你的仓库中，进入 **Settings → Secrets and variables → Actions → New repository secret**，添加以下 Secrets：

| Secret 名称 | 必填 | 说明 |
|------------|------|------|
| `GH_USERNAME` | ✅ | GitHub 用户名 |
| `GH_PASSWORD` | ✅ | GitHub 密码 |
| `GH_2FA_SECRET` | ❌ | TOTP 密钥（如使用 TOTP 2FA）|
| `TELEGRAM_BOT_TOKEN` | ❌ | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | ❌ | Telegram Chat ID |

### 3. 启用 Actions

进入仓库的 **Actions** 页面，点击 **I understand my workflows, go ahead and enable them**。

### 4. 手动测试

在 **Actions** 页面，选择 **Auto Login** workflow，点击 **Run workflow** 手动触发一次测试。

## ⏰ 运行时间

默认每 10 天运行一次（每月 1 日、11 日、21 日 UTC 00:00）。

如需修改，编辑 `.github/workflows/auto_login.yml` 中的 cron 表达式。

## 📁 文件结构

```
.
├── .github/workflows/
│   └── auto_login.yml    # GitHub Actions 配置
├── scripts/
│   └── auto_login.py     # 自动登录脚本
├── requirements.txt      # Python 依赖
└── README.md
```

## ⚠️ 注意事项

1. **两步验证 (2FA)**
   - 如果你的 GitHub 账户启用了 TOTP 2FA，请配置 `GH_2FA_SECRET`
   - 如果使用 GitHub Mobile，脚本会等待 60 秒供你手动确认

2. **设备验证**
   - 如果 GitHub 提示设备验证，脚本会等待 30 秒
   - 请及时检查邮箱完成验证

3. **首次授权**
   - 首次登录可能需要授权 OAuth
   - 建议先手动登录一次完成授权

## 📄 License

MIT License
