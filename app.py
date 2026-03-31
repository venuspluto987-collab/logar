import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from streamlit_drawable_canvas import st_canvas
import io

st.set_page_config(layout="wide")

st.title("🖌️ AI Photoshop Dashboard")

# ---------- SIDEBAR ----------
st.sidebar.title("🛠️ Tools")
tool = st.sidebar.radio(
    "Choose Tool",
    ["Enhancer", "Background Changer", "Draw Eraser"]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Image", type=["png", "jpg", "jpeg"]
)

# ---------- MAIN ----------
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Original Image", use_container_width=True)

    # =========================
    # ✨ ENHANCER
    # =========================
    if tool == "Enhancer":
        st.subheader("✨ Image Enhancer")

        brightness = st.slider("Brightness", 0.5, 2.0, 1.0)
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0)
        sharpness = st.slider("Sharpness", 0.5, 3.0, 1.0)

        img = ImageEnhance.Brightness(image).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Sharpness(img).enhance(sharpness)

        st.image(img, caption="Enhanced Image", use_container_width=True)

    # =========================
    # 🎨 BACKGROUND CHANGER
    # =========================
    elif tool == "Background Changer":
        st.subheader("🎨 Background Changer")

        bg_color = st.color_picker("Pick Background Color", "#00ff00")

        img_np = np.array(image)

        # Detect light pixels (basic background detection)
        mask = np.mean(img_np, axis=2) > 200

        new_bg = np.zeros_like(img_np)
        color = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
        new_bg[:] = color

        result = img_np.copy()
        result[mask] = new_bg[mask]

        st.image(result, caption="Background Changed", use_container_width=True)

    # =========================
    # 🧽 DRAW ERASER (FIXED)
    # =========================
    elif tool == "Draw Eraser":
        st.subheader("🧽 Draw to Erase (Blur Effect)")

        brush_size = st.slider("Brush Size", 5, 50, 20)

        # ✅ FIX: Convert image to BytesIO (prevents Streamlit error)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=brush_size,
            stroke_color="rgba(255,0,0,1)",
            background_image=Image.open(img_bytes),  # ✅ FIXED
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="freedraw",
            key="canvas",
        )

        if canvas_result.image_data is not None:
            mask = canvas_result.image_data

            # Convert mask to grayscale
            mask_gray = np.mean(mask[:, :, :3], axis=2)

            # Detect drawn region
            mask_binary = mask_gray > 50

            img_np = np.array(image)

            # Create blurred version
            blurred = np.array(image.filter(ImageFilter.GaussianBlur(15)))

            # Apply blur only where drawn
            img_np[mask_binary] = blurred[mask_binary]

            st.subheader("✅ Edited Image")
            st.image(img_np, use_container_width=True)

else:
    st.info("👈 Upload an image from sidebar to start editing")