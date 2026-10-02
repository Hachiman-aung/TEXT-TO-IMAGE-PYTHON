from generative_fill import generative_fill_ui
from generate_image import hd_generate_images
from object_removel import object_removel
from life_style import real_life
import os
from PIL import Image
import base64
import streamlit as st

st.set_page_config(page_title="ImagiCraft Studio", layout="wide")

# ---------------------- Main App ----------------------


def main():
    if "active_section" not in st.session_state:
        st.session_state.active_section = "Home"

    if st.session_state.active_section != "Home":
        show_navbar()

    if st.session_state.active_section == "Home":
        show_home()
    elif st.session_state.active_section == "Generate":
        show_generate_images()
    elif st.session_state.active_section == "Edit":
        show_edit_product()
    elif st.session_state.active_section == "Lifestyle":
        show_lifestyle_shots()
    elif st.session_state.active_section == "remove":
        show_photo_enhancer()

# ---------------------- Navbar ----------------------


def show_navbar():
    st.markdown("""
    <style>
    .navbar {
        background-color: #f0f2f6;
        padding: 0.2rem 0.3rem;
        margin-bottom: 0.2rem;
        border-radius: 4px;
        text-align: center;
    }
    .navbar button {
        background-color: #ffffff;
        border: 1px solid #ddd;
        padding: 0.2rem 0.4rem;
        margin: 0.1rem 0.1rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .navbar button:hover {
        background-color: #e6e6e6;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    nav1, nav2, nav3, nav4, nav5 = st.columns(5)

    with nav1:
        if st.button("🧠 Generate", use_container_width=True):
            st.session_state.active_section = "Generate"
            st.rerun()
    with nav2:
        if st.button("🛠️ Edit", use_container_width=True):
            st.session_state.active_section = "Edit"
            st.rerun()
    with nav3:
        if st.button("🌿 Lifestyle", use_container_width=True):
            st.session_state.active_section = "Lifestyle"
            st.rerun()
    with nav4:
        if st.button("✨ Object Remover", use_container_width=True):
            st.session_state.active_section = "remove"
            st.rerun()
    with nav5:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.active_section = "Home"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------- Home Page ----------------------


def show_home():
    st.markdown("""
        <style>
            body {
                background-image: radial-gradient(ellipse 40% 100% at 60% -10%, rgba(119, 138, 232, 0.3), rgba(119, 138, 232, 0));
                background-color: #0a0f20;
            }

            [data-testid="stAppViewContainer"] {
                background-image: radial-gradient(ellipse 40% 100% at 60% -10%, rgba(119, 138, 232, 0.3), rgba(119, 138, 232, 0));
                background-color: #0a0f20;
            }

            .desc-box {
                height: 180px;
                padding: 1rem;
                margin-top: 0.5rem;
                border-radius: 20px;
                font-size: 1.2rem;
                text-align: center;
                color: white;
                position: relative;
                overflow: hidden;
                animation: fadeIn 1s ease-in-out;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                border: 1px solid rgba(255, 255, 255, 0.18);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                background: rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .desc-box:hover {
                transform: translateY(-6px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
                background: rgba(255, 255, 255, 0.15);
            }

            .desc-box::before {
                content: "";
                position: absolute;
                top: -3px;
                left: -3px;
                right: -3px;
                bottom: -3px;
                border-radius: 24px;
                background: linear-gradient(270deg, #ff4d4d, #4d88ff, #33cc99, #cc66ff, #ff4d4d);
                background-size: 1000% 1000%;
                animation: gradientShift 10s ease infinite;
                z-index: -1;
                filter: blur(10px);
                opacity: 0.7;
            }

            .tagline {
                font-size: 2.1rem;
                color: white;
                margin-top: 40px;
                font-weight: 700;
                background: linear-gradient(to right, #005c97, #363795);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
            }

            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes fadeIn {
                from {opacity: 0; transform: translateY(10px);}
                to {opacity: 1; transform: translateY(0);}
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏠 Welcome to ImagiCraft Studio")
    st.markdown("### Choose a feature to get started")

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        if st.button("🧠 Generate Images", key="gen", use_container_width=True):
            st.session_state.active_section = "Generate"
            st.rerun()
        st.markdown(
            '<div class="desc-box">Create AI-generated images from your creative prompts.</div>',
            unsafe_allow_html=True
        )

    with col2:
        if st.button("🛠️ Edit Product", key="edit", use_container_width=True):
            st.session_state.active_section = "Edit"
            st.rerun()
        st.markdown(
            '<div class="desc-box">Fine-tune your product images easily with editing tools.</div>',
            unsafe_allow_html=True
        )

    with col3:
        if st.button("🌿 Lifestyle Shots", key="life", use_container_width=True):
            st.session_state.active_section = "Lifestyle"
            st.rerun()
        st.markdown(
            '<div class="desc-box">Blend your product into stunning lifestyle backgrounds.</div>',
            unsafe_allow_html=True
        )

    with col4:
        if st.button("✨ Object Remover", key="remove", use_container_width=True):
            st.session_state.active_section = "remove"
            st.rerun()
        st.markdown(
            '<div class="desc-box">Enhance your image quality with AI-powered upgrades.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="tagline">Transform ideas into visual masterpieces with ImagiCraft Studio</div>',
                unsafe_allow_html=True)

# ---------------------- Section Pages ----------------------


def show_generate_images():
    hd_generate_images()


def show_edit_product():
    generative_fill_ui()


def show_lifestyle_shots():
    real_life()


def show_photo_enhancer():
    object_removel()

# ---------------------- Run App ----------------------


if __name__ == "__main__":
    main()
