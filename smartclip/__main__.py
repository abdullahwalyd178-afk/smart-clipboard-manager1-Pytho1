import argparse,threading
def main():
    parser=argparse.ArgumentParser(description="Smart Clipboard Manager")
    parser.add_argument("--startup",action="store_true"); parser.add_argument("--remove-startup",action="store_true")
    args=parser.parse_args()
    if args.startup or args.remove_startup:
        from .startup import set_startup
        set_startup(args.startup); print("Startup setting updated."); return
    from .config import database_path,RETENTION_SECONDS
    from .storage import ClipboardStore
    from .monitor import ClipboardMonitor
    from .ui import HistoryWindow
    store=ClipboardStore(database_path(),RETENTION_SECONDS); store.cleanup()
    cleanup_stop=threading.Event()
    def cleanup_loop():
        while not cleanup_stop.wait(600):
            try: store.cleanup()
            except Exception as exc: print(f"Cleanup failed: {exc}")
    cleanup_thread=threading.Thread(target=cleanup_loop,name="retention-cleanup",daemon=True)
    cleanup_thread.start()
    window=HistoryWindow(store); monitor=ClipboardMonitor(store); monitor.start()
    try:
        import pystray
        from PIL import Image,ImageDraw
        icon_image=Image.new("RGB",(64,64),"white"); draw=ImageDraw.Draw(icon_image)
        draw.rounded_rectangle((6,6,58,58),radius=10,fill="#315b9a"); draw.text((17,20),"CL",fill="white")
        def show(_icon,_item): window.root.after(0,window.show)
        def quit_app(icon,_item):
            monitor.stop(); icon.stop(); window.root.after(0,window.root.destroy)
        menu=pystray.Menu(pystray.MenuItem("Open history",show,default=True),
            pystray.MenuItem("Pause monitoring",lambda _i,_m:monitor.pause()),
            pystray.MenuItem("Resume monitoring",lambda _i,_m:monitor.pause(False)),
            pystray.MenuItem("Clean expired",lambda _i,_m:store.cleanup()),
            pystray.MenuItem("Quit",quit_app))
        tray=pystray.Icon("SmartClipboardManager",icon_image,"Smart Clipboard Manager",menu)
        threading.Thread(target=tray.run,daemon=True).start()
        window.root.withdraw(); window.root.mainloop()
    except ImportError:
        window.root.mainloop()
    finally:
        cleanup_stop.set(); cleanup_thread.join(timeout=5)
        monitor.stop()
if __name__=="__main__": main()
