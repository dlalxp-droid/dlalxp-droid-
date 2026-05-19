"""
공통 오버레이 — 모든 릴스 영상에 필수.
A. 하단 지속 노출 유의문구 (0~13초, 글자크기 ≥ 영상 세로 1/40 = 48pt)
B. 마지막 풀스크린 필수고지 (13~15초)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BAND_Y = 1810       # 하단 띠 시작 y
BAND_H = 110        # 띠 높이

PAPER     = (250, 246, 235)
INK       = (32, 40, 70)
RED_INK   = (210, 60, 70)
PENCIL    = (110, 118, 135)
BAND_BG   = (252, 248, 232)
BAND_LINE = (210, 180, 140)

_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_HERE)
_FDIR = os.path.join(_BASE, 'fonts')
NANUM_P = os.path.join(_FDIR, 'NanumPenScript-Regular.ttf')
GAMJA_P = os.path.join(_FDIR, 'GamjaFlower-Regular.ttf')
HIM_P   = os.path.join(_FDIR, 'HiMelody-Regular.ttf')

def _f(p, s): return ImageFont.truetype(p, s)

DISCLAIMERS = [
    ("본 내용은 모집종사자 개인의 의견이며,",
     "손익은 보험계약자·피보험자에게 귀속됩니다"),
    ("보험사·상품별로 상이할 수 있으므로",
     "세부사항은 반드시 해당 약관을 참조 바랍니다"),
    ("성별·연령·직업 등에 따라 가입 담보·",
     "가입금액·보험료 등이 달라질 수 있습니다"),
]

def draw_bottom_disclaimer(base, t):
    if t >= 13.0:
        return
    if t < 5:
        idx = 0
    elif t < 10:
        idx = 1
    else:
        idx = 2
    line1, line2 = DISCLAIMERS[idx]

    band = Image.new('RGBA', (W, BAND_H), BAND_BG + (245,))
    bd = ImageDraw.Draw(band)
    bd.line([(0, 0), (W, 0)], fill=BAND_LINE + (220,), width=2)

    font = _f(NANUM_P, 48)
    pad_top = 6
    line_h  = 48
    for i, line in enumerate([line1, line2]):
        b = bd.textbbox((0, 0), line, font=font)
        tx = (W - (b[2] - b[0])) // 2
        bd.text((tx, pad_top + i * line_h), line, fill=INK + (255,), font=font)

    base.alpha_composite(band, (0, BAND_Y))


SWITCH_LINES = [
    ("[승환계약 안내]", True),
    ("기존 계약 해지 후 새 계약 체결 과정에서", False),
    ("1. 질병이력·연령증가 등으로 가입이 거절되거나", False),
    ("    보험료가 인상될 수 있습니다.", False),
    ("2. 가입 상품에 따라 새로운 면책기간 적용 및", False),
    ("    보장 제한 등 기타 불이익이 발생할 수 있습니다.", False),
]

def draw_final_disclosure(base, t):
    """13~15초 풀스크린 필수고지"""
    if t < 13.0:
        return
    fade_p = min(1.0, (t - 13.0) / 0.3)

    # 페이퍼 톤 풀스크린
    overlay = Image.new('RGBA', (W, H), PAPER + (int(252 * fade_p),))
    base.alpha_composite(overlay, (0, 0))

    if fade_p < 0.4:
        return

    a = int(255 * min(1.0, (fade_p - 0.3) / 0.7))

    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)

    title_font = _f(GAMJA_P, 104)
    label_font = _f(GAMJA_P, 60)
    body_font  = _f(NANUM_P, 52)
    small_font = _f(NANUM_P, 42)

    # 타이틀
    title = "※ 필수 고지사항"
    b = ld.textbbox((0, 0), title, font=title_font)
    tx = (W - (b[2] - b[0])) // 2
    ld.text((tx, 110), title, fill=RED_INK + (a,), font=title_font)

    # 가로 줄
    ld.line([(120, 250), (W - 120, 250)], fill=INK + (a,), width=3)

    LEFT = 130
    y = 310

    # ─── 설계사 ───
    ld.text((LEFT, y), "설계사", fill=PENCIL + (a,), font=label_font)
    y += 76
    ld.text((LEFT, y), "프라임에셋  박기성", fill=INK + (a,), font=body_font)
    y += 66
    ld.text((LEFT, y), "협회 등록번호  202511200002261",
            fill=INK + (a,), font=body_font)
    y += 110

    # ─── 심의필 ───
    ld.text((LEFT, y), "심의필", fill=PENCIL + (a,), font=label_font)
    y += 76
    ld.text((LEFT, y), "제 [----] 호  ( ---- ~ ---- )",
            fill=INK + (a,), font=body_font)
    y += 66
    ld.text((LEFT, y), "본 광고는 광고심의기준을 준수하였으며,",
            fill=PENCIL + (a,), font=small_font)
    y += 52
    ld.text((LEFT, y), "유효기간은 심의일로부터 1년입니다.",
            fill=PENCIL + (a,), font=small_font)
    y += 110

    # ─── 승환계약 안내 ───
    ld.text((LEFT, y), "[승환계약 안내]", fill=RED_INK + (a,), font=label_font)
    y += 80
    for line in [
        "기존 계약 해지 후 새 계약 체결 과정에서",
        "1. 질병이력·연령증가 등으로 가입이 거절되거나",
        "    보험료가 인상될 수 있습니다.",
        "2. 가입 상품에 따라 새로운 면책기간 적용 및",
        "    보장 제한 등 기타 불이익이 발생할 수 있습니다.",
    ]:
        ld.text((LEFT, y), line, fill=INK + (a,), font=small_font)
        y += 56

    base.alpha_composite(layer, (0, 0))
