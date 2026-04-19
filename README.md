# WebsiteChecker-Telegram-Bot
A lightweight Python bot that monitors your websites 24/7 and sends instant Telegram alerts when a site goes down or recovers — with /status command support.
# 🌐 WebsiteChecker-Telegram-Bot

A lightweight, 100% free website monitoring bot that runs on your Linux server or AWS EC2 and sends instant Telegram notifications when your sites go down or recover.

No paid services. No third-party monitoring tools. Just Python + Telegram.

---

## ✨ Features

- 🔴 Instant alert when a site goes down (500, 403, 404, timeouts, etc.)
- 🟢 Recovery alert when a site comes back up
- 📊 `/status` command — check all sites anytime on Telegram
- 🤫 No spam — only notified on changes, not every check
- ⚙️ Runs 24/7 as a background service with systemd
- 🆓 Completely free — no API costs, no subscriptions

---

## 📸 Preview

```
✅ Website Monitor is now running!
You'll only be notified when a site goes down or recovers.
Type /status anytime to check all sites.
```

```
💥 SITE ALERT!
URL: https://yoursite.com
Status: 500
Type /status to see all sites.
```
