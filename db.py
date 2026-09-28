"""Test_Prompt 数据库层（SQLite 适配版）。

原 MySQL 建表语句适配说明：
- BIGINT UNSIGNED AUTO_INCREMENT  ->  INTEGER PRIMARY KEY AUTOINCREMENT
- DECIMAL(12,6)                   ->  REAL（保留 6 位小数展示）
- ENGINE/CHARSET 子句             ->  SQLite 无需
- 外键                            ->  连接时需 PRAGMA foreign_keys = ON
"""
import os
import sqlite3

# 数据库文件：用户指定库名 Prompt_Test_DB，SQLite 以文件承载，后缀 .db 便于辨识
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Prompt_Test_DB.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS server (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    plat_name  TEXT NOT NULL DEFAULT '',
    base_url   TEXT NOT NULL DEFAULT '',
    company    TEXT NOT NULL DEFAULT '',
    homepage   TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_server_plat_name ON server(plat_name);

CREATE TABLE IF NOT EXISTS model (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    svc_id        INTEGER NOT NULL,
    model_name    TEXT NOT NULL DEFAULT '',
    in_token_fee  REAL NOT NULL DEFAULT 0,
    out_token_fee REAL NOT NULL DEFAULT 0,
    unit          TEXT NOT NULL DEFAULT '',
    type          TEXT NOT NULL DEFAULT '',
    url           TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (svc_id) REFERENCES server(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_model_svc_id ON model(svc_id);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """建表并首次写入示例数据（仅当 server 表为空时）。"""
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        cur = conn.execute("SELECT COUNT(*) AS c FROM server")
        if cur.fetchone()["c"] == 0:
            _seed(conn)
        conn.commit()
    finally:
        conn.close()


def _seed(conn):
    servers = [
        ("OpenAI", "https://api.openai.com/v1", "OpenAI Inc", "https://openai.com"),
        ("Anthropic", "https://api.anthropic.com", "Anthropic PBC", "https://www.anthropic.com"),
        ("阿里云通义", "https://dashscope.aliyuncs.com", "阿里巴巴", "https://tongyi.aliyun.com"),
        ("百度文心", "https://qianfan.baidubce.com", "百度", "https://wenxin.baidu.com"),
        ("腾讯混元", "https://hunyuan.tencentcloudapi.com", "腾讯", "https://hunyuan.tencent.com"),
        ("字节豆包", "https://ark.cn-beijing.volces.com", "字节跳动", "https://www.volcengine.com"),
        ("智谱 GLM", "https://open.bigmodel.cn", "智谱AI", "https://www.bigmodel.cn"),
        ("DeepSeek", "https://api.deepseek.com", "深度求索", "https://www.deepseek.com"),
    ]
    conn.executemany(
        "INSERT INTO server(plat_name, base_url, company, homepage) VALUES (?,?,?,?)",
        servers,
    )
    # 取刚插入的 id（顺序 1..8），直接用 plat_name 映射更稳健
    id_map = {r["plat_name"]: r["id"] for r in conn.execute("SELECT id, plat_name FROM server")}
    models = [
        (id_map["OpenAI"], "gpt-4o", 5, 15, "百万", "对话", "https://platform.openai.com"),
        (id_map["Anthropic"], "claude-3.5-sonnet", 3, 15, "百万", "对话", "https://www.anthropic.com/claude"),
        (id_map["阿里云通义"], "qwen-max", 1.2, 1.2, "百万", "对话", "https://tongyi.aliyun.com"),
        (id_map["百度文心"], "ernie-4.0", 8, 8, "百万", "对话", "https://wenxin.baidu.com"),
        (id_map["腾讯混元"], "hunyuan-pro", 6, 6, "百万", "对话", "https://hunyuan.tencent.com"),
        (id_map["字节豆包"], "doubao-pro", 0.8, 2, "百万", "对话", "https://www.volcengine.com"),
        (id_map["智谱 GLM"], "glm-4", 1, 1, "百万", "对话", "https://www.bigmodel.cn"),
        (id_map["DeepSeek"], "deepseek-v3", 0.5, 1.1, "百万", "对话", "https://www.deepseek.com"),
    ]
    conn.executemany(
        "INSERT INTO model(svc_id, model_name, in_token_fee, out_token_fee, unit, type, url) "
        "VALUES (?,?,?,?,?,?,?)",
        models,
    )


# ---------------- 服务 server ----------------
def get_servers():
    conn = get_conn()
    try:
        return conn.execute("SELECT * FROM server ORDER BY id").fetchall()
    finally:
        conn.close()


def get_server(sid):
    conn = get_conn()
    try:
        return conn.execute("SELECT * FROM server WHERE id=?", (sid,)).fetchone()
    finally:
        conn.close()


def search_servers(plat="", company=""):
    sql = "SELECT * FROM server WHERE 1=1"
    args = []
    if plat:
        sql += " AND plat_name LIKE ?"
        args.append(f"%{plat}%")
    if company:
        sql += " AND company LIKE ?"
        args.append(f"%{company}%")
    sql += " ORDER BY id"
    conn = get_conn()
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


def add_server(plat_name, base_url, company, homepage):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO server(plat_name, base_url, company, homepage) VALUES (?,?,?,?)",
            (plat_name, base_url, company, homepage),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_servers(ids):
    conn = get_conn()
    try:
        conn.executemany("DELETE FROM server WHERE id=?", [(i,) for i in ids])
        conn.commit()
    finally:
        conn.close()


# ---------------- 模型 model ----------------
def get_models():
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT m.*, s.plat_name FROM model m JOIN server s ON m.svc_id=s.id ORDER BY m.id"
        ).fetchall()
    finally:
        conn.close()


def get_model(mid):
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT m.*, s.plat_name FROM model m JOIN server s ON m.svc_id=s.id WHERE m.id=?",
            (mid,),
        ).fetchone()
    finally:
        conn.close()


def get_models_by_server(svc_id):
    conn = get_conn()
    try:
        return conn.execute("SELECT * FROM model WHERE svc_id=? ORDER BY id", (svc_id,)).fetchall()
    finally:
        conn.close()


def search_models(plat="", model_name="", mtype="", in_min=None, in_max=None, out_min=None, out_max=None):
    sql = ("SELECT m.*, s.plat_name FROM model m JOIN server s ON m.svc_id=s.id WHERE 1=1")
    args = []
    if plat:
        sql += " AND s.plat_name LIKE ?"
        args.append(f"%{plat}%")
    if model_name:
        sql += " AND m.model_name LIKE ?"
        args.append(f"%{model_name}%")
    if mtype:
        sql += " AND (m.type LIKE ? OR m.type=?)"
        args.append(f"%{mtype}%"); args.append(mtype)
    if in_min is not None:
        sql += " AND m.in_token_fee >= ?"; args.append(in_min)
    if in_max is not None:
        sql += " AND m.in_token_fee <= ?"; args.append(in_max)
    if out_min is not None:
        sql += " AND m.out_token_fee >= ?"; args.append(out_min)
    if out_max is not None:
        sql += " AND m.out_token_fee <= ?"; args.append(out_max)
    sql += " ORDER BY m.id"
    conn = get_conn()
    try:
        return conn.execute(sql, args).fetchall()
    finally:
        conn.close()


def add_model(svc_id, model_name, in_fee, out_fee, unit, mtype, url):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO model(svc_id, model_name, in_token_fee, out_token_fee, unit, type, url) "
            "VALUES (?,?,?,?,?,?,?)",
            (svc_id, model_name, in_fee, out_fee, unit, mtype, url),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def delete_models(ids):
    conn = get_conn()
    try:
        conn.executemany("DELETE FROM model WHERE id=?", [(i,) for i in ids])
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("DB initialized at", DB_PATH)
    print("servers:", len(get_servers()), "models:", len(get_models()))
