# frontend/chat_ui.py
import streamlit as st
import requests
import time

API_BASE = "http://127.0.0.1:8000"

st.title("💬 ChatGLM3-6B 云端聊天机器人")

# 初始化 session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# 登录页面
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["登录", "注册"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("用户名")
            password = st.text_input("密码", type="password")
            submit = st.form_submit_button("登录")
            if submit:
                resp = requests.post(f"{API_BASE}/token", data={
                    "username": username,
                    "password": password
                })
                if resp.status_code == 200:
                    st.session_state.token = resp.json()["access_token"]
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("登录失败")

    with tab2:
        with st.form("register_form"):
            reg_user = st.text_input("新用户名")
            reg_pass = st.text_input("新密码", type="password")
            submit_reg = st.form_submit_button("注册")
            if submit_reg:
                resp = requests.post(f"{API_BASE}/register", data={
                    "username": reg_user,
                    "password": reg_pass
                })
                if resp.status_code == 200:
                    st.success("注册成功，请登录")
                else:
                    st.error("注册失败")

else:
    # 已登录
    st.write(f"欢迎，{st.session_state.token.split('.')[1][:6]}...")

    # 显示历史
    if st.button("刷新历史"):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        resp = requests.get(f"{API_BASE}/history", headers=headers)
        if resp.status_code == 200:
            st.session_state.messages = [
                {"role": "user", "content": c['prompt']}
                for c in resp.json()
            ][::-1]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                resp = requests.post(f"{API_BASE}/chat", json={"prompt": prompt}, headers=headers)
                if resp.status_code == 200:
                    answer = resp.json()["response"]
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("请求失败")

    if st.button("退出登录"):
        st.session_state.logged_in = False
        st.session_state.token = ""
        st.session_state.messages = []
        st.rerun()
