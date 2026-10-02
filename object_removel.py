import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import io
import requests
import numpy as np
from streamlit_drawable_canvas import st_canvas
from my_utils import initialize_session_state
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground
)

load_dotenv()
api_key = os.getenv("BRIA_API_KEY")


def download_image(url):
    try:
        return requests.get(url).content
    except:
        return None


def object_removel():
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

    st.title("🎨 Erase Elements")
    st.markdown("Upload an image and select the area you want to erase.")

    uploaded_file = st.file_uploader(
        "Upload Image", type=["png", "jpg", "jpeg"], key="erase_upload")

    if uploaded_file:
        # Load and resize image for canvas
        img = Image.open(uploaded_file)
        img_width, img_height = img.size
        max_width = 600
        max_height = 600
        aspect_ratio = img_width / img_height

        if img_width > img_height:
            canvas_width = min(img_width, max_width)
            canvas_height = int(canvas_width / aspect_ratio)
        else:
            canvas_height = min(img_height, max_height)
            canvas_width = int(canvas_height * aspect_ratio)

        img = img.resize((canvas_width, canvas_height))

        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Center the canvas with 3 columns layout
        left, center, right = st.columns([1, 2, 1])
        with center:
            stroke_width = st.slider(
                "Brush width", 1, 50, 20, key="erase_brush_width")
            stroke_color = st.color_picker(
                "Brush color", "#ffffff", key="erase_brush_color")

            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0.0)",  # Transparent fill
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="",
                background_image=img,
                drawing_mode="freedraw",
                height=canvas_height,
                width=canvas_width,
                key="erase_canvas",
            )

        st.markdown("---")

        content_moderation = st.checkbox(
            "Enable Content Moderation", False, key="erase_content_mod")

        if st.button("🎨 Erase Selected Area", key="erase_btn"):
            if canvas_result and canvas_result.image_data is not None:
                with st.spinner("Erasing selected area..."):
                    try:
                        # Convert canvas result to mask
                        mask_img = Image.fromarray(
                            canvas_result.image_data.astype('uint8'), mode='RGBA')
                        mask_img = mask_img.convert('L')

                        image_bytes = uploaded_file.getvalue()

                        result = erase_foreground(
                            api_key,
                            image_data=image_bytes,
                            content_moderation=content_moderation
                        )

                        if result and "result_url" in result:
                            st.session_state.edited_image = result["result_url"]
                            st.success("✨ Area erased successfully!")
                        else:
                            st.error(
                                "No result URL in the API response. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        if "422" in str(e):
                            st.warning(
                                "Content moderation failed. Please ensure the image is appropriate.")
            else:
                st.warning(
                    "Please draw on the image to select the area to erase.")

        # Show Original and Generated images side by side at bottom
        if st.session_state.get("edited_image") and uploaded_file:
            st.markdown("---")
            st.subheader("🖼️ Comparison")

            col1, col2 = st.columns(2)
            with col1:
                st.image(uploaded_file, caption="Original",
                         use_column_width=True)
            with col2:
                st.image(st.session_state.edited_image,
                         caption="Generated", use_column_width=True)

                image_data = download_image(st.session_state.edited_image)
                if image_data:
                    st.download_button("⬇️ Download", image_data,
                                       file_name="erased_image.png")


__all__ = ['object_removel']
