"""Test_Prompt —— Streamlit 应用（对应 HTML 原型功能）。

菜单：基础信息(服务器列表/添加服务器/模型列表/添加模型) + 提示词调试。
数据层见 db.py（SQLite：Prompt_Test_DB.db）。
"""
import streamlit as st
import db

st.set_page_config(page_title="Test_Prompt", layout="wide", page_icon="🅣")
db.init_db()

BRAND = "🅣 **Test_Prompt**"
PLAT_PRESETS = ["硅基流动", "OpenRouter", "魔搭社区", "OpenAI"]
MODEL_TYPES = ["对话", "视频", "嵌入", "生图", "语音", "重排"]


def brand():
    st.sidebar.markdown(BRAND)


def go(page, **params):
    for k, v in params.items():
        st.query_params[k] = str(v)
    st.switch_page(page)


# ---------------- 服务器列表 ----------------
def server_list():
    st.title("服务器列表")
    st.caption("基础信息 / 模型服务器")
    st.divider()

    with st.container():
        c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
        plat = c1.text_input("平台/官方名", key="s_plat")
        company = c2.text_input("公司名", key="s_company")
        search = c3.button("搜索", use_container_width=True)
        reset = c4.button("重置", use_container_width=True)

    if reset:
        st.query_params.clear()
        st.rerun()

    if search:
        rows = db.search_servers(plat, company)
    else:
        rows = db.get_servers()

    if not rows:
        st.info("没有符合条件的服务器。")
        return

    st.subheader(f"共 {len(rows)} 条")
    edited = st.data_editor(
        [{"选择": False, "平台/官方名": r["plat_name"], "公司名": r["company"],
          "api 接口(base_url)": r["base_url"], "id": r["id"]} for r in rows],
        column_config={"选择": st.column_config.CheckboxColumn("选择", width="small")},
        hide_index=True, use_container_width=True, key="s_editor", num_rows="fixed",
    )

    sel_ids = [r["id"] for r in edited if r["选择"]]
    ac1, ac2 = st.columns([1, 1])
    if ac2.button("➕ 添加服务器", use_container_width=True, type="primary"):
        go(server_add)
    if ac1.button("🗑 删除", use_container_width=True, disabled=not sel_ids,
                 type="tertiary"):
        if st.confirm(f"确定删除选中的 {len(sel_ids)} 个服务器吗？删除后其下模型也会一并删除。"):
            db.delete_servers(sel_ids)
            st.success("已删除。")
            st.rerun()

    # 平台名点击查看详情
    st.divider()
    st.caption("点击平台名查看详情：")
    for r in rows:
        if st.button(f"🔎 {r['plat_name']}", key=f"view_{r['id']}"):
            go(server_detail, id=r["id"])


# ---------------- 添加服务器 ----------------
def server_add():
    st.title("添加服务器")
    st.caption("基础信息 / 模型服务器")
    st.divider()

    preset = st.selectbox("常用平台（选填，点击填入下方）", [""] + PLAT_PRESETS)
    if preset:
        st.session_state.sa_plat = preset

    with st.form("add_server_form"):
        plat_name = st.text_input("平台/官方名 *", value=st.session_state.get("sa_plat", ""))
        base_url = st.text_input("api 网址 (base_url) *")
        company = st.text_input("公司名 *")
        homepage = st.text_input("首页")
        submitted = st.form_submit_button("保存", type="primary")
        cancelled = st.form_submit_button("取消")
        if cancelled:
            go(server_list)
        if submitted:
            if not (plat_name and base_url and company):
                st.error("平台/官方名、api 网址、公司名为必填项。")
            else:
                db.add_server(plat_name, base_url, company, homepage)
                st.success("保存成功！")
                st.balloons()
                go(server_list)


