"""
LeafGuard — Flask Web Server

Serves the website and provides REST API:
  GET  /            → auth page (website/index.html)
  GET  /app         → main SPA (website/app.html)
  POST /api/auth/register
  POST /api/auth/login
  POST /api/auth/logout
  GET  /api/auth/me
  POST /api/chat    → LeafGuardAgent.chat()  (requires auth)

Run:
  pip install flask
  python server.py
  Open http://localhost:5000
"""

from __future__ import annotations
import hashlib, os, secrets, sqlite3, sys
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory, session

# ── Path setup ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "AI Models"))
sys.path.insert(0, str(ROOT / "recommendation Engine"))
sys.path.insert(0, str(ROOT / "AgroRAG"))

from dotenv import load_dotenv
load_dotenv(ROOT / "AgroRAG" / ".env")

# ── Flask ──────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=str(ROOT / "website"), static_url_path="")
app.secret_key = os.environ.get("LEAFGUARD_SECRET", "leafguard-dev-secret-2026-change-in-prod")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# ── SQLite ─────────────────────────────────────────────────────────────────
DB = ROOT / "users.db"

def _db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db():
    with _db() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dest_lat   REAL,
                dest_lng   REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id     INTEGER NOT NULL,
                product_id   TEXT,
                product_name TEXT    NOT NULL,
                qty          INTEGER NOT NULL DEFAULT 1,
                price        REAL    NOT NULL DEFAULT 0,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
        c.commit()

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Order tracking ─────────────────────────────────────────────────────────────
import datetime as _dt

_WAREHOUSE_LAT = 24.6877   # LeafGuard warehouse — Riyadh
_WAREHOUSE_LNG = 46.7219

_ORDER_STEPS = [
    {"key": "order_received",   "label": "Order Received",    "at_min": 0,  "pct": 10},
    {"key": "confirmed",        "label": "Order Confirmed",   "at_min": 1,  "pct": 25},
    {"key": "preparing",        "label": "Preparing Order",   "at_min": 3,  "pct": 50},
    {"key": "out_for_delivery", "label": "Out for Delivery",  "at_min": 7,  "pct": 75},
    {"key": "delivered",        "label": "Delivered",         "at_min": 13, "pct": 100},
]

def _order_status(created_at_str: str) -> dict:
    try:
        created = _dt.datetime.fromisoformat(created_at_str)
    except Exception:
        created = _dt.datetime.utcnow()
    elapsed = (_dt.datetime.utcnow() - created).total_seconds() / 60

    current = _ORDER_STEPS[0]
    for step in _ORDER_STEPS:
        if elapsed >= step["at_min"]:
            current = step

    return {
        "current_key":   current["key"],
        "current_label": current["label"],
        "progress":      current["pct"],
        "elapsed_min":   round(elapsed, 1),
        "steps": [{**s, "done": elapsed >= s["at_min"]} for s in _ORDER_STEPS],
    }

# ── Agent (lazy) ───────────────────────────────────────────────────────────
_agent = None

def _get_agent():
    global _agent
    if _agent is None:
        try:
            from agent import LeafGuardAgent
            _agent = LeafGuardAgent()
            print("[LeafGuard] Agent loaded successfully.")
        except Exception as exc:
            print(f"[LeafGuard] Agent failed to load: {exc}")
    return _agent

# ── Auth guard ─────────────────────────────────────────────────────────────
def require_auth(f):
    @wraps(f)
    def _wrap(*a, **kw):
        if "user_id" not in session:
            return jsonify({"error": "Not authenticated"}), 401
        return f(*a, **kw)
    return _wrap

# ── Page routes ────────────────────────────────────────────────────────────
@app.route("/")
def auth_page():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/app")
@app.route("/app.html")
def app_page():
    return send_from_directory(app.static_folder, "app.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# ── Auth endpoints ─────────────────────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def register():
    d        = request.get_json(force=True) or {}
    name     = (d.get("name") or "").strip()
    email    = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""

    if not (name and email and password):
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    try:
        with _db() as c:
            c.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
                (name, email, _hash(password)),
            )
            c.commit()
            user = c.execute(
                "SELECT id, name, email FROM users WHERE email=?", (email,)
            ).fetchone()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409

    session["user_id"]    = user["id"]
    session["user_name"]  = user["name"]
    session["user_email"] = user["email"]
    return jsonify({"id": user["id"], "name": user["name"], "email": user["email"]})


@app.route("/api/auth/login", methods=["POST"])
def login():
    d        = request.get_json(force=True) or {}
    email    = (d.get("email") or "").strip().lower()
    password = d.get("password") or ""

    with _db() as c:
        user = c.execute(
            "SELECT id, name, email FROM users WHERE email=? AND password_hash=?",
            (email, _hash(password)),
        ).fetchone()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"]    = user["id"]
    session["user_name"]  = user["name"]
    session["user_email"] = user["email"]
    return jsonify({"id": user["id"], "name": user["name"], "email": user["email"]})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/auth/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({
        "id":    session["user_id"],
        "name":  session["user_name"],
        "email": session["user_email"],
    })

