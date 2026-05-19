"""
릴스 01: 보험 점검 체크리스트
손글씨 노트풍 1080x1920 / 15초 / 30fps
"""
import os, math, random, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reels_overlay import draw_bottom_disclaimer, draw_final_disclosure

W, H = 1080, 1920
FPS = 30
DURATION = 15
TOTAL = FPS * DURATION

PAPER      = (250, 246, 235)
LINE       = (210, 220, 230)
INK        = (32, 40, 70)
RED_INK    = (210, 60, 70)
PENCIL     = (110, 118, 135)
HL_YELLOW  = (255, 230, 60)
STICKY     = (255, 232, 110)
STICKY_DK  = (230, 200, 70)
MARGIN_RED = (220, 130, 130)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(BASE_DIR, 'fonts')
NANUM_P  = os.path.join(FONT_DIR, 'NanumPenScript-Regular.ttf')
GAMJA_P  = os.path.join(FONT_DIR, 'GamjaFlower-Regular.ttf')
HIM_P    = os.path.join(FONT_DIR, 'HiMelody-Regular.ttf')

def f(p, s): return ImageFont.truetype(p, s)
def ease(t): return 1 - (1-t)**3
def clamp(v, lo=0.0, hi=1.0): return max(lo, min(hi, v))

def hand_line(draw, p1, p2, color, width=3, jitter=1.5, segs=14, seed=0):
    rng = random.Random(seed)
    pts = []
    for i in range(segs+1):
        t = i/segs
        x = p1[0] + (p2[0]-p1[0])*t
        y = p1[1] + (p2[1]-p1[1])*t
        if 0 < i < segs:
            x += rng.uniform(-jitter, jitter)
            y += rng.uniform(-jitter, jitter)
        pts.append((x,y))
    for i in range(len(pts)-1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)

def wavy_underline(draw, x1, x2, y, color, amp=8, period=42, width=4, jitter=2, seed=0):
    if x2 <= x1: return
    rng = random.Random(seed)
    n = max(4, int((x2-x1)/3))
    pts = []
    for i in range(n+1):
        t = i/n
        x = x1 + (x2-x1)*t
        y_off = math.sin((x - x1) / period * 2 * math.pi) * amp
        y_off += rng.uniform(-jitter, jitter)
        pts.append((x, y + y_off))
    for i in range(len(pts)-1):
        draw.line([pts[i], pts[i+1]], fill=color, width=width)

def draw_paper(img, draw):
    draw.rectangle([0,0,W,H], fill=PAPER)
    for y in range(160, H-40, 78):
        draw.line([(150, y), (W-60, y)], fill=LINE, width=2)
    hand_line(draw, (135, 0), (135, H), MARGIN_RED, width=3, jitter=1.0, segs=50, seed=1)
    for cy in [240, 720, 1200, 1680]:
        cx = 80; r = 22
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(228, 220, 198), outline=(195, 188, 170), width=2)
        draw.ellipse([cx-r+5, cy-r+5, cx-r+13, cy-r+13], fill=(245, 240, 222))