# ---------------- 模型列表 ----------------
def model_list():
    st.title("模型列表")
    st.caption("基础信息 / 模型")
    st.divider()

    with st.container():
        r1 = st.columns([2, 2, 2, 1.2, 1.2])
        plat = r1[0].text_input("平台/官方名", key="m_plat")
        mtype = r1[1].text_input("类型", key="m_type")
        mname = r1[2].text_input("模型名", key="m_name")
        in_min = r1[3].number_input("输入费≥", min_value=0.0, value=None, step=0.1, format="%.4f", key="in_min")
        in_max = r1[4].number_input("输入费≤", min_value=0.0, value=None, step=0.1, format="%.4f", key="in_max")
        r2 = st.columns([1.2, 1.2, 1, 1])
        out_min = r2[0].number_input("输出费≥", min_value=0.0, value=None, step=0.1, format="%.4f", key="out_min")
        out_max = r2[1].number_input("输出费≤", min_value=0.0, value=None, step=0.1, format="%.4f", key="out_max")
        search = r2[2].button("搜索", use_container_width=True)
        reset = r2[3].button("重置", use_container_width=True)

    if reset:
        st.query_params.clear()
        st.rerun()

    if search:
        rows = db.search_models(plat, mname, mtype, in_min, in_max, out_min, out_max)
    else:
        rows = db.get_models()

    if not rows:
        st.info("没有符合条件的模型。")
        return

    st.subheader(f"共 {len(rows)} 条")
    edited = st.data_editor(
        [{"选择": False, "平台/官方名": r["plat_name"], "模型名": r["model_name"],
          "类型": r["type"], "输入token费用": f"¥{r['in_token_fee']}/{r['unit']}",
          "输出token费用": f"¥{r['out_token_fee']}/{r['unit']}", "id": r["id"]} for r in rows],
        column_config={"选择": st.column_config.CheckboxColumn("选择", width="small")},
        hide_index=True, use_container_width=True, key="m_editor", num_rows="fixed",
    )

    sel_ids = [r["id"] for r in edited if r["选择"]]
    ac1, ac2 = st.columns([1, 1])
    if ac2.button("➕ 添加模型", use_container_width=True, type="primary"):
        go(model_add)
    if ac1.button("🗑 删除", use_container_width=True, disabled=not sel_ids, type="tertiary"):
        if st.confirm(f"确定删除选中的 {len(sel_ids)} 个模型吗？"):
            db.delete_models(sel_ids)
            st.success("已删除。")
            st.rerun()


# ---------------- 添加模型 ----------------
def model_add():
    st.title("添加模型")
    st.caption("基础信息 / 模型")
    st.divider()

    servers = db.get_servers()
    svc_map = {f"{s['plat_name']}": s["id"] for s in servers}

    with st.form("add_model_form"):
        svc = st.selectbox("服务器 *", list(svc_map.keys()))
        model_name = st.text_input("模型名 *")
        col1, col2 = st.columns(2)
        in_fee = col1.number_input("输入 token 计费 *", min_value=0.0, step=0.0001, format="%.4f")
        out_fee = col2.number_input("输出 token 计费 *", min_value=0.0, step=0.0001, format="%.4f")
        unit = st.selectbox("单位 *", ["K", "万", "十万", "百万"])
        mtype = st.multiselect("类型", MODEL_TYPES)
        url = st.text_input("网址")
        submitted = st.form_submit_button("保存", type="primary")
        cancelled = st.form_submit_button("取消")
        if cancelled:
            go(model_list)
        if submitted:
            if not model_name:
                st.error("模型名为必填项。")
            else:
                db.add_model(svc_map[svc], model_name, in_fee, out_fee, unit,
                             ",".join(mtype), url)
                st.success("保存成功！")
                st.balloons()
                go(model_list)


# ---------------- 服务器详情 ----------------
def server_detail():
    sid = st.query_params.get("id")
    if isinstance(sid, list):
        sid = sid[0] if sid else None
    if not sid:
        st.warning("缺少 id 参数。")
        return
    s = db.get_server(int(sid))
    if not s:
        st.error("未找到该服务器。")
        return
    st.title(s["plat_name"])
    st.caption("服务器详情")
    st.divider()
    st.markdown(f"**公司名：** {s['company']}")
    st.markdown(f"**api 网址：** `{s['base_url']}`")
    st.markdown(f"**首页：** {s['homepage'] or '—'}")
    st.subheader("该服务下的模型")
    models = db.get_models_by_server(s["id"])
    if models:
        st.dataframe(
            [{"模型名": m["model_name"], "类型": m["type"],
              "输入token费用": f"¥{m['in_token_fee']}/{m['unit']}",
              "输出token费用": f"¥{m['out_token_fee']}/{m['unit']}"} for m in models],
            hide_index=True, use_container_width=True,
        )
    else:
        st.info("该服务下暂无模型。")
    if st.button("← 返回服务器列表"):
        go(server_list)


