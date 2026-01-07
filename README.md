# Zeabur & Koyeb 鑷姩鐧诲綍

鑷姩鐧诲綍 Zeabur 鍜?Koyeb 骞冲彴锛屼繚鎸佽处鎴锋椿璺冦€傞€氳繃 GitHub Actions 姣?10 澶╄嚜鍔ㄨ繍琛屼竴娆°€?

## 馃殌 蹇€熷紑濮?

### 1. Fork 浠撳簱

鐐瑰嚮鍙充笂瑙?**Fork** 鎸夐挳锛屽皢姝や粨搴?Fork 鍒颁綘鐨勮处鎴枫€?

### 2. 閰嶇疆 Secrets

鍦ㄤ綘鐨勪粨搴撲腑锛岃繘鍏?**Settings 鈫?Secrets and variables 鈫?Actions 鈫?New repository secret**锛屾坊鍔犱互涓?Secrets锛?

| Secret 鍚嶇О | 蹇呭～ | 璇存槑 |
|------------|------|------|
| `GH_USERNAME` | 鉁?| GitHub 鐢ㄦ埛鍚?|
| `GH_PASSWORD` | 鉁?| GitHub 瀵嗙爜 |
| `GH_2FA_SECRET` | 鉂?| TOTP 瀵嗛挜锛堝浣跨敤 TOTP 2FA锛墊
| `TELEGRAM_BOT_TOKEN` | 鉂?| Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | 鉂?| Telegram Chat ID |

### 3. 鍚敤 Actions

杩涘叆浠撳簱鐨?**Actions** 椤甸潰锛岀偣鍑?**I understand my workflows, go ahead and enable them**銆?

### 4. 鎵嬪姩娴嬭瘯

鍦?**Actions** 椤甸潰锛岄€夋嫨 **Auto Login** workflow锛岀偣鍑?**Run workflow** 鎵嬪姩瑙﹀彂涓€娆℃祴璇曘€?

## 鈴?杩愯鏃堕棿

榛樿姣?10 澶╄繍琛屼竴娆★紙姣忔湀 1 鏃ャ€?1 鏃ャ€?1 鏃?UTC 00:00锛夈€?

濡傞渶淇敼锛岀紪杈?`.github/workflows/auto_login.yml` 涓殑 cron 琛ㄨ揪寮忋€?

## 馃搧 鏂囦欢缁撴瀯

```
.
鈹溾攢鈹€ .github/workflows/
鈹?  鈹斺攢鈹€ auto_login.yml    # GitHub Actions 閰嶇疆
鈹溾攢鈹€ scripts/
鈹?  鈹斺攢鈹€ auto_login.py     # 鑷姩鐧诲綍鑴氭湰
鈹溾攢鈹€ requirements.txt      # Python 渚濊禆
鈹斺攢鈹€ README.md
```

## 鈿狅笍 娉ㄦ剰浜嬮」

1. **涓ゆ楠岃瘉 (2FA)**
   - 濡傛灉浣犵殑 GitHub 璐︽埛鍚敤浜?TOTP 2FA锛岃閰嶇疆 `GH_2FA_SECRET`
   - 濡傛灉浣跨敤 GitHub Mobile锛岃剼鏈細绛夊緟 60 绉掍緵浣犳墜鍔ㄧ‘璁?

2. **璁惧楠岃瘉**
   - 濡傛灉 GitHub 鎻愮ず璁惧楠岃瘉锛岃剼鏈細绛夊緟 30 绉?
   - 璇峰強鏃舵鏌ラ偖绠卞畬鎴愰獙璇?

3. **棣栨鎺堟潈**
   - 棣栨鐧诲綍鍙兘闇€瑕佹巿鏉?OAuth
   - 寤鸿鍏堟墜鍔ㄧ櫥褰曚竴娆″畬鎴愭巿鏉?

## 馃搫 License

MIT License
