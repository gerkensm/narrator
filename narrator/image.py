import asyncio
import io
import base64
import magic
from PIL import ImageGrab
from cv2 import VideoCapture, imencode

async def capture_screen() -> io.BytesIO:
    """
    Capture the current screen and return it as a BytesIO object.

    Returns:
        io.BytesIO: The captured screen image as a BytesIO object.
    """
    img = ImageGrab.grab()
    img_byte_io = io.BytesIO()
    img.convert("RGB").save(img_byte_io, format='PNG')
    img_byte_io.flush()
    img_byte_io.seek(0)
    return img_byte_io

async def capture_cam() -> io.BytesIO:
    """
    Capture an image from the default camera and return it as a BytesIO object.

    Returns:
        io.BytesIO: The captured camera image as a BytesIO object.
    """
    cam = VideoCapture(0)
    for _ in range(3):
        cam.read()
        await asyncio.sleep(0.3)
    success, img = cam.read()
    if success:
        is_success, buffer = imencode(".jpg", img)
        io_buf = io.BytesIO(buffer)
        if is_success:
            io_buf.flush()
            io_buf.seek(0)
            return io_buf
    raise Exception("Could not capture camera image")

def image_to_base64(image_buffer_io: io.BytesIO) -> str:
    """
    Convert an image buffer to a base64-encoded string.

    Args:
        image_buffer_io (io.BytesIO): The input image buffer.

    Returns:
        str: The base64-encoded image string.
    """
    image_buffer_io.seek(0)
    mime_type = magic.from_buffer(image_buffer_io.getvalue(), mime=True)
    if not mime_type or not mime_type.startswith('image'):
        raise ValueError("The file type is not recognized as an image")
    image_buffer_io.seek(0)
    encoded_string = base64.b64encode(image_buffer_io.getvalue()).decode('utf-8')
    image_base64 = f"data:{mime_type};base64,{encoded_string}"
    return image_base64