# 🐍 Razer Gold PIN Checker (Undetected TLS)

<img src="https://i.imgur.com/JEHQuPN.png">

This Python tool allows you to log into your Razer Gold account and validate Razer Gold PIN codes — without using a browser. It operates via a TLS fingerprinted session that mimics Chrome behavior and includes CAPTCHA solving using CapSolver.

The tool is fully automated and designed to work with proxyless requests.

Currently, this version is tailored for **Turkish Lira (₺)**. However, it can be easily modified to support other currencies.

---

### ⚙️ Features

- TLS client session mimicking real Chrome browser
- Logs into Razer Gold accounts with email & encrypted password
- Automatically solves ReCAPTCHA v2 via CapSolver (no proxy required)
- Checks Razer Gold PIN codes and logs successful redemptions
- Multi-code processing with optional threading
- Logs invalid codes to wrong.txt, valid ones are logged with their value
- Displays total loaded balance at the end

---

### 📦 Installation

Make sure Python 3.8+ is installed.

Install dependencies:

```
pip install tls-client loguru capsolver
```

---

### 📁 File Structure

- config.json: Login credentials and CapSolver key
- codes.txt: List of Razer Gold PIN codes (one per line)
- wrong.txt: Automatically generated file that stores failed codes

Example config.json:
```
{
    "EMAIL": "your_email@example.com",
    "PASSWORD": "U2FsdGVkX19...==",
    "CAPSOLVER_KEY": "your-capsolver-api-key"
}
```

⚠️ The PASSWORD must be in encrypted form. You can retrieve this by opening Razer Gold’s login page in a browser and monitoring network traffic after logging in. Look for the field encryptedPw in the POST request.

---

### 🔐 Important Notes on Login

The login XML payload:
```
<COP><User><email>{EMAIL}</email><password>{PASSWORD}</password></User><ServiceCode>0060</ServiceCode></COP>
```

The ServiceCode may change based on screen resolution. It defaults to 0060 for 1920x1080 resolution. You must verify this if you use a different screen setup.

---

### 🚀 How to Use

- Open your browser and log into https://gold.razer.com
- Use developer tools to capture the login request and extract the encrypted password
- Save your config.json with the encrypted password and CapSolver key
- Add your PIN codes into codes.txt

Run the script:
```
python main.py
```

The script will:
- Log into your Razer account
- Solve ReCAPTCHA using CapSolver
- Attempt to redeem each PIN code
- Print and log the value of successfully redeemed codes
- Skip or log failed codes
- Print your final wallet balance

---

### 💡 Tips

- You can increase the max_workers value in the script for more parallel requests
- A delay is included to prevent triggering rate limits
- Valid PIN codes are displayed with the amount credited in your wallet
- Invalid or already-used codes are saved into wrong.txt

---

### ⚠️ Disclaimer
This project is for educational and personal use only. You are responsible for how you use this tool. The developer assumes no liability for any misuse, account bans, or violations of Razer's terms of service.
