import re
import socket
from flask import Flask, render_template, request
import dns.resolver
import dns.exception

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024  # limit request size

EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")

def check_email(raw):
    address = raw.strip()
    if not address:
        return {"email": raw, "status": "Unknown", "reason": "Blank entry."}

    if len(address) > 254 or not EMAIL_RE.fullmatch(address):
        return {"email": address, "status": "Likely to bounce", "reason": "The address does not match the expected email format."}

    domain = address.rsplit("@", 1)[1].rstrip(".")
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=3.0)
        mx_records = [str(item.exchange).rstrip(".") for item in answers]
        # An MX record is evidence that the domain is configured to receive mail,
        # not proof that a specific mailbox exists or will accept a message.
        if mx_records:
            return {
                "email": address,
                "status": "Likely to be delivered",
                "reason": "The domain publishes mail-server (MX) records. The mailbox itself has not been verified."
            }
        return {"email": address, "status": "Likely to bounce", "reason": "No mail-server records were found for this domain."}
    except dns.resolver.NXDOMAIN:
        return {"email": address, "status": "Likely to bounce", "reason": "The email domain does not exist in DNS."}
    except dns.resolver.NoAnswer:
        # RFC fallback: some domains accept mail at their address records without MX.
        try:
            dns.resolver.resolve(domain, "A", lifetime=2.0)
            return {"email": address, "status": "Unknown", "reason": "No MX record; domain has an address record, but mail acceptance cannot be confirmed."}
        except Exception:
            return {"email": address, "status": "Likely to bounce", "reason": "No MX or usable address record was found."}
    except (dns.exception.Timeout, dns.resolver.NoNameservers, socket.timeout):
        return {"email": address, "status": "Unknown", "reason": "DNS lookup timed out or could not be completed."}
    except Exception:
        return {"email": address, "status": "Unknown", "reason": "The domain could not be checked reliably."}

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    raw_list = ""
    if request.method == "POST":
        raw_list = request.form.get("emails", "")[:20000]
        # Accept one address per line, comma, or semicolon. Keep duplicates as entered.
        entries = [x.strip() for x in re.split(r"[\n,;]+", raw_list) if x.strip()]
        if len(entries) > 100:
            results = [{"email": "", "status": "Unknown", "reason": "Please check no more than 100 addresses at a time."}]
        else:
            results = [check_email(entry) for entry in entries]
    return render_template("index.html", results=results, raw_list=raw_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
