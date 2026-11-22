from smartclip.storage import ClipboardStore
def test_text_and_empty(tmp_path):
    store=ClipboardStore(tmp_path/"clips.db")
    assert store.add_text("hello",100) is not None
    assert store.add_text("  ") is None
    assert store.list_clips()[0]["content"]=="hello"
def test_expiry_preserves_pinned(tmp_path):
    store=ClipboardStore(tmp_path/"clips.db",100)
    store.add_text("old",100); pinned=store.add_text("keep",100); store.set_pinned(pinned,True)
    assert store.cleanup(now=1000)==1
    assert [r["content"] for r in store.list_clips()]==["keep"]
def test_unpin_then_expire(tmp_path):
    store=ClipboardStore(tmp_path/"clips.db",100); item=store.add_text("temp",100)
    store.set_pinned(item,True); store.set_pinned(item,False)
    assert store.cleanup(now=1000)==1
    assert store.list_clips()==[]
def test_image_and_ocr_search(tmp_path):
    store=ClipboardStore(tmp_path/"clips.db"); item=store.add_image(b"image-bytes","integral x")
    assert store.get_clip(item)["image"]==b"image-bytes"
    assert len(store.list_clips("integral"))==1
def test_delete(tmp_path):
    store=ClipboardStore(tmp_path/"clips.db"); item=store.add_text("remove")
    assert store.delete(item) and store.get_clip(item) is None
