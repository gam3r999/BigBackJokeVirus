"""
╔══════════════════════════════════════════════════════════╗
║              big_back_virus.py                           ║
║  Prank script — 100% reversible, run revert_virus.py    ║
╚══════════════════════════════════════════════════════════╝

FOLDER STRUCTURE:
    big_back_virus.py
    revert_virus.py
    music.mp3           ← big back earrape (mp3/wav/ogg)
    byebyte.wav         ← byebyte music MUST BE WAV for Sound channel
    images/             ← your images/gifs

REQUIREMENTS:
    pip install pygame pillow

NOTE: byebyte MUST be a .wav file — pygame.mixer.Sound cannot load MP3.
      Convert with Audacity, VLC, or any online converter.

TIMELINE:
    0s   — big back music plays alone
    6s   — popups + ALL GDI effects + byebyte.wav joins simultaneously
    36s  — wallpaper changes (everything still running)
    38s  — popups close, BSOD appears (GDI + both tracks continue)
    58s  — everything stops

GDI EFFECTS (cycle randomly):
    • Screen inversion / color flip
    • Horizontal sine wobble
    • Zoom tunnel (shrink into center)
    • 90° rotation chunks
    • Screen swirl (polar warp)
    • Random static / noise blocks
    • Vertical flip strips
    • Kaleidoscope mirror halves
"""

import os
import sys
import time
import shutil
import ctypes
import random
import threading
import math
import tkinter as tk
from PIL import Image, ImageTk
import pygame

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR  = os.path.join(SCRIPT_DIR, "images")
BACKUP_DIR  = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "big_back_backup")

POPUP_COUNT    = 7
POPUP_W        = 420
POPUP_H        = 320
FLASH_INTERVAL = 150
BSOD_DURATION  = 20

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# ─────────────────────────────────────────────
# AUDIO FILE DETECTION
# ─────────────────────────────────────────────

def find_audio(hints, extensions=(".mp3", ".wav", ".ogg")):
    for fname in os.listdir(SCRIPT_DIR):
        base, ext = os.path.splitext(fname)
        if ext.lower() in extensions:
            for hint in hints:
                if hint.lower() in base.lower():
                    return os.path.join(SCRIPT_DIR, fname)
    return None

BIGBACK_FILE = find_audio(["music", "bigback", "big_back", "big back"])
# byebyte MUST be WAV — pygame.mixer.Sound can't decode MP3
BYEBYTE_FILE = find_audio(["byebyte", "bye_byte", "bye byte"], extensions=(".wav",))

# ─────────────────────────────────────────────
# AUDIO
# pygame.mixer.music  → big back  (streamed MP3, looping)
# pygame.mixer.Sound  → byebyte   (WAV loaded into memory, looping)
# They play on completely separate channels simultaneously.
# ─────────────────────────────────────────────

def init_audio():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(8)

def play_bigback():
    if not BIGBACK_FILE:
        print("[!] music.mp3 not found — skipping big back audio")
        return
    pygame.mixer.music.load(BIGBACK_FILE)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)
    print(f"[*] Big back: {os.path.basename(BIGBACK_FILE)}")

def play_byebyte():
    if not BYEBYTE_FILE:
        print("[!] byebyte.wav not found — make sure it's a .wav file")
        return
    try:
        snd = pygame.mixer.Sound(BYEBYTE_FILE)
        snd.set_volume(1.0)
        ch = pygame.mixer.find_channel(True)  # grab any free channel
        if ch:
            ch.play(snd, loops=-1)
            print(f"[*] Byebyte: {os.path.basename(BYEBYTE_FILE)}")
        else:
            print("[!] No free mixer channel for byebyte")
    except Exception as e:
        print(f"[!] Byebyte playback error: {e}")

def stop_all_audio():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
    try:
        pygame.mixer.stop()
    except Exception:
        pass

# ─────────────────────────────────────────────
# WINDOWS GDI SETUP
# ─────────────────────────────────────────────

user32 = ctypes.windll.user32
gdi32  = ctypes.windll.gdi32

SRCCOPY   = 0x00CC0020
SRCINVERT = 0x00550009
NOTSRCCOPY= 0x00330008
HALFTONE  = 4
BLACKNESS = 0x00000042

def screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def get_screen_dc():
    return user32.GetDC(None)

def release_dc(hdc):
    user32.ReleaseDC(None, hdc)

def make_mem_dc(hdc, sw, sh):
    """Create a memory DC with a compatible bitmap, return (mem_dc, bmp)."""
    mem_dc = gdi32.CreateCompatibleDC(hdc)
    bmp    = gdi32.CreateCompatibleBitmap(hdc, sw, sh)
    gdi32.SelectObject(mem_dc, bmp)
    return mem_dc, bmp

def free_mem_dc(mem_dc, bmp):
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mem_dc)

# ─────────────────────────────────────────────
# GDI EFFECT 1 — COLOR INVERSION
# ─────────────────────────────────────────────

def gdi_invert(sw, sh):
    hdc = get_screen_dc()
    gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, SRCINVERT)
    for _ in range(random.randint(4, 10)):
        x = random.randint(0, sw - 150)
        y = random.randint(0, sh - 150)
        w = random.randint(80, 350)
        h = random.randint(80, 250)
        gdi32.BitBlt(hdc, x, y, w, h, hdc, x, y, SRCINVERT)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 2 — HORIZONTAL SINE WOBBLE
# ─────────────────────────────────────────────

_wobble_phase = 0.0

def gdi_wobble(sw, sh):
    global _wobble_phase
    hdc = get_screen_dc()
    mem_dc, bmp = make_mem_dc(hdc, sw, sh)
    gdi32.BitBlt(mem_dc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    strip_h = 5
    for y in range(0, sh, strip_h):
        offset = int(math.sin(_wobble_phase + y * 0.025) * 28)
        gdi32.BitBlt(hdc, offset, y, sw, strip_h, mem_dc, 0, y, SRCCOPY)
    _wobble_phase += 0.35
    free_mem_dc(mem_dc, bmp)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 3 — ZOOM TUNNEL (shrink into center)
# ─────────────────────────────────────────────

def gdi_tunnel(sw, sh):
    hdc = get_screen_dc()
    mem_dc, bmp = make_mem_dc(hdc, sw, sh)
    gdi32.BitBlt(mem_dc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)
    layers = random.randint(4, 7)
    for i in range(layers):
        scale = 1.0 - (i + 1) * (0.85 / layers)
        nw = int(sw * scale)
        nh = int(sh * scale)
        nx = (sw - nw) // 2
        ny = (sh - nh) // 2
        gdi32.SetStretchBltMode(hdc, HALFTONE)
        gdi32.StretchBlt(hdc, nx, ny, nw, nh, mem_dc, 0, 0, sw, sh, SRCCOPY)
    free_mem_dc(mem_dc, bmp)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 4 — ROTATION CHUNKS
# Chops screen into tiles and rotates each tile 90/180/270°
# by swapping quadrant BitBlts
# ─────────────────────────────────────────────

def gdi_rotation_chunks(sw, sh):
    hdc = get_screen_dc()
    mem_dc, bmp = make_mem_dc(hdc, sw, sh)
    gdi32.BitBlt(mem_dc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)

    tile_w = sw // random.randint(3, 6)
    tile_h = sh // random.randint(3, 6)

    for ty in range(0, sh - tile_h, tile_h):
        for tx in range(0, sw - tile_w, tile_w):
            # Pick a random rotation: 0, 90, 180, 270
            rot = random.choice([0, 1, 2, 3])
            if rot == 0:
                continue
            elif rot == 1:
                # 180° — copy tile flipped both axes by using offset source
                sx = tx + tile_w if tx + tile_w < sw else tx
                sy = ty + tile_h if ty + tile_h < sh else ty
                gdi32.StretchBlt(hdc, tx, ty, tile_w, tile_h,
                                 mem_dc, sx, sy, -tile_w, -tile_h, SRCCOPY)
            elif rot == 2:
                # Horizontal flip within tile
                gdi32.StretchBlt(hdc, tx, ty, tile_w, tile_h,
                                 mem_dc, tx + tile_w, ty, -tile_w, tile_h, SRCCOPY)
            elif rot == 3:
                # Vertical flip within tile
                gdi32.StretchBlt(hdc, tx, ty, tile_w, tile_h,
                                 mem_dc, tx, ty + tile_h, tile_w, -tile_h, SRCCOPY)

    free_mem_dc(mem_dc, bmp)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 5 — SCREEN SWIRL
# Warps concentric rings of the screen in alternating directions
# by sampling rings from the snapshot at offset angles
# ─────────────────────────────────────────────

_swirl_angle = 0.0

def gdi_swirl(sw, sh):
    global _swirl_angle
    hdc = get_screen_dc()
    mem_dc, bmp = make_mem_dc(hdc, sw, sh)
    gdi32.BitBlt(mem_dc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)

    cx, cy   = sw // 2, sh // 2
    ring_w   = max(30, sw // 14)
    max_ring = min(cx, cy)

    for r in range(0, max_ring, ring_w):
        angle_offset = math.sin(_swirl_angle + r * 0.04) * 40
        ox = int(math.cos(math.radians(angle_offset)) * r * 0.12)
        oy = int(math.sin(math.radians(angle_offset)) * r * 0.12)

        x1 = max(0, cx - r - ring_w)
        y1 = max(0, cy - r - ring_w)
        x2 = min(sw, cx + r + ring_w)
        y2 = min(sh, cy + r + ring_w)
        rw = x2 - x1
        rh = y2 - y1
        if rw > 0 and rh > 0:
            sx = max(0, min(sw - rw, x1 + ox))
            sy = max(0, min(sh - rh, y1 + oy))
            gdi32.BitBlt(hdc, x1, y1, rw, rh, mem_dc, sx, sy, SRCCOPY)

    _swirl_angle += 0.2
    free_mem_dc(mem_dc, bmp)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 6 — STATIC / NOISE BLOCKS
# Draws random solid-color rectangles all over the screen
# ─────────────────────────────────────────────

def gdi_static(sw, sh):
    hdc = get_screen_dc()
    count = random.randint(30, 80)
    for _ in range(count):
        x = random.randint(0, sw - 60)
        y = random.randint(0, sh - 40)
        w = random.randint(5, 60)
        h = random.randint(5, 40)
        # Random grayscale color brush
        gray = random.randint(0, 255)
        color = gray | (gray << 8) | (gray << 16)
        brush = gdi32.CreateSolidBrush(color)
        rect  = ctypes.create_string_buffer(16)
        ctypes.struct = None
        import struct
        rect_bytes = struct.pack("iiii", x, y, x + w, y + h)
        ctypes.windll.user32.FillRect(hdc, ctypes.create_string_buffer(rect_bytes), brush)
        gdi32.DeleteObject(brush)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 7 — VERTICAL STRIP FLIP
# Copies vertical strips of screen with Y flipped
# ─────────────────────────────────────────────

def gdi_vflip_strips(sw, sh):
    hdc = get_screen_dc()
    mem_dc, bmp = make_mem_dc(hdc, sw, sh)
    gdi32.BitBlt(mem_dc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)

    strip_w = sw // random.randint(6, 14)
    for x in range(0, sw - strip_w, strip_w * 2):
        # Flip this strip vertically
        gdi32.StretchBlt(hdc, x, 0, strip_w, sh,
                         mem_dc, x, sh, strip_w, -sh, SRCCOPY)

    free_mem_dc(mem_dc, bmp)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 8 — KALEIDOSCOPE MIRROR
# Copies left half mirrored onto right half, top mirrored onto bottom
# ─────────────────────────────────────────────

def gdi_kaleidoscope(sw, sh):
    hdc = get_screen_dc()
    mem_dc, bmp = make_mem_dc(hdc, sw, sh)
    gdi32.BitBlt(mem_dc, 0, 0, sw, sh, hdc, 0, 0, SRCCOPY)

    mode = random.randint(0, 3)
    half_w = sw // 2
    half_h = sh // 2

    if mode == 0:
        # Mirror left→right
        gdi32.StretchBlt(hdc, sw, 0, -sw, sh,
                         mem_dc, 0, 0, sw, sh, SRCCOPY)
    elif mode == 1:
        # Mirror top→bottom
        gdi32.StretchBlt(hdc, 0, sh, sw, -sh,
                         mem_dc, 0, 0, sw, sh, SRCCOPY)
    elif mode == 2:
        # Mirror left half only
        gdi32.StretchBlt(hdc, half_w, 0, half_w, sh,
                         mem_dc, half_w, 0, -half_w, sh, SRCCOPY)
    elif mode == 3:
        # Mirror top half only
        gdi32.StretchBlt(hdc, 0, half_h, sw, half_h,
                         mem_dc, 0, half_h, sw, -half_h, SRCCOPY)

    free_mem_dc(mem_dc, bmp)
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI EFFECT 9 — FLASH (invert entire screen fast)
# ─────────────────────────────────────────────

_flash_state = False

def gdi_flash(sw, sh):
    global _flash_state
    hdc = get_screen_dc()
    gdi32.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, SRCINVERT)
    _flash_state = not _flash_state
    release_dc(hdc)

# ─────────────────────────────────────────────
# GDI MASTER LOOP
# Effects are grouped into bursts — each burst runs one effect
# for a random number of frames before switching to the next.
# ─────────────────────────────────────────────

_gdi_active = False

EFFECTS = [
    gdi_invert,
    gdi_wobble,
    gdi_tunnel,
    gdi_rotation_chunks,
    gdi_swirl,
    gdi_static,
    gdi_vflip_strips,
    gdi_kaleidoscope,
    gdi_flash,
    gdi_tunnel,       # tunnel appears twice — it's the most impactful
    gdi_swirl,
    gdi_wobble,
    gdi_rotation_chunks,
]

def start_gdi_effects():
    global _gdi_active
    _gdi_active = True
    sw, sh = screen_size()

    def _loop():
        idx   = 0
        burst = 0
        random.shuffle(EFFECTS)
        while _gdi_active:
            fn = EFFECTS[idx % len(EFFECTS)]
            try:
                fn(sw, sh)
            except Exception:
                pass
            burst += 1
            if burst >= random.randint(6, 18):
                burst = 0
                idx  += 1
            time.sleep(0.035)   # ~28 fps

    threading.Thread(target=_loop, daemon=True).start()
    print("[*] GDI effects running (9 effects active).")

def stop_gdi_effects():
    global _gdi_active
    _gdi_active = False
    time.sleep(0.15)
    print("[*] GDI effects stopped.")

# ─────────────────────────────────────────────
# LOAD IMAGE PATHS
# ─────────────────────────────────────────────

def load_image_paths():
    if not os.path.isdir(IMAGES_DIR):
        print(f"[!] images/ folder not found at: {IMAGES_DIR}")
        sys.exit(1)
    paths = [
        os.path.join(IMAGES_DIR, f)
        for f in sorted(os.listdir(IMAGES_DIR))
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ]
    if not paths:
        print("[!] No images found in images/")
        sys.exit(1)
    print(f"[*] Found {len(paths)} image(s)")
    return paths

# ─────────────────────────────────────────────
# WALLPAPER
# ─────────────────────────────────────────────

def get_current_wallpaper():
    buf = ctypes.create_unicode_buffer(260)
    user32.SystemParametersInfoW(0x0073, 260, buf, 0)
    return buf.value

def set_wallpaper(path):
    user32.SystemParametersInfoW(0x0014, 0, path, 0x01 | 0x02)

def backup_and_change_wallpaper(new_image_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    original = get_current_wallpaper()
    with open(os.path.join(BACKUP_DIR, "original_path.txt"), "w") as f:
        f.write(original)
    if original and os.path.exists(original):
        ext = os.path.splitext(original)[1] or ".bmp"
        shutil.copy2(original, os.path.join(BACKUP_DIR, "original_wallpaper" + ext))
    bmp_path = os.path.join(BACKUP_DIR, "prank_wallpaper.bmp")
    Image.open(new_image_path).convert("RGB").save(bmp_path, "BMP")
    set_wallpaper(bmp_path)
    print("[*] Wallpaper changed and backed up.")

# ─────────────────────────────────────────────
# POPUP WINDOWS
# Images loaded INSIDE each thread to avoid cross-thread Tkinter errors
# ─────────────────────────────────────────────

_popups_alive = False

def _make_popup_window(image_paths, x, y, start_index):
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{POPUP_W}x{POPUP_H}+{x}+{y}")
    root.attributes("-topmost", True)
    root.configure(bg="black")

    photos = []
    for path in image_paths:
        try:
            img = Image.open(path).convert("RGB")
            img = img.resize((POPUP_W, POPUP_H), Image.LANCZOS)
            photos.append(ImageTk.PhotoImage(img, master=root))
        except Exception as e:
            print(f"[!] Skipping {os.path.basename(path)}: {e}")

    if not photos:
        root.destroy()
        return

    label = tk.Label(root, bd=0, bg="black")
    label.pack(fill="both", expand=True)
    idx = [start_index % len(photos)]

    def next_frame():
        if not _popups_alive:
            try:
                root.destroy()
            except Exception:
                pass
            return
        try:
            label.config(image=photos[idx[0]])
            idx[0] = (idx[0] + 1) % len(photos)
            root.after(FLASH_INTERVAL, next_frame)
        except Exception:
            pass

    root.after(0, next_frame)
    try:
        root.mainloop()
    except Exception:
        pass

def spawn_popup_windows(image_paths, count):
    global _popups_alive
    _popups_alive = True
    probe = tk.Tk()
    probe.withdraw()
    sw = probe.winfo_screenwidth()
    sh = probe.winfo_screenheight()
    probe.destroy()
    margin = 40
    for i in range(count):
        x = random.randint(margin, max(margin + 1, sw - POPUP_W - margin))
        y = random.randint(margin, max(margin + 1, sh - POPUP_H - margin))
        start_idx = (i * max(1, len(image_paths) // count)) % len(image_paths)
        threading.Thread(
            target=_make_popup_window,
            args=(image_paths, x, y, start_idx),
            daemon=True
        ).start()
        time.sleep(0.2)

def close_popup_windows():
    global _popups_alive
    _popups_alive = False

# ─────────────────────────────────────────────
# FAKE BSOD
# ─────────────────────────────────────────────

def show_fake_bsod(duration):
    # Find bsod.png next to the script (case-insensitive)
    bsod_path = None
    for fname in os.listdir(SCRIPT_DIR):
        if fname.lower() == "bsod.png":
            bsod_path = os.path.join(SCRIPT_DIR, fname)
            break

    if not bsod_path:
        print("[!] bsod.png not found next to script — skipping BSOD.")
        time.sleep(duration)
        return

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg="black")

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    # Load and stretch bsod.png to fill the entire screen
    img   = Image.open(bsod_path).convert("RGB")
    img   = img.resize((sw, sh), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img, master=root)

    lbl = tk.Label(root, image=photo, bd=0, bg="black")
    lbl.image = photo   # keep reference alive
    lbl.place(x=0, y=0, width=sw, height=sh)

    start = time.time()

    def update():
        if (time.time() - start) >= duration:
            root.destroy()
        else:
            root.after(400, update)

    root.after(400, update)
    root.mainloop()

# ─────────────────────────────────────────────
# MAIN SEQUENCE
# ─────────────────────────────────────────────

def main():
    image_paths = load_image_paths()

    # Phase 1 — big back music alone (6s)
    print("[*] Phase 1 — big back music")
    init_audio()
    play_bigback()
    time.sleep(6)

    # Phase 2 — popups + GDI chaos + byebyte all at once
    print("[*] Phase 2 — popups + GDI effects + byebyte")
    spawn_popup_windows(image_paths, count=POPUP_COUNT)
    start_gdi_effects()
    play_byebyte()
    time.sleep(30)

    # Phase 3 — wallpaper (everything still running)
    print("[*] Phase 3 — wallpaper change")
    try:
        backup_and_change_wallpaper(image_paths[0])
    except Exception as e:
        print(f"[!] Wallpaper failed: {e}")
    time.sleep(2)

    # Phase 4 — BSOD (GDI + both tracks keep going)
    print(f"[*] Phase 4 — BSOD + GDI + music ({BSOD_DURATION}s)")
    close_popup_windows()
    time.sleep(0.3)
    show_fake_bsod(BSOD_DURATION)

    # Phase 5 — kill everything
    stop_gdi_effects()
    stop_all_audio()
    print("[*] Done! Run revert_virus.py to restore everything.")

if __name__ == "__main__":
    main()
