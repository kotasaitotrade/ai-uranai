"""スマホ最適化UI"""
import streamlit as st
import plotly.graph_objects as go
from datetime import date
import math
from logic import (
    calc_compatibility, get_zodiac, get_daily_fortune,
    get_numerology_full, get_kyusei_fortune, get_animal_fortune,
    get_seimei_fortune, get_horoscope, get_shichuu, get_biorhythm,
    get_blood_fortune, draw_tarot, draw_hexagram,
    ZODIAC_KEYWORD, ZODIAC_RULING, ZODIAC_ELEMENT, JUNISHI_ANIMAL,
    PLANET_MEANING, BLOOD_PERSONALITY, SPREAD_TYPES, SPREAD_POSITIONS,
)

MOBILE_CSS = """
<style>
    .stApp { background: linear-gradient(160deg, #0d0d2b 0%, #1a1a4e 100%); color: #f0e6ff; }
    h1, h2, h3 { color: #d4b8ff; }
    /* スマホ向け：タッチターゲット大きめ・余白調整 */
    .stButton>button {
        background: linear-gradient(90deg, #6a0dad, #9b6dff);
        color: white; border: none; border-radius: 12px;
        padding: 14px 24px; font-size: 17px; width: 100%;
        min-height: 52px;
    }
    .stSelectbox > div, .stDateInput > div { font-size: 16px; }
    .score-box {
        background: rgba(100,60,180,0.3);
        border: 1px solid #7b5ea7; border-radius: 12px;
        padding: 16px; text-align: center; margin: 8px 0;
    }
    .score-num { font-size: 44px; font-weight: bold; color: #f0c040; }
    .card {
        background: rgba(60,40,100,0.4);
        border: 1px solid #5a3d8a; border-radius: 12px;
        padding: 14px; margin: 6px 0;
    }
    .advice-box {
        background: rgba(60,40,100,0.4);
        border-left: 3px solid #9b6dff;
        padding: 12px 14px; margin: 6px 0;
        border-radius: 0 8px 8px 0;
    }
    /* メニューグリッド */
    .menu-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; margin: 12px 0; }
    .menu-btn {
        background: rgba(60,40,120,0.6); border: 1px solid #5a3d8a;
        border-radius: 12px; padding: 14px 4px; text-align: center;
        cursor: pointer; font-size: 13px; color: #d4b8ff;
    }
    .menu-btn:active { background: rgba(100,60,180,0.8); }
    .menu-btn .icon { font-size: 26px; display: block; margin-bottom: 4px; }
    /* セクションヘッダ */
    .section-header {
        color: #d4b8ff; font-size: 18px; font-weight: bold;
        margin: 16px 0 8px 0; padding-bottom: 6px;
        border-bottom: 1px solid #3a2a6a;
    }
    /* Streamlit余白削減 */
    .block-container { padding: 8px 12px 40px 12px !important; max-width: 100% !important; }
    section[data-testid="stSidebar"] { display: none; }
    header { display: none !important; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; padding: 8px 6px; color: #c9a0ff; }
</style>
"""

def render_mobile():
    st.set_page_config(page_title="🔮 占いポータル", page_icon="🔮",
                       layout="centered", initial_sidebar_state="collapsed")
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    page = st.query_params.get("page", "home")
    if page == "home":
        _home()
    else:
        _fortune_page(page)

def _go(page: str):
    params = dict(st.query_params)
    params["page"] = page
    st.query_params.update(params)