def draw_sticky_tag(base, progress=1.0):
    if progress <= 0: return
    off = int(40 * (1 - progress))
    a = int(255 * progress)
    sw, sh = 350, 130
    pad = 30
    layer = Image.new('RGBA', (sw + pad*2, sh + pad*2), (0,0,0,0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([pad+6, pad+8, pad+sw+6, pad+sh+8], fill=(0,0,0,45))
    ld.rectangle([pad, pad, pad+sw, pad+sh], fill=STICKY+(a,))
    ld.polygon([(pad+sw, pad+sh-28), (pad+sw, pad+sh), (pad+sw-28, pad+sh)], fill=STICKY_DK+(a,))
    font = f(GAMJA_P, 60)
    text = "보험 점검"
    bb = ld.textbbox((0,0), text, font=font)
    text_w = bb[2]-bb[0]; text_h = bb[3]-bb[1]
    tx = pad + (sw - text_w - 60)//2
    ty = pad + (sh - text_h)//2 - 8
    ld.text((tx, ty), text, fill=INK+(a,), font=font)
    cx = tx + text_w + 22
    cy = ty + text_h//2 + 10
    ld.line([(cx, cy), (cx+13, cy+18), (cx+40, cy-22)], fill=RED_INK+(a,), width=6)
    rot = layer.rotate(-5, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(rot, (W - rot.width - 60, 50 + off))

def _draw_text_lines(base, lines, font, y_start, color, line_h, progress, stagger=0.4, align='center'):
    for i, line in enumerate(lines):
        lp = clamp(progress * (1 + stagger * (len(lines)-1)) - i * stagger)
        if lp <= 0: continue
        a = int(255 * lp)
        layer = Image.new('RGBA', (W, line_h + 20), (0,0,0,0))
        ld = ImageDraw.Draw(layer)
        b = ld.textbbox((0,0), line, font=font)
        tw = b[2]-b[0]
        if align == 'center':
            tx = (W - tw)//2
        else:
            tx = 180
        ld.text((tx, 0), line, fill=color+(a,), font=font)
        base.alpha_composite(layer, (0, y_start + i*line_h))

def draw_title(base, progress=1.0):
    font = f(GAMJA_P, 82)
    lines = ["매달 보험료 내면서", "정작 보장은 받을 수 있을까요?"]
    _draw_text_lines(base, lines, font, 220, INK, 100, progress, stagger=0.45)

def draw_body(base, progress=1.0, hl_progress=1.0):
    font = f(NANUM_P, 64)
    lines = ["가입 전·후 꼭 봐야 할", "5가지 체크포인트"]
    y_start = 460
    if hl_progress > 0:
        tmp = Image.new('RGBA', (10,10)); td = ImageDraw.Draw(tmp)
        b = td.textbbox((0,0), lines[1], font=font)
        line_w = b[2]-b[0]
        cx = (W - line_w)//2
        hl_w = int(line_w * hl_progress) + 20
        hl_layer = Image.new('RGBA', (line_w+60, 90), (0,0,0,0))
        hl_d = ImageDraw.Draw(hl_layer)
        rng = random.Random(7)
        for i in range(5):
            jx = rng.randint(-4, 4); jy = rng.randint(-1, 2)
            hl_d.rectangle([10 + jx, 8 + i*3 + jy, 10 + hl_w + jx, 75 + jy],
                          fill=HL_YELLOW+(95,))
        base.alpha_composite(hl_layer, (cx - 30, y_start + 78))
    _draw_text_lines(base, lines, font, y_start, INK, 82, progress, stagger=0.35)

def draw_quote(base, progress=1.0):
    font = f(HIM_P, 52)
    lines = ['"어차피 약관 봐도 모르겠고..."', '"가입했으니 알아서 되겠지" 했다면']
    _draw_text_lines(base, lines, font, 660, PENCIL, 66, progress, stagger=0.35)

def draw_arrow_and_geunde(base, arrow_progress=1.0, text_progress=1.0):
    if arrow_progress > 0:
        layer = Image.new('RGBA', (200, 90), (0,0,0,0))
        ld = ImageDraw.Draw(layer)
        ax = 100
        ay_bot = int(60 * arrow_progress) + 5
        hand_line(ld, (ax, 5), (ax, ay_bot), INK+(int(255*arrow_progress),),
                 width=4, jitter=1.2, segs=10, seed=11)
        if arrow_progress > 0.55:
            hp = clamp((arrow_progress - 0.55) / 0.45)
            a = int(255 * hp)
            hl = int(22 * hp)
            hand_line(ld, (ax, ay_bot), (ax-hl, ay_bot-hl-2), INK+(a,),
                     width=4, jitter=1.0, segs=6, seed=12)
            hand_line(ld, (ax, ay_bot), (ax+hl, ay_bot-hl-2), INK+(a,),
                     width=4, jitter=1.0, segs=6, seed=13)
        base.alpha_composite(layer, ((W-200)//2, 830))
    if text_progress > 0:
        font = f(GAMJA_P, 54)
        a = int(255 * text_progress)
        layer = Image.new('RGBA', (W, 80), (0,0,0,0))
        ld = ImageDraw.Draw(layer)
        text = "근데..."
        b = ld.textbbox((0,0), text, font=font)
        tx = (W - (b[2]-b[0]))//2
        ld.text((tx, 0), text, fill=INK+(a,), font=font)
        rot = layer.rotate(-2, resample=Image.BICUBIC, expand=False)
        base.alpha_composite(rot, (0, 930))

def draw_red_punch(base, progress=1.0, underline_progress=1.0):
    font = f(GAMJA_P, 80)
    lines = ["모르고 지나가면", "정작 필요할 때 못 받아요"]
    y_start = 990
    _draw_text_lines(base, lines, font, y_start, RED_INK, 108, progress, stagger=0.4)
    if underline_progress > 0:
        tmp = Image.new('RGBA', (10,10)); td = ImageDraw.Draw(tmp)
        b = td.textbbox((0,0), lines[1], font=font)
        line_w = b[2]-b[0]
        cx_start = (W - line_w)//2
        cx_now = cx_start + int(line_w * underline_progress)
        bd = ImageDraw.Draw(base)
        wavy_underline(bd, cx_start, cx_now, y_start + 108 + 100, RED_INK,
                      amp=9, period=44, width=5, jitter=1.8, seed=21)

def draw_checklist(base, progress_per_item):
    items = [
        ("갱신형 vs 비갱신형", "(보험료 인상)", False),
        ("일반암 vs 유사암", "(지급 금액 차이)", False),
        ("실손 1·2세대 vs 5세대", "(보장 범위)", False),
        ("납입면제 조항 있는지", "", True),
        ("보장 공백(면책기간) 확인", "", True),
    ]
    font = f(NANUM_P, 52)
    sub_font = f(NANUM_P, 36)
    y_start = 1230
    x_box = 180
    x_text = 248
    row_h = 58

    for i, (title, sub, hl) in enumerate(items):
        box_p, check_p = progress_per_item[i]
        if box_p <= 0: continue
        y = y_start + i * row_h
        a_box = int(255 * box_p)
        if hl and box_p > 0.4:
            hp = clamp((box_p - 0.4) / 0.6)
            tmp = Image.new('RGBA', (10,10)); td = ImageDraw.Draw(tmp)
            b = td.textbbox((0,0), title, font=font)
            tw_val = b[2]-b[0]
            hl_layer = Image.new('RGBA', (tw_val + 40, 66), (0,0,0,0))
            hl_d = ImageDraw.Draw(hl_layer)
            rng = random.Random(30 + i)
            for j in range(4):
                jx = rng.randint(-3, 3); jy = rng.randint(-1, 1)
                hl_d.rectangle([jx, 6 + j*3 + jy, int(tw_val*hp) + jx + 18, 58 + jy],
                              fill=HL_YELLOW+(90,))
            base.alpha_composite(hl_layer, (x_text - 8, y - 2))
        bd = ImageDraw.Draw(base)
        box_size = 40
        bx, by = x_box, y + 6
        hand_line(bd, (bx, by), (bx+box_size, by), INK, width=3, jitter=1.2, segs=8, seed=40+i*4)
        hand_line(bd, (bx+box_size, by), (bx+box_size, by+box_size), INK, width=3, jitter=1.2, segs=8, seed=41+i*4)
        hand_line(bd, (bx+box_size, by+box_size), (bx, by+box_size), INK, width=3, jitter=1.2, segs=8, seed=42+i*4)
        hand_line(bd, (bx, by+box_size), (bx, by), INK, width=3, jitter=1.2, segs=8, seed=43+i*4)
        if check_p > 0:
            ap = clamp(check_p)
            p1 = (bx + 4, by + box_size//2 + 2)
            p2 = (bx + box_size//2, by + box_size - 2)
            p3 = (bx + box_size + 10, by - 6)
            if ap <= 0.5:
                t = ap / 0.5
                cur = (p1[0] + (p2[0]-p1[0])*t, p1[1] + (p2[1]-p1[1])*t)
                hand_line(bd, p1, cur, RED_INK, width=5, jitter=1, segs=4, seed=50+i)
            else:
                t = (ap - 0.5) / 0.5
                hand_line(bd, p1, p2, RED_INK, width=5, jitter=1, segs=4, seed=50+i)
                cur = (p2[0] + (p3[0]-p2[0])*t, p2[1] + (p3[1]-p2[1])*t)
                hand_line(bd, p2, cur, RED_INK, width=5, jitter=1, segs=6, seed=51+i)
        layer = Image.new('RGBA', (W, 70), (0,0,0,0))
        ld = ImageDraw.Draw(layer)
        ld.text((0, 0), title, fill=INK+(a_box,), font=font)
        if sub:
            b = ld.textbbox((0,0), title, font=font)
            title_w = b[2]-b[0]
            ld.text((title_w + 14, 14), sub, fill=PENCIL+(a_box,), font=sub_font)
        base.alpha_composite(layer, (x_text, y))

    disc_font = f(HIM_P, 30)
    disc = "* 보험사·상품별로 달라질 수 있어요"
    layer = Image.new('RGBA', (W, 38), (0,0,0,0))
    ld = ImageDraw.Draw(layer)
    b = ld.textbbox((0,0), disc, font=disc_font)
    tx = (W - (b[2]-b[0]))//2
    ld.text((tx, 0), disc, fill=PENCIL+(190,), font=disc_font)
    base.alpha_composite(layer, (0, y_start + 5 * row_h + 4))

def draw_star_bonus(base, star_progress=1.0, text_progress=1.0):
    sx, sy = 210, 1605
    if star_progress > 0:
        size = 32
        pts = []
        for i in range(10):
            angle = -math.pi/2 + i * math.pi/5
            r = size if i % 2 == 0 else size * 0.45
            pts.append((sx + math.cos(angle)*r, sy + math.sin(angle)*r))
        n_segs = max(1, int(len(pts) * star_progress))
        bd = ImageDraw.Draw(base)
        for i in range(n_segs):
            p1 = pts[i]
            p2 = pts[(i+1) % len(pts)]
            hand_line(bd, p1, p2, RED_INK, width=4, jitter=1, segs=4, seed=70+i)
    if text_progress > 0:
        font = f(GAMJA_P, 56)
        a = int(255 * text_progress)
        layer = Image.new('RGBA', (W, 80), (0,0,0,0))
        ld = ImageDraw.Draw(layer)
        text = "증권 한 장이면 다 점검돼요"
        ld.text((0, 0), text, fill=INK+(a,), font=font)
        base.alpha_composite(layer, (260, 1583))

def draw_cta(base, progress=1.0):
    if progress <= 0: return
    off = int(60 * (1 - progress))
    a = int(255 * progress)
    sw, sh = 860, 200
    pad = 26
    layer = Image.new('RGBA', (sw+pad*2, sh+pad*2), (0,0,0,0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([pad+8, pad+10, pad+sw+8, pad+sh+10], fill=(0,0,0,55))
    ld.rectangle([pad, pad, pad+sw, pad+sh], fill=STICKY+(a,))
    ld.polygon([(pad+sw, pad+sh-32), (pad+sw, pad+sh), (pad+sw-32, pad+sh)], fill=STICKY_DK+(a,))
    font_id  = f(GAMJA_P, 50)
    font_big = f(GAMJA_P, 58)
    font_med = f(NANUM_P, 46)
    line_id = "@gi_seong_5253"
    line1   = '댓글에 "정보" 남기면'
    line2   = "DM으로 증권 분석 안내드려요"
    bid = ld.textbbox((0,0), line_id, font=font_id)
    b1  = ld.textbbox((0,0), line1, font=font_big)
    b2  = ld.textbbox((0,0), line2, font=font_med)
    txid = pad + (sw - (bid[2]-bid[0]))//2
    tx1  = pad + (sw - (b1[2]-b1[0]))//2
    tx2  = pad + (sw - (b2[2]-b2[0]) - 56)//2
    ld.text((txid, pad+4),  line_id, fill=RED_INK+(a,), font=font_id)
    ld.text((tx1,  pad+58), line1,   fill=INK+(a,),     font=font_big)
    ld.text((tx2,  pad+128), line2,  fill=INK+(a,),     font=font_med)
    ex = tx2 + (b2[2]-b2[0]) + 14
    ey = pad + 140
    ld.rectangle([ex, ey, ex+44, ey+30], fill=(255,255,255,a), outline=RED_INK+(a,), width=3)
    ld.line([(ex, ey), (ex+22, ey+17), (ex+44, ey)], fill=RED_INK+(a,), width=3)
    rot = layer.rotate(-2, resample=Image.BICUBIC, expand=True)
    y_paste = 1810 - rot.height - 8 + off
    base.alpha_composite(rot, ((W - rot.width)//2, y_paste))

def render_frame(frame_idx, save_path=None):
    t = frame_idx / FPS
    img = Image.new('RGBA', (W, H), PAPER + (255,))
    draw = ImageDraw.Draw(img)
    draw_paper(img, draw)

    def seg(t_start, t_end):
        if t < t_start: return 0.0
        if t >= t_end: return 1.0
        return ease((t - t_start) / (t_end - t_start))

    p_sticky  = seg(0.3, 1.0)
    p_title   = seg(0.9, 2.1)
    p_body    = seg(2.3, 3.1)
    p_hl      = seg(3.1, 3.7)
    p_quote   = seg(3.7, 4.5)
    p_arrow   = seg(4.6, 5.2)
    p_geunde  = seg(5.2, 5.4)
    p_red     = seg(5.4, 6.6)
    p_redwave = seg(6.6, 7.2)
    check_items = []
    for i in range(5):
        ts = 7.2 + i * 0.35
        check_items.append((seg(ts, ts + 0.2), seg(ts + 0.1, ts + 0.4)))
    p_star  = seg(9.2, 9.6)
    p_bonus = seg(9.5, 9.9)
    p_cta   = seg(9.9, 10.9)

    draw_sticky_tag(img, p_sticky)
    draw_title(img, p_title)
    draw_body(img, p_body, p_hl)
    draw_quote(img, p_quote)
    draw_arrow_and_geunde(img, p_arrow, p_geunde)
    draw_red_punch(img, p_red, p_redwave)
    draw_checklist(img, check_items)
    draw_star_bonus(img, p_star, p_bonus)
    draw_cta(img, p_cta)

    draw_bottom_disclaimer(img, t)
    draw_final_disclosure(img, t)

    if save_path:
        img.convert('RGB').save(save_path)
    return img

def render_static():
    out_dir = os.path.join(BASE_DIR, 'output')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'static_01_preview.png')
    render_frame(TOTAL - 1, path)
    print(f"Saved: {path}")

def render_video():
    out_dir_frames = os.path.join(BASE_DIR, 'frames')
    os.makedirs(out_dir_frames, exist_ok=True)
    for i in range(TOTAL):
        path = os.path.join(out_dir_frames, f'f_{i:04d}.png')
        render_frame(i, path)
        if (i+1) % 30 == 0:
            print(f"  rendered {i+1}/{TOTAL}")
    print("Done frames.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'video':
        render_video()
    else:
        render_static()