# ── Chat endpoint ──────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
@require_auth
def chat():
    import json as _json, os as _os, tempfile

    image_path = None
    location   = None

    image_paths = []

    # Multipart = message + optional image files (image, image_1 … image_4)
    if request.content_type and "multipart/form-data" in request.content_type:
        message = (request.form.get("message") or "").strip()
        loc_raw = request.form.get("location")
        if loc_raw:
            try: location = _json.loads(loc_raw)
            except: pass
        for key in ["image", "image_1", "image_2", "image_3", "image_4"]:
            img = request.files.get(key)
            if img and img.filename:
                ext = _os.path.splitext(img.filename)[1] or ".jpg"
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                img.save(tmp.name)
                image_paths.append(tmp.name)
    else:
        d        = request.get_json(force=True) or {}
        message  = (d.get("message") or "").strip()
        location = d.get("location")

    if not message:
        return jsonify({"error": "message is required"}), 400

    if location and location.get("city"):
        message = (
            f"[User location: {location['city']}, {location.get('country','')}]\n\n"
            + message
        )

    agent = _get_agent()
    if not agent:
        return jsonify({
            "reply": (
                "The AI system is currently unavailable. "
                "Make sure your OpenAI API key is set in AgroRAG/.env "
                "and all Python dependencies are installed."
            ),
            "tools": [], "low_confidence": False,
        })

    _IMAGE_TOOLS = {"check_health_status", "classify_crop", "classify_disease", "classify_datepalm_disease"}

    def _check_confidence(tool_results):
        for name, res in tool_results.items():
            if name in _IMAGE_TOOLS:
                conf = res.get("confidence") if isinstance(res, dict) else None
                if isinstance(conf, (int, float)) and conf < 0.5:
                    return True
        return False

    try:
        if not image_paths:
            result = agent.chat(message, image_path=None)
            low_conf = _check_confidence(result.get("tool_results", {}))
            return jsonify({
                "reply": result["answer"],
                "tools": result.get("tools_used", []),
                "low_confidence": low_conf,
            })

        # Process each image and combine results
        answers, all_tools = [], []
        low_conf = False
        for i, path in enumerate(image_paths):
            r = agent.chat(message, image_path=path)
            prefix = f"**Image {i+1}:**\n" if len(image_paths) > 1 else ""
            answers.append(prefix + r["answer"])
            all_tools.extend(r.get("tools_used", []))
            if _check_confidence(r.get("tool_results", {})):
                low_conf = True

        combined = "\n\n---\n\n".join(answers)
        return jsonify({
            "reply": combined,
            "tools": list(dict.fromkeys(all_tools)),
            "low_confidence": low_conf,
        })
    except Exception as exc:
        return jsonify({"reply": f"Error: {exc}", "tools": [], "low_confidence": False})
    finally:
        for p in image_paths:
            try: _os.unlink(p)
            except: pass


# ── Order endpoints ────────────────────────────────────────────────────────────

@app.route("/api/order/submit", methods=["POST"])
@require_auth
def submit_order():
    d        = request.get_json(force=True) or {}
    items    = d.get("items", [])
    dest_lat = d.get("dest_lat")
    dest_lng = d.get("dest_lng")

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    with _db() as c:
        cur = c.execute(
            "INSERT INTO orders (user_id, dest_lat, dest_lng) VALUES (?,?,?)",
            (session["user_id"], dest_lat, dest_lng),
        )
        order_id = cur.lastrowid
        for item in items:
            c.execute(
                "INSERT INTO order_items (order_id, product_id, product_name, qty, price)"
                " VALUES (?,?,?,?,?)",
                (order_id, item.get("id"), item.get("name", ""),
                 int(item.get("qty", 1)), float(item.get("price", 0))),
            )
        c.commit()

    return jsonify({"ok": True, "order_id": order_id})


@app.route("/api/orders", methods=["GET"])
@require_auth
def get_orders():
    with _db() as c:
        rows = c.execute(
            "SELECT id, created_at FROM orders WHERE user_id=? ORDER BY id DESC",
            (session["user_id"],),
        ).fetchall()

    result = []
    for row in rows:
        st = _order_status(row["created_at"])
        with _db() as c:
            items = c.execute(
                "SELECT product_name, qty FROM order_items WHERE order_id=?",
                (row["id"],),
            ).fetchall()
        total_qty = sum(i["qty"] for i in items)
        preview   = items[0]["product_name"][:32] if items else ""
        result.append({
            "id":           row["id"],
            "created":      row["created_at"][:16].replace("T", " "),
            "status_key":   st["current_key"],
            "status_label": st["current_label"],
            "progress":     st["progress"],
            "total_qty":    total_qty,
            "preview":      preview,
        })

    return jsonify({"ok": True, "orders": result})


@app.route("/api/order/<int:order_id>", methods=["GET"])
@require_auth
def get_order(order_id):
    with _db() as c:
        row = c.execute(
            "SELECT id, created_at, dest_lat, dest_lng FROM orders"
            " WHERE id=? AND user_id=?",
            (order_id, session["user_id"]),
        ).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        items = c.execute(
            "SELECT product_name, qty, price FROM order_items WHERE order_id=?",
            (order_id,),
        ).fetchall()

    dest = ({"lat": row["dest_lat"], "lng": row["dest_lng"]}
            if row["dest_lat"] and row["dest_lng"] else None)

    return jsonify({
        "ok":       True,
        "status":   _order_status(row["created_at"]),
        "dest":     dest,
        "warehouse": {"lat": _WAREHOUSE_LAT, "lng": _WAREHOUSE_LNG},
        "items":    [{"name": i["product_name"], "qty": i["qty"], "price": i["price"]}
                     for i in items],
    })


@app.route("/api/order/<int:order_id>/dest", methods=["POST"])
@require_auth
def update_order_dest(order_id):
    d   = request.get_json(force=True) or {}
    lat = d.get("lat")
    lng = d.get("lng")
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng required"}), 400
    with _db() as c:
        c.execute(
            "UPDATE orders SET dest_lat=?, dest_lng=? WHERE id=? AND user_id=?",
            (lat, lng, order_id, session["user_id"]),
        )
        c.commit()
    return jsonify({"ok": True})


if __name__ == "__main__":
    _init_db()
    print("=" * 52)
    print("  LeafGuard Web Server  —  http://localhost:5000")
    print("=" * 52)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port, use_reloader=False)