def _home():
    st.markdown("# 🔮 占いポータル")
    st.markdown("<p style='color:#a090c0;text-align:center;'>占いを選んでください</p>", unsafe_allow_html=True)

    menus = [
        ("💫", "相性占い", "compat"),
        ("⭐", "星座占い", "zodiac"),
        ("🔢", "数秘術", "numerology"),
        ("☯️", "九星気学", "kyusei"),
        ("🐾", "動物占い", "animal"),
        ("✍️", "姓名判断", "seimei"),
        ("🌌", "ホロスコープ", "horoscope"),
        ("🀄", "四柱推命", "shichuu"),
        ("📈", "バイオリズム", "biorhythm"),
        ("🩸", "血液型", "blood"),
        ("🃏", "タロット", "tarot"),
        ("☯", "易経", "ekikyo"),
    ]

    # 3列グリッド
    for i in range(0, len(menus), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(menus):
                icon, label, key = menus[i + j]
                with col:
                    if st.button(f"{icon}\n{label}", key=f"menu_{key}",
                                 use_container_width=True):
                        _go(key)
                        st.rerun()

def _back_btn():
    if st.button("← 戻る", key="back_btn"):
        _go("home")
        st.rerun()

def _fortune_page(page: str):
    pages = {
        "compat": _compat, "zodiac": _zodiac, "numerology": _numerology,
        "kyusei": _kyusei, "animal": _animal, "seimei": _seimei,
        "horoscope": _horoscope, "shichuu": _shichuu, "biorhythm": _biorhythm,
        "blood": _blood, "tarot": _tarot, "ekikyo": _ekikyo,
    }
    pages.get(page, _home)()

# ===== 相性占い =====
def _compat():
    _back_btn()
    st.markdown("<div class='section-header'>💫 相性占い</div>", unsafe_allow_html=True)
    st.markdown("**🌸 あなた**")
    name1 = st.text_input("ニックネーム", key="m_cn1", placeholder="さくら")
    birth1 = st.date_input("生年月日", key="m_cb1", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    st.markdown("**🌟 相手**")
    name2 = st.text_input("ニックネーム", key="m_cn2", placeholder="たろう")
    birth2 = st.date_input("生年月日", key="m_cb2", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,6,15))
    if st.button("💫 占う", key="m_btn_compat"):
        n1, n2 = name1 or "あなた", name2 or "相手"
        r = calc_compatibility(n1, birth1, n2, birth2)
        st.markdown(f"""<div class='score-box'>
            <div style='color:#c9a0ff;'>総合相性スコア</div>
            <div class='score-num'>{r['total']}点</div>
            <div style='color:#a090c0;'>{r['total_comment']}</div>
        </div>""", unsafe_allow_html=True)
        axes = ["シンクロ","価値観","ノリ","ミライ","運命"]
        scores = [r['synchro'],r['values'],r['vibe'],r['future'],r['fate']]
        fig = go.Figure(data=go.Scatterpolar(
            r=scores+[scores[0]], theta=axes+[axes[0]],
            fill='toself', fillcolor='rgba(155,109,255,0.3)',
            line=dict(color='#9b6dff',width=2), marker=dict(color='#f0c040',size=7)
        ))
        fig.update_layout(
            polar=dict(bgcolor='rgba(20,10,40,0.8)',
                radialaxis=dict(visible=True,range=[0,100],tickfont=dict(color='#a090c0'),gridcolor='rgba(150,100,255,0.2)'),
                angularaxis=dict(tickfont=dict(color='#d4b8ff',size=12),gridcolor='rgba(150,100,255,0.2)')),
            paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
            height=300, margin=dict(t=20,b=20,l=40,r=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        for title, key, score in [
            ("💫 シンクロ","synchro",r['synchro']),("🧭 価値観","values",r['values']),
            ("🎉 ノリ","vibe",r['vibe']),("🌱 ミライ","future",r['future']),("🔮 運命","fate",r['fate']),
        ]:
            c = "#9b6dff" if score>=70 else "#f0c040" if score>=50 else "#e06060"
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#c9a0ff;font-weight:bold;'>{title}</span>
                <span style='float:right;color:{c};font-weight:bold;'>{score}点</span>
                <div style='clear:both;margin-top:6px;color:#c8b8e0;font-size:14px;'>{r[key+'_advice']}</div>
            </div>""", unsafe_allow_html=True)

# ===== 星座占い =====
def _zodiac():
    _back_btn()
    st.markdown("<div class='section-header'>⭐ 星座占い</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_zb", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,4,1))
    if st.button("⭐ 占う", key="m_btn_z"):
        today = date.today()
        zodiac = get_zodiac(birth)
        r = get_daily_fortune(zodiac, today)
        st.markdown(f"## {zodiac}")
        st.markdown(f"""<div class='card'>
            <span style='color:#a090c0;'>属性：</span>{ZODIAC_ELEMENT[zodiac]}
            <span style='color:#a090c0;'>キーワード：</span>{ZODIAC_KEYWORD[zodiac]}
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='score-box'>
            <div style='color:#c9a0ff;'>総合運</div>
            <div class='score-num'>{r['total']}点</div>
            <div style='color:#f0c040;'>🍀 {r['lucky_color']}　🔢 {r['lucky_number']}</div>
        </div>""", unsafe_allow_html=True)
        for area, icon in [("恋愛","💕"),("仕事","💼"),("金運","💰"),("健康","💪")]:
            s = r[area]['score']
            c = "#9b6dff" if s>=75 else "#f0c040" if s>=55 else "#e06060"
            stars = "★"*(s//20)+"☆"*(5-s//20)
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#c9a0ff;font-weight:bold;'>{icon} {area}</span>
                <span style='float:right;color:{c};'>{stars}</span>
                <div style='clear:both;margin-top:6px;color:#c8b8e0;font-size:14px;'>{r[area]['advice']}</div>
            </div>""", unsafe_allow_html=True)

# ===== 数秘術 =====
def _numerology():
    _back_btn()
    st.markdown("<div class='section-header'>🔢 数秘術</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_nb", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("🔢 占う", key="m_btn_n"):
        r = get_numerology_full(birth)
        st.markdown(f"""<div class='score-box'>
            <div style='color:#f0c040;font-size:26px;font-weight:bold;'>{r['life_path']} — {r['name']}</div>
            <div style='color:#c8b8e0;margin-top:10px;font-size:14px;line-height:1.7;'>{r['personality']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='advice-box'>
            <span style='color:#c9a0ff;font-weight:bold;'>{date.today().year}年 パーソナルイヤー：{r['personal_year']}</span>
            <div style='margin-top:8px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['personal_year_meaning']}</div>
        </div>""", unsafe_allow_html=True)

# ===== 九星気学 =====
def _kyusei():
    _back_btn()
    st.markdown("<div class='section-header'>☯️ 九星気学</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_kb", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("☯️ 占う", key="m_btn_k"):
        r = get_kyusei_fortune(birth, date.today())
        st.markdown(f"## 本命星：{r['star_name']}")
        st.markdown(f"""<div class='card'>五行：{r['element']}　キーワード：{r['keyword']}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='advice-box'>
            <span style='color:#c9a0ff;font-weight:bold;'>性格</span>
            <div style='margin-top:6px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['personality']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='score-box'>
            <div style='color:#f0c040;font-size:20px;'>🧭 吉方位：{r['lucky_direction']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='advice-box'>
            <span style='color:#c9a0ff;font-weight:bold;'>{r['year']}年の運勢</span>
            <div style='margin-top:6px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['year_fortune']}</div>
        </div>""", unsafe_allow_html=True)

# ===== 動物占い =====
def _animal():
    _back_btn()
    st.markdown("<div class='section-header'>🐾 動物占い</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_ab", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("🐾 占う", key="m_btn_a"):
        r = get_animal_fortune(birth)
        st.markdown(f"""<div class='score-box'>
            <div style='font-size:32px;font-weight:bold;color:#f0c040;'>{r['animal']}</div>
            <div style='color:#c9a0ff;font-size:16px;margin-top:6px;'>{r['sub_type']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='advice-box'>
            <span style='color:#c9a0ff;font-weight:bold;'>特徴</span>
            <div style='margin-top:6px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['personality']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='advice-box'>
            <span style='color:#c9a0ff;font-weight:bold;'>{r['sub_type']}の特徴</span>
            <div style='margin-top:6px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['sub_personality']}</div>
        </div>""", unsafe_allow_html=True)

# ===== 姓名判断 =====
def _seimei():
    _back_btn()
    st.markdown("<div class='section-header'>✍️ 姓名判断</div>", unsafe_allow_html=True)
    surname = st.text_input("苗字", key="m_ss", placeholder="山田")
    surname_strokes = st.number_input("苗字の総画数", key="m_ss2", min_value=1, max_value=81, value=12)
    given = st.text_input("名前", key="m_sg", placeholder="太郎")
    given_strokes = st.number_input("名前の総画数", key="m_sg2", min_value=1, max_value=81, value=14)
    if st.button("✍️ 占う", key="m_btn_s"):
        r = get_seimei_fortune(int(surname_strokes), int(given_strokes))
        luck_color = {"大吉":"#f0c040","最高運":"#ff6090","吉":"#9b6dff","小吉":"#60b0f0","努力運":"#a0a0a0"}
        overall_color = luck_color.get(r['overall'],"#a0a0a0")
        full = f"{surname} {given}" if surname and given else "入力された名前"
        st.markdown(f"""<div class='score-box'>
            <div style='color:#c9a0ff;'>{full}</div>
            <div style='font-size:36px;font-weight:bold;color:{overall_color};'>{r['overall']}</div>
            <div style='color:#a090c0;'>吉数：{r['lucky_count']}格 / 5格</div>
        </div>""", unsafe_allow_html=True)
        for label, data, desc in [
            ("天格",r['tenkaku'],"祖先から受け継いだ運勢"),
            ("地格",r['chikaku'],"才能・幼少〜中年期の運"),
            ("人格",r['jinkaku'],"社会的な運勢（最重要）"),
            ("外格",r['sotokaku'],"対人関係・社会的環境"),
            ("総格",r['sokaku'],"人生全体・晩年の運"),
        ]:
            lc = luck_color.get(data['luck'],"#a0a0a0")
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#c9a0ff;font-weight:bold;'>{label}（{data['value']}画）</span>
                <span style='float:right;color:{lc};font-weight:bold;'>{data['luck']}</span>
                <div style='clear:both;color:#a090c0;font-size:11px;'>{desc}</div>
                <div style='margin-top:4px;color:#c8b8e0;font-size:13px;'>{data['desc']}</div>
            </div>""", unsafe_allow_html=True)

# ===== ホロスコープ =====
def _horoscope():
    _back_btn()
    st.markdown("<div class='section-header'>🌌 ホロスコープ</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_hb", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,4,5))
    hour = st.slider("出生時刻", 0, 23, 12, key="m_hh", format="%d時")
    if st.button("🌌 読み解く", key="m_btn_h"):
        r = get_horoscope(birth, hour)
        st.markdown(f"""<div class='score-box'>
            <div style='font-size:16px;color:#f0c040;'>☉ {r['sun_sign']}　☽ {r['moon_sign']}　↑ {r['ascendant']['sign']}</div>
            <div style='color:#a090c0;margin-top:6px;font-size:13px;'>支配：{r['dominant_element']}　{r['dominant_sign']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("**🪐 天体配置**")
        for planet in ["太陽","月","水星","金星","火星","木星","土星"]:
            p = r['planets'][planet]
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#f0c040;font-weight:bold;'>{p['planet_symbol']} {planet}</span>
                <span style='color:#c9a0ff;margin-left:8px;'>{p['sign']} {p['degree']}°</span>
                <span style='color:#a090c0;font-size:11px;margin-left:6px;'>第{p['house']}H</span>
                <div style='margin-top:4px;color:#c8b8e0;font-size:13px;'>{p['sign_meaning']}</div>
            </div>""", unsafe_allow_html=True)
        if r['aspects']:
            st.markdown("**🔗 アスペクト**")
            ac = {"調和":"#9b6dff","緊張":"#e06060","強化":"#f0c040"}
            for asp in r['aspects'][:5]:
                c = ac.get(asp['type'],"#a090c0")
                st.markdown(f"""<div class='card' style='padding:8px 12px;'>
                    <span style='color:{c};font-weight:bold;'>{asp['p1']} × {asp['p2']}</span>
                    <span style='color:#c9a0ff;margin-left:8px;font-size:13px;'>{asp['angle']}</span>
                    <span style='color:{c};font-size:12px;margin-left:6px;'>【{asp['type']}】</span>
                </div>""", unsafe_allow_html=True)

# ===== 四柱推命 =====
def _shichuu():
    _back_btn()
    st.markdown("<div class='section-header'>🀄 四柱推命</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_shb", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("🀄 占う", key="m_btn_sh"):
        from logic import get_shichuu as _gs
        r = _gs(birth)
        st.markdown(f"""<div class='score-box'>
            <div style='font-size:22px;color:#f0c040;font-weight:bold;'>本命五行：{r['honmei_gogyo']}（{r['honmei_inyo']}）</div>
            <div style='color:#c8b8e0;margin-top:10px;font-size:14px;'>{r['personality']}</div>
        </div>""", unsafe_allow_html=True)
        for label, val in [("年柱",r['year_pillar']),("月柱",r['month_pillar']),("日柱",r['day_pillar'])]:
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#c9a0ff;font-weight:bold;'>{label}</span>
                <span style='float:right;color:#f0c040;font-size:22px;font-weight:bold;'>{val}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='advice-box'>
            <span style='color:#c9a0ff;font-weight:bold;'>{date.today().year}年の運勢</span>
            <div style='margin-top:6px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['year_luck']}</div>
        </div>""", unsafe_allow_html=True)

# ===== バイオリズム =====
def _biorhythm():
    _back_btn()
    st.markdown("<div class='section-header'>📈 バイオリズム</div>", unsafe_allow_html=True)
    birth = st.date_input("生年月日", key="m_biob", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    target = st.date_input("調べたい日", key="m_biot", value=date.today())
    if st.button("📈 見る", key="m_btn_bio"):
        r = get_biorhythm(birth, target)
        for label, val, lbl, color in [
            ("💪 身体（23日）",r['physical'],r['physical_label'],r['physical_color']),
            ("💝 感情（28日）",r['emotional'],r['emotional_label'],r['emotional_color']),
            ("🧠 知性（33日）",r['intellectual'],r['intellectual_label'],r['intellectual_color']),
        ]:
            pct = int((val+1)/2*100)
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#c9a0ff;font-weight:bold;'>{label}</span>
                <span style='float:right;color:{color};font-weight:bold;'>{lbl}</span>
                <div style='background:#2a1a4a;border-radius:4px;height:12px;margin-top:10px;'>
                    <div style='background:{color};width:{pct}%;height:12px;border-radius:4px;'></div>
                </div>
            </div>""", unsafe_allow_html=True)
        hist = r['history']
        dates = [h['date'].strftime('%m/%d') for h in hist]
        fig = go.Figure()
        for key, name, color in [('physical','身体','#9b6dff'),('emotional','感情','#ff90b0'),('intellectual','知性','#60c0d0')]:
            fig.add_trace(go.Scatter(x=dates, y=[h[key] for h in hist], name=name, line=dict(color=color,width=2), mode='lines'))
        fig.add_hline(y=0, line_dash="dash", line_color="#5a3d8a")
        fig.add_vline(x=dates[15], line_dash="dot", line_color="#f0c040")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,5,30,0.8)',
            xaxis=dict(tickfont=dict(color='#a090c0',size=10), gridcolor='rgba(100,80,160,0.2)', tickangle=45),
            yaxis=dict(tickfont=dict(color='#a090c0'), range=[-1.1,1.1], gridcolor='rgba(100,80,160,0.2)'),
            legend=dict(font=dict(color='#c9a0ff',size=11)),
            margin=dict(t=10,b=40,l=30,r=10), height=220,
        )
        st.plotly_chart(fig, use_container_width=True)

# ===== 血液型 =====
def _blood():
    _back_btn()
    st.markdown("<div class='section-header'>🩸 血液型占い</div>", unsafe_allow_html=True)
    blood = st.selectbox("あなたの血液型", ["A","B","O","AB"], key="m_bl")
    use_partner = st.checkbox("相手との相性も見る", key="m_blp")
    partner = None
    if use_partner:
        partner = st.selectbox("相手の血液型", ["A","B","O","AB"], key="m_blp2")
    if st.button("🩸 占う", key="m_btn_bl"):
        r = get_blood_fortune(blood, partner)
        st.markdown(f"## {blood}型：{r['title']}")
        st.markdown(f"""<div class='advice-box'>
            <div style='color:#c8b8e0;font-size:14px;line-height:1.7;'>{r['desc']}</div>
        </div>""", unsafe_allow_html=True)
        for label, val in [("✨ 強み",r['strength']),("⚠️ 弱み",r['weakness']),
                            ("🎨 ラッキーカラー",r['lucky_color']),("💕 恋愛傾向",r['love'])]:
            st.markdown(f"""<div class='advice-box'>
                <span style='color:#c9a0ff;font-weight:bold;'>{label}</span>
                <div style='margin-top:4px;color:#c8b8e0;font-size:14px;'>{val}</div>
            </div>""", unsafe_allow_html=True)
        if partner and 'compat_score' in r:
            sc = r['compat_score']
            bc = "#9b6dff" if sc>=75 else "#f0c040" if sc>=55 else "#e06060"
            st.markdown(f"""<div class='score-box' style='margin-top:12px;'>
                <div style='color:#c9a0ff;'>{blood}型 × {partner}型</div>
                <div class='score-num' style='color:{bc};'>{sc}点</div>
                <div style='color:#c8b8e0;font-size:14px;margin-top:6px;'>{r['compat_desc']}</div>
            </div>""", unsafe_allow_html=True)

# ===== タロット =====
def _tarot():
    _back_btn()
    st.markdown("<div class='section-header'>🃏 タロット</div>", unsafe_allow_html=True)
    spread = st.selectbox("スプレッド", list(SPREAD_TYPES.keys()), key="m_ts")
    if st.button("🃏 引く", key="m_btn_t"):
        import time as _t
        cards = draw_tarot(SPREAD_TYPES[spread], seed=int(_t.time()*1000)%100000)
        for card, pos in zip(cards, SPREAD_POSITIONS[SPREAD_TYPES[spread]]):
            direction = "逆位置 🔄" if card['is_reversed'] else "正位置 ✨"
            dc = "#e06060" if card['is_reversed'] else "#9b6dff"
            meaning = card['reversed'] if card['is_reversed'] else card['upright']
            st.markdown(f"""<div class='card'>
                <div style='display:flex;align-items:center;gap:10px;'>
                    <div style='font-size:32px;'>{card['symbol']}</div>
                    <div>
                        <div style='color:#a090c0;font-size:12px;'>{pos}</div>
                        <div style='color:#f0c040;font-size:16px;font-weight:bold;'>{card['num']}. {card['name']}</div>
                        <div style='color:{dc};font-size:12px;'>{direction}</div>
                    </div>
                </div>
                <div style='margin-top:10px;color:#c8b8e0;font-size:14px;line-height:1.7;'>{meaning}</div>
            </div>""", unsafe_allow_html=True)

# ===== 易経 =====
def _ekikyo():
    _back_btn()
    st.markdown("<div class='section-header'>☯ 易経</div>", unsafe_allow_html=True)
    question = st.text_input("問い（任意）", key="m_eq", placeholder="例：今の仕事を続けるべきか？")
    if st.button("☯ 卦を立てる", key="m_btn_e"):
        import time as _t
        hex_r = draw_hexagram(seed=int(_t.time()*1000)%100000)
        if question:
            st.markdown(f"<p style='color:#a090c0;font-size:13px;'>問い：{question}</p>", unsafe_allow_html=True)
        st.markdown(f"""<div class='score-box'>
            <div style='font-size:24px;font-weight:bold;color:#f0c040;'>第{hex_r['number']}卦 {hex_r['kanji']}</div>
            <div style='color:#c9a0ff;font-size:16px;margin-top:4px;'>{hex_r['name']} — {hex_r['theme']}</div>
            <div style='color:#c8b8e0;margin-top:10px;font-size:14px;line-height:1.8;'>{hex_r['message']}</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("**六爻**")
        cols = st.columns(6)
        for i, (line_val, col) in enumerate(zip(reversed(hex_r['lines']), cols)):
            is_changing = (6-i) in hex_r['changing_lines']
            color = "#f0c040" if is_changing else "#c9a0ff"
            symbol = "━━" if line_val=="陽" else "━ ━"
            col.markdown(f"""<div style='text-align:center;padding:6px;background:rgba(60,40,100,0.4);border-radius:6px;'>
                <div style='color:{color};font-size:16px;'>{symbol}</div>
                <div style='color:{color};font-size:10px;'>{line_val}</div>
            </div>""", unsafe_allow_html=True)
