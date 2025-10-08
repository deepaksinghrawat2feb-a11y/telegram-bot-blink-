from flask import Flask, request

app = Flask(__name__)

@app.route("/callback", methods=["GET", "POST"])
def callback():
    data = request.args.to_dict() if request.method == "GET" else request.get_json(silent=True) or request.form.to_dict()
    app.logger.info(f"Callback received: {data}")
    return {"ok": True, "data": data}, 200

@app.route("/")
def health():
    return {"status": "ok"}, 200
