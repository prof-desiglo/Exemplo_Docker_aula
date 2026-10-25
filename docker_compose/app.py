import os
import time
import pymysql
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppass"),
        database=os.getenv("DB_NAME", "appdb"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

def init_db():
    # tenta algumas vezes, caso o MySQL ainda esteja iniciando
    for _ in range(15):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tarefas (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        titulo VARCHAR(255) NOT NULL,
                        criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            return
        except pymysql.err.OperationalError:
            time.sleep(2)
    raise RuntimeError("Não foi possível conectar ao MySQL")

PAGINA = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Tarefas</title>
  <style>
    body { font-family: sans-serif; max-width: 500px; margin: 40px auto; }
    li { margin: 6px 0; }
    input[type=text] { width: 70%; padding: 6px; }
  </style>
</head>
<body>
  <h1>Tarefas</h1>
  <form method="post" action="/add">
    <input type="text" name="titulo" placeholder="Nova tarefa" required>
    <button>Adicionar</button>
  </form>
  <ul>
    {% for t in tarefas %}
      <li>{{ t.titulo }}
        <a href="/del/{{ t.id }}">[x]</a>
      </li>
    {% endfor %}
  </ul>
</body>
</html>
"""

@app.route("/")
def index():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, titulo FROM tarefas ORDER BY id DESC")
        tarefas = cur.fetchall()
    return render_template_string(PAGINA, tarefas=tarefas)

@app.route("/add", methods=["POST"])
def add():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO tarefas (titulo) VALUES (%s)", (request.form["titulo"],))
    return redirect("/")

@app.route("/del/<int:tid>")
def delete(tid):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tarefas WHERE id = %s", (tid,))
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
