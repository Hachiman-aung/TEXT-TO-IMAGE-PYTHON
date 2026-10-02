import streamlit as st
import os
from dotenv import load_dotenv
from services import generative_fill
from PIL import Image
import io
import requests
import numpy as np
from streamlit_drawable_canvas import st_canvas

load_dotenv()
api_key = os.getenv("BRIA_API_KEY")


def initialize_session_state():
    for key in ['edited_image', 'generated_images', 'pending_urls']:
        if key not in st.session_state:
            st.session_state[key] = [] if "list" in key else None


def download_image(url):
    try:
        return requests.get(url).content
    except:
        return None


def check_generated_images():
    ready, pending = [], []
    for url in st.session_state.pending_urls:
        if requests.head(url).status_code == 200:
            ready.append(url)
        else:
            pending.append(url)
    st.session_state.pending_urls = pending
    if ready:
        st.session_state.edited_image = ready[0]
        return True
    return False


def generative_fill_ui():
    initialize_session_state()

    # ---- STYLES ----
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        color: white;
        background-color: #0a0f20;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #0a0f20;
    }

    label, input, textarea, .stTextInput > div > div > input {
        color: white !important;
    }

    div.stButton > button {
        background-color: rgba(255, 255, 255, 0.45);
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 12px;
        color: #1a1a1a;
        font-weight: 600;
        transition: 0.3s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.65);
        transform: scale(1.03);
    }

    .block-container {
        padding-top: 30px !important;
        padding-bottom: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📤 Upload & Draw")

    uploaded_file = st.file_uploader(
        "Upload image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        img = img.resize((min(img.width, 480), int(
            min(img.width, 480) * img.height / img.width)))

        stroke_width = st.slider("🖌️ Brush Size", 1, 50, 20)
        stroke_color = st.color_picker("🎯 Brush Color", "#FFFFFF")

        # Use 3-column layout to center the canvas
        left, center, right = st.columns([1, 2, 1])
        with center:
            canvas = st_canvas(
                fill_color="rgba(255,255,255,0.3)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_image=img,
                height=img.height,
                width=img.width,
                drawing_mode="freedraw",
                key="canvas"
            )

    st.markdown("---")
    st.subheader("✨ Prompt")

    prompt = st.text_input("Describe your image")
    negative_prompt = st.text_input("What to avoid? (optional)")

    col1, col2 = st.columns(2)
    with col1:
        sync_mode = st.checkbox("Sync Mode", False)
    with col2:
        seed = st.number_input("Seed (optional)", value=0)
        content_mod = st.checkbox("Moderation", False)

    if st.button("🚀 Generate"):
        if not prompt or canvas.image_data is None:
            st.error("Please enter a prompt and draw a mask.")
            return

        mask_img = Image.fromarray(
            canvas.image_data.astype('uint8')).convert('L')
        mask_io = io.BytesIO()
        mask_img.save(mask_io, format="PNG")
        image_bytes = uploaded_file.getvalue()
        mask_bytes = mask_io.getvalue()

        with st.spinner("🧠 AI generating..."):
            result = generative_fill(
                api_key, image_bytes, mask_bytes,
                prompt,
                negative_prompt=negative_prompt or None,
                num_results=1,
                sync=sync_mode,
                seed=seed if seed > 0 else None,
                content_moderation=content_mod
            )
            if result:
                urls = result.get("urls") or [result.get("result_url")]
                if sync_mode:
                    st.session_state.edited_image = urls[0]
                    st.session_state.generated_images = urls
                    st.success("✅ Done!")
                else:
                    st.session_state.pending_urls = urls
                    if check_generated_images():
                        st.rerun()

    if st.session_state.edited_image and uploaded_file:
        st.markdown("---")
        st.subheader("🖼️ Comparison")

        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption="Original", use_column_width=True)
        with col2:
            st.image(st.session_state.edited_image,
                     caption="Generated", use_column_width=True)

            image_data = download_image(st.session_state.edited_image)
            if image_data:
                st.download_button("⬇️ Download", image_data,
                                   file_name="generated_image.png")


__all__ = ['generative_fill_ui']