# ---------------- 提示词调试 ----------------
def debug():
    st.title("提示词调试")
    st.caption("基础信息 / 提示词调试")
    st.divider()

    servers = db.get_servers()
    models = db.get_models()
    svc_map = {f"{s['plat_name']}": s for s in servers}
    model_map = {f"{m['model_name']}（{m['plat_name']}）": m for m in models}

    lc, rc = st.columns(2)

    with lc:
        st.subheader("配置与输入")
        svc_name = st.selectbox("服务器 *", list(svc_map.keys()))
        base_url = svc_map[svc_name]["base_url"]
        st.text_input("Base_url", value=base_url, disabled=True)
        api_key = st.text_input("api_key *", type="password")
        mdl_name = st.selectbox("模型 *", list(model_map.keys()))
        m = model_map[mdl_name]
        st.caption(f"输入 token 费用：¥{m['in_token_fee']}/{m['unit']}　"
                   f"输出 token 费用：¥{m['out_token_fee']}/{m['unit']}")

        sys_p = st.text_area("系统提示词 *", height=150)
        user1 = st.text_area("用户提示词（第 1 轮） *", height=70)

        if "rounds" not in st.session_state:
            st.session_state.rounds = []
        multi = st.checkbox("多轮会话")
        if multi:
            for i, _ in enumerate(st.session_state.rounds):
                cols = st.columns([5, 1])
                st.session_state.rounds[i] = cols[0].text_area(
                    f"第 {i+2} 轮 · 用户提示词", value=st.session_state.rounds[i], height=60,
                    key=f"round_{i}")
                if cols[1].button("删除", key=f"del_{i}"):
                    st.session_state.rounds.pop(i)
                    st.rerun()
            if st.button("➕ 添加下一轮"):
                st.session_state.rounds.append("")
                st.rerun()

        run = st.button("调试", type="primary")
        if st.button("重置"):
            st.session_state.rounds = []
            st.rerun()

    with rc:
        st.subheader("输出与费用")
        if run:
            if not (svc_name and api_key and mdl_name):
                st.error("请填写服务器、api_key、模型。")
            elif not sys_p.strip():
                st.error("请输入系统提示词。")
            elif not user1.strip():
                st.error("请输入第 1 轮用户提示词。")
            else:
                turns = [user1] + [t for t in st.session_state.rounds if t.strip()]
                all_text = "\n".join([sys_p] + turns)
                in_tokens = max(1, (len(all_text) + 1) // 2)
                # 模拟输出
                reply = (f"【{m['model_name']} 模拟回复】\n\n"
                         f"针对您的问题，这是一个原型模拟输出，用于演示调试流程与费用估算。\n"
                         f"实际应用中此处会返回模型基于「系统提示词 + 多轮上下文」生成的真实回复。")
                out_tokens = max(1, (len(reply) + 1) // 2)

                in_fee = in_tokens / 1e6 * m["in_token_fee"]
                out_fee = out_tokens / 1e6 * m["out_token_fee"]
                total = in_fee + out_fee
                st.session_state.debug_out = reply
                st.session_state.debug_metrics = (in_tokens, out_tokens, in_fee, out_fee, total)

        if "debug_out" in st.session_state:
            st.text_area("模型输出", value=st.session_state.debug_out, height=220,
                         help="点右上角可复制")
            if "debug_metrics" in st.session_state:
                it, ot, inf, outf, tot = st.session_state.debug_metrics
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("输入 token 费", f"¥{inf:.4f}", f"{it} tokens")
                mc2.metric("输出 token 费", f"¥{outf:.4f}", f"{ot} tokens")
                mc3.metric("总费", f"¥{tot:.4f}", f"{it+ot} tokens")
            st.caption("（原型模拟：按字符数估算 token，未发起真实 API 请求）")


# ---------------- 路由 ----------------
brand()
pg = st.navigation({
    "基础信息": [
        st.Page(server_list, title="服务器列表", icon="🖥️", default=True),
        st.Page(server_add, title="添加服务器", icon="➕"),
        st.Page(model_list, title="模型列表", icon="🧩"),
        st.Page(model_add, title="添加模型", icon="➕"),
        st.Page(server_detail, title="服务器详情", icon="🔎"),
    ],
    "提示词调试": [
        st.Page(debug, title="提示词调试", icon="💬"),
    ],
})
pg.run()
