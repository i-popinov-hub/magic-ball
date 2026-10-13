"""🔮 Магический шар — тестовое Streamlit-приложение.

Задайте вопрос, нажмите кнопку — шар ответит.
Открывается с телефона по QR-коду (см. сайдбар и README.md).
"""

from __future__ import annotations

import time
from io import BytesIO

import qrcode
import streamlit as st

from game import ANSWERS, is_valid_question, pick_answer

# Адрес, на который указывает QR-код. Впишите сюда адрес после деплоя,
# либо просто вставьте ссылку в сайдбаре при запущенном приложении.
PUBLIC_URL = ""

THINKING_FRAMES = ("🔮", "🔮 ✨", "✨ 🔮 ✨", "🔮 ✨", "🔮")

st.set_page_config(
    page_title="Магический шар",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 2rem; max-width: 46rem; }
      .ball-answer {
          margin: 1.2rem 0 0.4rem 0;
          padding: 1.4rem 1.2rem;
          border-radius: 1rem;
          background: radial-gradient(circle at 30% 20%, #4a2f7a 0%, #1b1030 70%);
          color: #f5f0ff;
          font-size: 1.6rem;
          font-weight: 700;
          line-height: 1.3;
          text-align: center;
          box-shadow: 0 0 0 1px #6d4fc4 inset, 0 12px 30px rgba(74, 47, 122, .35);
      }
      .ball-question { text-align: center; color: #9b8ec4; font-size: 1rem; }
      .ball-thinking { text-align: center; font-size: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def qr_png(url: str) -> bytes:
    """PNG с QR-кодом для ссылки (кэшируется, чтобы не перерисовывать)."""
    image = qrcode.make(url, box_size=8, border=2)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def ask_the_ball(question: str) -> None:
    """Показать анимацию «раздумий» и записать ответ в историю сессии."""
    previous = st.session_state.history[-1]["answer"] if st.session_state.history else None
    answer = pick_answer(question, previous=previous)

    placeholder = st.empty()
    for frame in THINKING_FRAMES:
        placeholder.markdown(f"<div class='ball-thinking'>{frame}</div>", unsafe_allow_html=True)
        time.sleep(0.28)
    placeholder.empty()

    st.session_state.history.append({"question": question, "answer": answer})
    st.session_state.last = {"question": question, "answer": answer}


if "history" not in st.session_state:
    st.session_state.history = []
if "last" not in st.session_state:
    st.session_state.last = None

# ---------------------------------------------------------------- сайдбар ---
with st.sidebar:
    st.header("📱 Открыть на телефоне")
    st.caption("Наведите камеру телефона на QR-код — приложение откроется в браузере.")

    url = st.text_input(
        "Адрес приложения",
        value=PUBLIC_URL,
        placeholder="https://your-app.streamlit.app",
        help="Вставьте адрес из Streamlit Community Cloud (или любой другой публичный адрес).",
    ).strip()

    if url:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        st.image(qr_png(url), caption=url)
    else:
        st.info("Пока адрес не указан — QR-код появится здесь.")

    st.divider()
    if st.button("🧹 Очистить историю", use_container_width=True):
        st.session_state.history = []
        st.session_state.last = None
        st.rerun()

# ------------------------------------------------------------------- шапка ---
st.title("🔮 Магический шар")
st.write("Спросите что-нибудь — и шар ответит. Ответы не стоит воспринимать всерьёз 🙂")

with st.form("ask", clear_on_submit=False):
    question = st.text_input(
        "Ваш вопрос",
        placeholder="Например: стоит ли мне сегодня деплоить?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Спросить шар", use_container_width=True, type="primary")

# ------------------------------------------------------------------- ответ ---
if submitted:
    if not is_valid_question(question):
        st.warning("Сначала задайте вопрос — шар не читает мысли (пока).")
    else:
        ask_the_ball(question.strip())

if st.session_state.last:
    st.markdown(
        f"<div class='ball-question'>Вопрос: {st.session_state.last['question']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='ball-answer'>{st.session_state.last['answer']}</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------- история ---
if st.session_state.history:
    remaining = st.session_state.history[:-1]
    if remaining:
        with st.expander(f"История ответов ({len(remaining)})"):
            for item in reversed(remaining):
                st.markdown(f"**{item['question']}**  \n{item['answer']}")
                st.divider()

st.caption(f"В колоде шара {len(ANSWERS)} ответов. Сделано на Streamlit.")
