import streamlit as st
import requests

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


def hd_generate_images():
    initialize_session_state()
    st.markdown("""
        <style>
            body {
                background-image: radial-gradient(ellipse 40% 100% at 60% -10%, rgba(119, 138, 232, 0.3), rgba(119, 138, 232, 0));
                background-color: #0a0f20;
                color: white;
            }
            [data-testid="stAppViewContainer"] {
                background-image: radial-gradient(ellipse 40% 100% at 60% -10%, rgba(119, 138, 232, 0.3), rgba(119, 138, 232, 0));
                background-color: #0a0f20;
            }
            textarea, select, input {
                color: white;
                background-color: #1a1a2e;
                border: 1px solid #3a3a5c;
                border-radius: 5px;
            }
            div.stButton > button {
                background-color: rgba(255, 255, 255, 0.45);
                border: none;
                padding: 0.5rem 1.5rem;
                border-radius: 12px;
                color: #1a1a1a;
                font-weight: 600;
                transition: 0.3s ease-in-out;
                margin-bottom: 8px; /* small margin between stacked buttons */
                width: 100%;
            }
            div.stButton > button:hover {
                background-color: rgba(255, 255, 255, 0.65);
                transform: scale(1.03);
            }
            .block-container {
                padding-top: 30px !important;
                padding-bottom: 30px !important;
            }

            /* Glassmorphism + animated glowing border for placeholder */
            .glass-placeholder {
                height: 500px;
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                box-shadow:
                    0 0 8px 2px rgba(119, 138, 232, 0.7),
                    0 0 15px 5px rgba(119, 138, 232, 0.4);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: #a9b0ff;
                font-style: italic;
                text-align: center;
                padding: 20px;
                position: relative;
                animation: glow 3s ease-in-out infinite alternate;
                user-select: none;
            }

            @keyframes glow {
                0% {
                    box-shadow:
                        0 0 8px 2px rgba(119, 138, 232, 0.7),
                        0 0 15px 5px rgba(119, 138, 232, 0.4);
                }
                100% {
                    box-shadow:
                        0 0 15px 5px rgba(119, 138, 232, 1),
                        0 0 25px 8px rgba(119, 138, 232, 0.6);
                }
            }

            .glass-placeholder p.title {
                font-size: 1.6rem;
                margin: 0 0 10px 0;
            }
            .glass-placeholder p.subtitle {
                font-size: 1rem;
                font-style: normal;
                color: #d0d4ffcc;
                max-width: 320px;
            }
        </style>
        """, unsafe_allow_html=True)

    st.header("Generate Images")

    # Increase gap between columns here
    col1, col3 = st.columns([4, 5], gap='medium')

    with col1:
        prompt = st.text_area("Enter your prompt", value="",
                              height=50, key="prompt_input")

        # Track original prompt changes
        if "original_prompt" not in st.session_state:
            st.session_state.original_prompt = prompt
        elif prompt != st.session_state.original_prompt:
            st.session_state.original_prompt = prompt
            st.session_state.enhanced_prompt = None

        if st.session_state.get('enhanced_prompt'):
            st.markdown("**Enhanced Prompt:**")
            st.markdown(f"*{st.session_state.enhanced_prompt}*")

        # Options placed here above buttons
        st.subheader("Options")

        aspect_ratio = st.selectbox(
            "Aspect ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])

        enhance_img = st.checkbox("Enhance image quality", value=True)

        st.subheader("Style Options")
        style = st.selectbox("Image Style", [
            "Realistic", "Artistic", "Cartoon", "Sketch",
            "Watercolor", "Oil Painting", "Digital Art"
        ])

        if style and style != "Realistic":
            prompt = f"{prompt}, in {style.lower()} style"

        # Buttons stacked vertically with small spacing
        enhance_clicked = st.button("✨ Enhance Prompt", key="enhance_button")
        generate_clicked = st.button("🎨 Generate Images", type="primary")

        if enhance_clicked:
            if not prompt:
                st.warning("Please enter a prompt to enhance.")
            else:
                with st.spinner("Enhancing prompt..."):
                    try:
                        result = enhance_prompt(
                            st.session_state.api_key, prompt)
                        if result:
                            st.session_state.enhanced_prompt = result
                            st.success("Prompt enhanced!")
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error enhancing prompt: {str(e)}")

    if generate_clicked:
        if not st.session_state.api_key:
            st.error("Please enter your API key in the sidebar.")
            return

        with st.spinner("🎨 Generating your masterpiece..."):
            try:
                result = generate_hd_image(
                    prompt=st.session_state.enhanced_prompt or prompt,
                    api_key=st.session_state.api_key,
                    num_results=1,
                    aspect_ratio=aspect_ratio,
                    sync=True,
                    enhance_image=enhance_img,
                    medium="art" if style != "Realistic" else "photography",
                    prompt_enhancement=False,
                    content_moderation=True
                )

                if result:
                    if isinstance(result, dict):
                        urls = []
                        if "result_url" in result:
                            urls = [result["result_url"]]
                        elif "result_urls" in result:
                            urls = result["result_urls"]
                        elif "result" in result and isinstance(result["result"], list):
                            for item in result["result"]:
                                if isinstance(item, dict) and "urls" in item:
                                    urls = item["urls"]
                                    break
                                elif isinstance(item, list) and len(item) > 0:
                                    urls = item
                                    break
                        if urls:
                            st.session_state.edited_images = urls  # Save all image URLs
                            st.success("✨ Images generated successfully!")
                        else:
                            st.error(
                                "No valid image URL found in API response.")
                    else:
                        st.error("Unexpected API response format.")

            except Exception as e:
                st.error(f"Error generating images: {str(e)}")

    with col3:
        if st.session_state.get("edited_images"):
            st.subheader("🖼️ Generated Images")

            for i, img_url in enumerate(st.session_state.edited_images):
                aspect_map = {
                    "1:1": (400, 400),
                    "16:9": (480, 270),
                    "9:16": (270, 480),
                    "4:3": (400, 300),
                    "3:4": (300, 400)
                }

                img_width, img_height = aspect_map.get(
                    aspect_ratio, (400, 400))

                st.image(
                    img_url, caption=f"Image {i+1}",
                    width=img_width
                )

                try:
                    img_bytes = requests.get(img_url).content

                    st.download_button(
                        label=f"📥 Download Image {i+1}",
                        data=img_bytes,
                        file_name=f"generated_image_{i+1}.jpg",
                        mime="image/jpeg"
                    )

                except Exception as e:
                    st.warning(f"Couldn't load/download image {i+1}: {str(e)}")

        else:
            st.markdown(
                """
                <div class="glass-placeholder">
                    <p class="title">📷 Images will appear here</p>
                    <p class="subtitle">Transform ideas into visual masterpieces with ImagiCraft Studio</p>
                </div>
                """,
                unsafe_allow_html=True
            )


__all__ = ['hd_generate_images']
