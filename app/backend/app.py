import base64
from datetime import datetime, timezone
import functools
import hashlib
import hmac
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import secrets

import psycopg
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = os.environ["PORTAL_SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_COOKIE_SECURE=False,  # Piloto HTTP limitado a 127.0.0.1.
    PERMANENT_SESSION_LIFETIME=1800,
)

USERS = json.loads(base64.b64decode(os.environ["PORTAL_USERS_B64"]).decode("utf-8"))
audit_logger = logging.getLogger("uts.audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False
audit_handler = logging.StreamHandler()
audit_handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(audit_handler)
audit_file = os.environ.get("PORTAL_AUDIT_FILE")
if audit_file:
    file_handler = RotatingFileHandler(audit_file, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    audit_logger.addHandler(file_handler)


def audit(event, **details):
    record = {"timestamp": datetime.now(timezone.utc).isoformat(),
              "event": event, "user": session.get("user"), "role": session.get("role"),
              "path": request.path, "remote_addr": request.remote_addr, **details}
    audit_logger.info(json.dumps(record, ensure_ascii=False, sort_keys=True))


def verify_password(password, stored):
    salt = bytes.fromhex(stored["salt"])
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600000)
    return hmac.compare_digest(actual, bytes.fromhex(stored["hash"]))


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


def requires_roles(*roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            username = session.get("user")
            if username not in USERS:
                audit("auth_required")
                return redirect(url_for("login"))
            role = USERS[username]["role"]
            if role not in roles:
                audit("access_denied", required_roles=list(roles))
                abort(403)
            session["role"] = role
            return view(*args, **kwargs)
        return wrapped
    return decorator


def db_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"], dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
    )


def query(sql, params=None):
    try:
        with db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
    except psycopg.Error:
        audit("database_query_failed")
        app.logger.exception("Database query failed")
        abort(503)


@app.get("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        token = request.form.get("csrf", "")
        if not hmac.compare_digest(token, session.get("csrf", "")) or not token:
            abort(400)
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and verify_password(password, user):
            session.clear()
            session.permanent = True
            session["user"] = username
            session["role"] = user["role"]
            audit("login_success")
            return redirect(url_for("index"))
        audit("login_failed", attempted_user=username[:80])
        error = "Usuario o contraseña incorrectos."
    return render_template("login.html", error=error)


@app.post("/logout")
def logout():
    token = request.form.get("csrf", "")
    if not hmac.compare_digest(token, session.get("csrf", "")) or not token:
        abort(400)
    audit("logout")
    session.clear()
    return redirect(url_for("index"))


@app.get("/estudiantes")
@requires_roles("docente", "administrador")
def estudiantes():
    rows = query("SELECT id, nombres, apellidos, correo FROM estudiantes ORDER BY id")
    audit("data_access", resource="estudiantes", row_count=len(rows))
    return render_template("tabla.html", titulo="Estudiantes", encabezados=["ID", "Nombres", "Apellidos", "Correo"], filas=rows)


@app.get("/cursos")
@requires_roles("estudiante", "docente", "administrador")
def cursos():
    rows = query("SELECT id, codigo, nombre, semestre, creditos FROM cursos ORDER BY id")
    audit("data_access", resource="cursos", row_count=len(rows))
    return render_template("tabla.html", titulo="Cursos", encabezados=["ID", "Código", "Nombre", "Semestre", "Créditos"], filas=rows)


@app.get("/matriculas")
@requires_roles("estudiante", "docente", "administrador")
def matriculas():
    sql = """
        SELECT m.id, e.nombres || ' ' || e.apellidos, c.codigo, c.nombre,
               c.semestre, m.nota_final
        FROM matriculas AS m
        JOIN estudiantes AS e ON e.id = m.estudiante_id
        JOIN cursos AS c ON c.id = m.curso_id
    """
    student_id = USERS[session["user"]].get("student_id") if session["role"] == "estudiante" else None
    if session["role"] == "estudiante" and student_id is None:
        abort(403)
    if student_id is not None:
        rows = query(sql + " WHERE e.id = %s ORDER BY m.id", (student_id,))
    else:
        rows = query(sql + " ORDER BY m.id")
    audit("data_access", resource="matriculas", row_count=len(rows))
    return render_template("tabla.html", titulo="Matrículas y notas", encabezados=["ID", "Estudiante", "Código", "Curso", "Semestre", "Nota final"], filas=rows)


@app.get("/health")
def health():
    try:
        with db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
    except (psycopg.Error, OSError):
        audit("service_unavailable", service="postgresql")
        app.logger.exception("Database health check failed")
        return jsonify(status="unhealthy", database="unavailable"), 503
    return jsonify(status="ok", database="connected")
