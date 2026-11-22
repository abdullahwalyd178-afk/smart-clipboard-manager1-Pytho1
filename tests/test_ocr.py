from smartclip.ocr import extract_text
def test_empty_and_invalid_images_are_safe():
    assert extract_text(b"")==""
    assert extract_text(b"not an image")==""
