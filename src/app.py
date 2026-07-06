import streamlit as st
from graph.game_graph import build_graph

st.set_page_config(page_title="Minimal LangGraph App", layout="centered")
st.title("Minimal LangGraph App")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "game_state" not in st.session_state:
    st.session_state.game_state = None

theme = st.text_input("Enter a theme", placeholder="haunted castle")

if st.button("Start Game"):
    initial_state = {
        "theme": theme,
        "message": ""
    }

    st.session_state.game_state = st.session_state.graph.invoke(initial_state)
    st.session_state.game_started = True

if st.session_state.game_started and st.session_state.game_state:
    st.subheader("Output")
    st.write(st.session_state.game_state["message"])

    st.subheader("Current State")
    st.json(st.session_state.game_state)

if st.button("Reset"):
    st.session_state.clear()
    st.rerun()