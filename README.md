# Email Address Checker — ShieldNex Software Development Task

A small Flask web app that accepts a list of email addresses and reports **Likely to be delivered**, **Likely to bounce**, or **Unknown**.

## How it works
1. Checks whether each address follows a basic email-address format.
2. Looks up DNS mail-exchange (MX) records for the domain.
3. Uses a cautious result:
   - **Likely to bounce**: malformed address, non-existent domain, or no usable mail configuration found.
   - **Likely to be delivered**: the domain publishes MX records. This does **not** prove that the mailbox exists.
   - **Unknown**: DNS lookup fails or available evidence is inconclusive.
4. It does not send email, attempt mailbox enumeration, or save submitted addresses to a database.

## Limitations
Many mail providers intentionally do not confirm whether an individual mailbox exists. Therefore, this application cannot guarantee delivery and may classify an address as likely to be delivered even if the mailbox is disabled, full, or nonexistent.

Some hosting providers may block outbound DNS requests or limit DNS resolution. In that environment, results may be **Unknown**. The deployed version checks address syntax and domain mail configuration only; it does not perform SMTP mailbox verification and never sends messages.

## Run locally
Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in a browser.

## Deploy on Render
1. Push this repository to your GitHub account.
2. Sign in to Render and choose **New → Web Service**.
3. Connect the GitHub repository.
4. Use build command `pip install -r requirements.txt`.
5. Use start command `gunicorn app:app`.
6. Deploy, then open the public `onrender.com` URL and test it.

A `render.yaml` file is included as a deployment reference. Free-tier availability and platform policies can change.

## Privacy and safe use
- Do not paste sensitive address lists.
- Requests are processed in memory and not written to a database by this application.
- No email is sent to any address.
- Use only for legitimate, consent-based checking.
