import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from datetime import date
import math
from counter import increment, render_ranking, get_counts
from logic import (
    calc_compatibility, get_zodiac, get_daily_fortune,
    get_numerology_full, get_kyusei_fortune, get_animal_fortune,
    get_seimei_fortune, get_horoscope, get_shichuu, get_biorhythm,
    get_blood_fortune, draw_tarot, draw_hexagram,
    ZODIAC_KEYWORD, ZODIAC_RULING, ZODIAC_ELEMENT, JUNISHI_ANIMAL,
    PLANET_MEANING, HOUSE_MEANING, BLOOD_PERSONALITY, SPREAD_TYPES, SPREAD_POSITIONS,
    CITY_COORDS,
)

st.set_page_config(page_title="無料占いポータル", page_icon="🔮", layout="wide")

# Mobile UA detection
components.html("""
<script>
(function() {
    var ua = navigator.userAgent;
    var isMobile = /iPhone|Android|iPad|Mobile/i.test(ua) && !/iPad/.test(ua) || /Android.*Mobile/.test(ua);
    var params = new URLSearchParams(window.location.search);
    if (isMobile && params.get('mobile') !== '1') {
        params.set('mobile', '1');
        window.location.replace(window.location.pathname + '?' + params.toString());
    } else if (!isMobile && params.get('mobile') === '1') {
        params.delete('mobile');
        var newSearch = params.toString();
        window.location.replace(window.location.pathname + (newSearch ? '?' + newSearch : ''));
    }
})();
</script>
""", height=0)

if st.query_params.get("mobile") == "1":
    from mobile_app import render_mobile
    render_mobile()
    st.stop()

# ===== CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Cinzel:wght@600&display=swap');

/* ===== カラーパレット =====
   BG:      #0d0d18  (深夜の空)
   Surface: #13131f  (カード背景)
   Raised:  #1c1c2e  (サイドバー・ヘッダー)
   Border:  #2a2a42  (境界線)
   Accent:  #6c63ff  (indigo — sparingly)
   Gold:    #f0c040  (スコア・ハイライト)
   Text1:   #e8e6f0  (主要テキスト)
   Text2:   #8e8ca0  (補助テキスト)
   Text3:   #50505e  (ミュート)
   Green:   #10b981  (無料バッジ)
*/

* { font-family: 'Noto Sans JP', sans-serif; box-sizing: border-box; }

.stApp {
    background: #0d0d18;
    color: #e8e6f0;
}

/* ヘッダー */
.site-header {
    background: #0d0d18;
    border-bottom: 1px solid #2a2a42;
    padding: 0 28px;
    display: flex;
    align-items: center;
    gap: 36px;
    height: 58px;
}
.site-logo {
    font-size: 20px;
    font-weight: 700;
    color: #e8e6f0;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.site-logo span { color: #f0c040; }
.header-nav { display: flex; gap: 4px; flex-wrap: wrap; }
.nav-btn {
    padding: 5px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border: none;
    background: transparent;
    color: #8e8ca0;
    transition: all 0.15s;
    white-space: nowrap;
}
.nav-btn:hover { background: #1c1c2e; color: #e8e6f0; }
.nav-btn.active { background: #1c1c2e; color: #f0c040; }

/* ページタイトルバー */
.page-title-bar {
    background: #13131f;
    border-bottom: 1px solid #2a2a42;
    padding: 18px 24px 14px;
}
.page-title-bar h1 {
    color: #e8e6f0;
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 3px 0;
}
.page-title-bar p {
    color: #8e8ca0;
    font-size: 13px;
    margin: 0;
}

/* 占いカード */
.fortune-card {
    background: #13131f;
    border: 1px solid #2a2a42;
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    cursor: pointer;
    height: 100%;
}
.fortune-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.5);
    border-color: #6c63ff;
}
.card-thumb {
    height: 108px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 52px;
    position: relative;
}
.card-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    background: #10b981;
    color: white;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 4px;
    letter-spacing: 0.5px;
}
.card-body { padding: 14px 14px 16px; }
.card-meta { margin-bottom: 6px; }
.card-title {
    color: #e8e6f0;
    font-size: 15px;
    font-weight: 700;
    line-height: 1.4;
    margin-bottom: 6px;
}
.card-desc { color: #8e8ca0; font-size: 12px; line-height: 1.65; }

/* 占い詳細ページ */
.detail-header {
    background: #13131f;
    border: 1px solid #2a2a42;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.detail-icon { font-size: 52px; }
.detail-title { font-size: 22px; font-weight: 700; color: #e8e6f0; margin-bottom: 4px; }
.detail-subtitle { color: #8e8ca0; font-size: 14px; }

/* スコアボックス */
.score-box {
    background: #13131f;
    border: 1px solid #2a2a42;
    border-radius: 12px;
    padding: 28px 24px;
    text-align: center;
    margin: 14px 0;
}
.score-num { font-size: 56px; font-weight: 700; color: #f0c040; }

/* アドバイスボックス */
.advice-box {
    background: #13131f;
    border: 1px solid #2a2a42;
    border-left: 3px solid #6c63ff;
    padding: 14px 16px;
    margin: 8px 0;
    border-radius: 0 8px 8px 0;
}

/* 結果カード */
.result-card {
    background: #13131f;
    border: 1px solid #2a2a42;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
}

/* サイドバー */
.sidebar-section {
    background: #13131f;
    border: 1px solid #2a2a42;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.sidebar-title {
    color: #e8e6f0;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2a2a42;
}
.sidebar-item {
    color: #8e8ca0;
    font-size: 13px;
    padding: 5px 0;
    cursor: pointer;
    transition: color 0.15s;
}
.sidebar-item:hover { color: #e8e6f0; }

/* Streamlit要素の上書き */
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }
header[data-testid="stHeader"] { display: none; }
.stButton>button {
    background: #6c63ff;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 32px;
    font-size: 14px;
    font-weight: 600;
    width: 100%;
    transition: opacity 0.15s, transform 0.1s;
}
.stButton>button:hover { opacity: 0.88; transform: translateY(-1px); }
.stButton>button:active { transform: translateY(0); }
[data-testid="stBaseButton-secondary"]>button {
    background: #1c1c2e !important;
    border: 1px solid #2a2a42 !important;
    color: #8e8ca0 !important;
}
[data-testid="stBaseButton-secondary"]>button:hover {
    border-color: #6c63ff !important;
    color: #e8e6f0 !important;
}
.stTabs [data-baseweb="tab"] { color: #8e8ca0; font-size: 13px; }
.stTabs [aria-selected="true"] { color: #f0c040; border-bottom-color: #f0c040; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background: #1c1c2e !important;
    border: 1px solid #2a2a42 !important;
    color: #e8e6f0 !important;
    border-radius: 8px !important;
}
[data-testid="stDateInput"] input {
    background: #1c1c2e !important;
    border: 1px solid #2a2a42 !important;
    color: #e8e6f0 !important;
}
[data-baseweb="select"] > div {
    background: #1c1c2e !important;
    border: 1px solid #2a2a42 !important;
    color: #e8e6f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ===== 占いメタデータ =====
FORTUNE_META = [
    {
        "key": "compat", "icon": "💫", "title": "相性占い",
        "subtitle": "2人の関係性を5軸で徹底分析",
        "desc": "生年月日から相性スコアをレーダーチャートで可視化。シンクロ・価値観・ノリ・ミライ・運命の5軸で診断します。",
        "tags": ["恋愛", "二人用"], "badge": "完全無料",
    },
    {
        "key": "zodiac", "icon": "⭐", "title": "星座占い",
        "subtitle": "今日の運勢を4つのエリアで鑑定",
        "desc": "恋愛・仕事・金運・健康の今日の運勢をスコアとアドバイスで。ラッキーカラー・ラッキーナンバーもわかります。",
        "tags": ["総合運", "一人用"], "badge": "完全無料",
    },
    {
        "key": "numerology", "icon": "🔢", "title": "数秘術",
        "subtitle": "ライフパスナンバーで本質を解読",
        "desc": "生年月日の数字が示すあなたの本質と才能。パーソナルイヤーナンバーで今年の運気の流れもわかります。",
        "tags": ["性格", "一人用"], "badge": "完全無料",
    },
    {
        "key": "kyusei", "icon": "☯️", "title": "九星気学",
        "subtitle": "本命星・吉方位・今年の運勢",
        "desc": "東洋の伝統占術。あなたの本命星から性格・吉方位・今年の運気スコアまで総合的に鑑定します。",
        "tags": ["総合運", "一人用"], "badge": "完全無料",
    },
    {
        "key": "animal", "icon": "🐾", "title": "動物占い",
        "subtitle": "12動物×5サブタイプ＝60種類の性格診断",
        "desc": "干支をベースにした性格診断。60種類の動物タイプのうちあなたはどれ？サブタイプで詳細な性格も判明。",
        "tags": ["性格", "一人用"], "badge": "完全無料",
    },
    {
        "key": "seimei", "icon": "✍️", "title": "姓名判断",
        "subtitle": "五格（天格・地格・人格・外格・総格）で鑑定",
        "desc": "苗字と名前の画数から天格・地格・人格・外格・総格の五格を算出。名前が持つ運命の力を読み解きます。",
        "tags": ["性格", "一人用"], "badge": "完全無料",
    },
    {
        "key": "horoscope", "icon": "🌌", "title": "ホロスコープ",
        "subtitle": "9天体の配置で本格天宮図を作成",
        "desc": "太陽・月・水星ほか9天体の正確な配置を計算。アスペクト分析と天宮図チャートで深く読み解きます。",
        "tags": ["性格", "一人用"], "badge": "完全無料",
    },
    {
        "key": "shichuu", "icon": "🀄", "title": "四柱推命",
        "subtitle": "年柱・月柱・日柱と五行バランスを解析",
        "desc": "東洋占術の王様。生年月日から三柱と五行バランスを算出し、本命五行と今年の運勢を鑑定します。",
        "tags": ["総合運", "一人用"], "badge": "完全無料",
    },
    {
        "key": "biorhythm", "icon": "📈", "title": "バイオリズム",
        "subtitle": "身体・感情・知性の3周期でコンディション分析",
        "desc": "身体(23日)・感情(28日)・知性(33日)の3つの生体リズムを30日グラフで表示。今日の状態を把握できます。",
        "tags": ["健康", "一人用"], "badge": "完全無料",
    },
    {
        "key": "blood", "icon": "🩸", "title": "血液型占い",
        "subtitle": "性格診断＋2人の相性スコア",
        "desc": "血液型別の詳細な性格診断と相性スコア。強み・弱み・恋愛傾向・ラッキーカラーがわかります。",
        "tags": ["性格", "恋愛"], "badge": "完全無料",
    },
    {
        "key": "tarot", "icon": "🃏", "title": "タロット",
        "subtitle": "大アルカナ22枚・3種のスプレッド",
        "desc": "大アルカナ22枚によるタロット占い。1枚引き・3枚・5枚スプレッドから選べます。正位置・逆位置も対応。",
        "tags": ["恋愛", "一人用"], "badge": "完全無料",
    },
    {
        "key": "ekikyo", "icon": "☯", "title": "易経",
        "subtitle": "六十四卦・六爻・変爻で深く鑑定",
        "desc": "中国最古の占い。64卦すべてに対応し、六爻の変爻まで読み解きます。心の問いへの深い洞察を得られます。",
        "tags": ["人生", "一人用"], "badge": "完全無料",
    },
]

CAT_LABELS = ["すべて", "恋愛", "性格", "総合運", "健康", "人生"]

# ===== ナビゲーション =====
NAV_ITEMS = [
    ("home", "🏠 ホーム"),
    ("new", "✨ 新着占い"),
    ("today", "📅 今日の運勢"),
    ("free", "🎁 無料占い"),
    ("ranking", "🏆 ランキング"),
]

def get_page():
    return st.query_params.get("p", "home")

def go_page(p, key=None):
    params = dict(st.query_params)
    params["p"] = p
    if key:
        params["fortune"] = key
    else:
        params.pop("fortune", None)
    st.query_params.update(params)

# ===== ヘッダー =====
current_page = get_page()
nav_html = "".join([
    f'<span class="nav-btn{" active" if current_page == k else ""}">{label}</span>'
    for k, label in NAV_ITEMS
])
st.markdown(f"""
<div class="site-header">
    <div class="site-logo">✨ <span>天啓館</span></div>
    <div class="header-nav">{nav_html}</div>
</div>
""", unsafe_allow_html=True)

# ナビボタンのクリック（Streamlitボタンで実装）
nav_cols = st.columns(len(NAV_ITEMS))
for i, (k, label) in enumerate(NAV_ITEMS):
    with nav_cols[i]:
        if st.button(label, key=f"nav_{k}", use_container_width=True):
            go_page(k)
            st.rerun()

st.markdown("<hr style='border-color:#2a2a42;margin:0;'>", unsafe_allow_html=True)

# ===== ページルーティング =====
current_page = get_page()
fortune_key = st.query_params.get("fortune", "")

# ===== 占い詳細ページ =====
if fortune_key:
    meta = next((m for m in FORTUNE_META if m["key"] == fortune_key), None)
    if meta:
        if st.button("← 占い一覧に戻る", key="back_to_list"):
            go_page(current_page)
            st.rerun()

        st.markdown(f"""
        <div class="detail-header">
            <div class="detail-icon">{meta['icon']}</div>
            <div>
                <div class="detail-title">{meta['title']}</div>
                <div class="detail-subtitle">{meta['subtitle']}</div>
                <div style="margin-top:8px;">
                    {''.join(f'<span style="background:#1c1c2e;color:#6c63ff;font-size:11px;padding:2px 10px;border-radius:10px;margin-right:6px;">{t}</span>' for t in meta['tags'])}
                    <span style="background:#0e3020;color:#20c070;font-size:11px;padding:2px 10px;border-radius:10px;">{meta['badge']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ===== 各占いフォーム =====
        if fortune_key == "compat":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🌸 あなた**")
                name1 = st.text_input("ニックネーム", key="c_name1", placeholder="さくら")
                birth1 = st.date_input("生年月日", key="c_birth1", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
            with col2:
                st.markdown("**🌟 相手**")
                name2 = st.text_input("ニックネーム", key="c_name2", placeholder="たろう")
                birth2 = st.date_input("生年月日", key="c_birth2", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,6,15))
            if st.button("💫 占う", key="btn_compat"):
                increment("compat")
                n1, n2 = name1 or "あなた", name2 or "相手"
                r = calc_compatibility(n1, birth1, n2, birth2)
                st.markdown(f"## ✨ {n1} × {n2} の相性結果")
                st.markdown(f"""<div class="score-box">
                    <div style="color:#c9a0ff;">総合相性スコア</div>
                    <div class="score-num">{r['total']}点</div>
                    <div style="color:#8e8ca0;">{r['total_comment']}</div>
                </div>""", unsafe_allow_html=True)
                axes = ["シンクロ","価値観","ノリ","ミライ","運命"]
                scores = [r['synchro'],r['values'],r['vibe'],r['future'],r['fate']]
                fig = go.Figure(data=go.Scatterpolar(
                    r=scores+[scores[0]], theta=axes+[axes[0]],
                    fill='toself', fillcolor='rgba(160,80,255,0.25)',
                    line=dict(color='#6c63ff',width=2), marker=dict(color='#f0c040',size=8)
                ))
                fig.update_layout(
                    polar=dict(bgcolor='rgba(20,10,40,0.9)',
                        radialaxis=dict(visible=True,range=[0,100],tickfont=dict(color='#706090'),gridcolor='rgba(108,99,255,0.15)'),
                        angularaxis=dict(tickfont=dict(color='#c0a0e0',size=13),gridcolor='rgba(108,99,255,0.15)')),
                    paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=40,b=40,l=60,r=60)
                )
                st.plotly_chart(fig, use_container_width=True)
                for title, key, score in [
                    ("💫 シンクロ","synchro",r['synchro']),("🧭 価値観","values",r['values']),
                    ("🎉 ノリ","vibe",r['vibe']),("🌱 ミライ","future",r['future']),("🔮 運命","fate",r['fate']),
                ]:
                    c = "#6c63ff" if score>=70 else "#f0c040" if score>=50 else "#e06060"
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#c8c5e0;font-weight:700;">{title}</span>
                        <span style="float:right;color:{c};font-size:20px;font-weight:700;">{score}点</span>
                        <div style="clear:both;margin-top:8px;color:#8e8ca0;">{r[key+'_advice']}</div>
                    </div>""", unsafe_allow_html=True)
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"**{n1}**")
                    st.markdown(f"- 星座：{r['zodiac1']}\n- 数秘：{r['life_path1']}\n- 九星：{r['kyusei1']}\n- 干支：{r['junishi1']}\n- 五行：{r['gogyo1']}")
                with cb:
                    st.markdown(f"**{n2}**")
                    st.markdown(f"- 星座：{r['zodiac2']}\n- 数秘：{r['life_path2']}\n- 九星：{r['kyusei2']}\n- 干支：{r['junishi2']}\n- 五行：{r['gogyo2']}")

        elif fortune_key == "zodiac":
            birth_z = st.date_input("生年月日", key="z_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,4,1))
            if st.button("⭐ 占う", key="btn_zodiac"):
                increment("zodiac")
                zodiac = get_zodiac(birth_z)
                r = get_daily_fortune(zodiac, date.today())
                st.markdown(f"## {zodiac}")
                st.markdown(f"""<div class="result-card">
                    <span style="color:#8e8ca0;">属性：</span><b style="color:#e0d0ff;">{ZODIAC_ELEMENT[zodiac]}</b>
                    <span style="color:#8e8ca0;">支配星：</span><b style="color:#e0d0ff;">{ZODIAC_RULING[zodiac]}</b>
                    <span style="color:#8e8ca0;">キーワード：</span><b style="color:#e0d0ff;">{ZODIAC_KEYWORD[zodiac]}</b>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="score-box">
                    <div style="color:#c8c5e0;">総合運</div>
                    <div class="score-num">{r['total']}点</div>
                    <div style="color:#f0c040;">🍀 {r['lucky_color']}　🔢 {r['lucky_number']}</div>
                </div>""", unsafe_allow_html=True)
                for area, icon in [("恋愛","💕"),("仕事","💼"),("金運","💰"),("健康","💪")]:
                    s = r[area]['score']
                    c = "#6c63ff" if s>=75 else "#f0c040" if s>=55 else "#e06060"
                    stars = "★"*(s//20)+"☆"*(5-s//20)
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#c8c5e0;font-weight:700;">{icon} {area}</span>
                        <span style="float:right;color:{c};">{stars} {s}点</span>
                        <div style="clear:both;margin-top:8px;color:#8e8ca0;">{r[area]['advice']}</div>
                    </div>""", unsafe_allow_html=True)

        elif fortune_key == "numerology":
            birth_n = st.date_input("生年月日", key="n_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
            if st.button("🔢 占う", key="btn_num"):
                increment("numerology")
                r = get_numerology_full(birth_n)
                st.markdown(f"""<div class="score-box">
                    <div style="color:#f0c040;font-size:30px;font-weight:700;">{r['life_path']} — {r['name']}</div>
                    <div style="color:#8e8ca0;margin-top:12px;line-height:1.7;">{r['personality']}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="advice-box">
                    <span style="color:#c8c5e0;font-weight:700;">{date.today().year}年 パーソナルイヤー：{r['personal_year']}</span>
                    <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r['personal_year_meaning']}</div>
                </div>""", unsafe_allow_html=True)

        elif fortune_key == "kyusei":
            birth_k = st.date_input("生年月日", key="k_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
            if st.button("☯️ 占う", key="btn_kyusei"):
                increment("kyusei")
                r = get_kyusei_fortune(birth_k, date.today())
                st.markdown(f"## 本命星：{r['star_name']}")
                st.markdown(f"""<div class="result-card">五行：{r['element']}　キーワード：{r['keyword']}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="advice-box">
                    <span style="color:#c8c5e0;font-weight:700;">性格・特徴</span>
                    <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r['personality']}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="score-box">
                    <div style="color:#f0c040;font-size:22px;">🧭 吉方位：{r['lucky_direction']}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="advice-box">
                    <span style="color:#c8c5e0;font-weight:700;">{r['year']}年の運勢</span>
                    <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r['year_fortune']}</div>
                </div>""", unsafe_allow_html=True)

        elif fortune_key == "animal":
            birth_a = st.date_input("生年月日", key="a_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
            if st.button("🐾 占う", key="btn_animal"):
                increment("animal")
                r = get_animal_fortune(birth_a)
                st.markdown(f"""<div class="score-box">
                    <div style="font-size:40px;font-weight:700;color:#f0c040;">{r['animal']}</div>
                    <div style="color:#c8c5e0;font-size:18px;margin-top:6px;">{r['sub_type']}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="advice-box">
                    <span style="color:#c8c5e0;font-weight:700;">🐾 動物の特徴</span>
                    <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r['personality']}</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="advice-box">
                    <span style="color:#c8c5e0;font-weight:700;">🧠 {r['sub_type']}の特徴</span>
                    <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r['sub_personality']}</div>
                </div>""", unsafe_allow_html=True)

        elif fortune_key == "seimei":
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                surname = st.text_input("苗字", key="s_surname", placeholder="山田")
                surname_strokes = st.number_input("苗字の総画数", key="s_strokes1", min_value=1, max_value=81, value=12)
            with col_s2:
                given = st.text_input("名前", key="s_given", placeholder="太郎")
                given_strokes = st.number_input("名前の総画数", key="s_strokes2", min_value=1, max_value=81, value=14)
            st.caption("※ 画数は漢字辞典の旧字体画数を使用してください")
            if st.button("✍️ 占う", key="btn_seimei"):
                increment("seimei")
                r = get_seimei_fortune(int(surname_strokes), int(given_strokes))
                luck_color = {"大吉":"#f0c040","最高運":"#ff6090","吉":"#6c63ff","小吉":"#60b0f0","努力運":"#808080"}
                oc = luck_color.get(r['overall'],"#808080")
                st.markdown(f"""<div class="score-box">
                    <div style="color:#8e8ca0;">{surname or ""} {given or ""}</div>
                    <div style="font-size:44px;font-weight:700;color:{oc};">{r['overall']}</div>
                    <div style="color:#8e8ca0;">吉数：{r['lucky_count']}格 / 5格</div>
                </div>""", unsafe_allow_html=True)
                for label, data, desc in [
                    ("天格",r['tenkaku'],"祖先から受け継いだ運勢"),("地格",r['chikaku'],"才能・幼少〜中年期"),
                    ("人格",r['jinkaku'],"社会的な運勢（最重要）"),("外格",r['sotokaku'],"対人関係・社会的環境"),("総格",r['sokaku'],"人生全体・晩年"),
                ]:
                    lc = luck_color.get(data['luck'],"#808080")
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#c8c5e0;font-weight:700;">{label}（{data['value']}画）</span>
                        <span style="float:right;color:{lc};font-weight:700;">{data['luck']}</span>
                        <div style="clear:both;color:#8e8ca0;font-size:11px;">{desc}</div>
                        <div style="margin-top:4px;color:#8e8ca0;">{data['desc']}</div>
                    </div>""", unsafe_allow_html=True)

        elif fortune_key == "horoscope":
            h_birth = st.date_input("生年月日", key="h_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,4,5))
            h_hour = st.slider("出生時刻", 0, 23, 12, key="h_hour", format="%d時")
            h_city = st.selectbox("出生地（都市）", list(CITY_COORDS.keys()), key="h_city")
            if st.button("🌌 ホロスコープを読み解く", key="btn_horo"):
                increment("horoscope")
                r = get_horoscope(h_birth, h_hour, h_city)
                st.markdown(f"""<div class="score-box">
                    <div style="font-size:20px;color:#f0c040;">☉ {r['sun_sign']}　☽ {r['moon_sign']}　↑ {r['ascendant']['sign']}</div>
                    <div style="color:#8e8ca0;margin-top:8px;">支配エレメント：{r['dominant_element']}　支配サイン：{r['dominant_sign']}</div>
                </div>""", unsafe_allow_html=True)
                planet_order = ["太陽","月","水星","金星","火星","木星","土星","天王星","海王星"]
                planet_colors = {"太陽":"#f0c040","月":"#c8c8ff","水星":"#80c080","金星":"#ff90b0",
                                 "火星":"#ff6060","木星":"#f0a030","土星":"#b0b060","天王星":"#60c0d0","海王星":"#6080ff"}
                fig = go.Figure()
                sign_syms = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
                for i, sym in enumerate(sign_syms):
                    angle = math.radians(i*30+15)
                    fig.add_annotation(x=math.cos(angle)*0.82,y=math.sin(angle)*0.82,text=sym,showarrow=False,font=dict(size=16,color="#8040c0"))
                    a0 = math.radians(i*30)
                    fig.add_shape(type="line",x0=math.cos(a0)*0.65,y0=math.sin(a0)*0.65,x1=math.cos(a0)*0.95,y1=math.sin(a0)*0.95,line=dict(color="#2a2a42",width=1))
                sign_list = ["牡羊座","牡牛座","双子座","蟹座","獅子座","乙女座","天秤座","蠍座","射手座","山羊座","水瓶座","魚座"]
                for planet in planet_order:
                    lon = r["planets"][planet]
                    deg = lon["degree"] + sign_list.index(lon["sign"])*30
                    angle = math.radians(deg)
                    fig.add_trace(go.Scatter(x=[math.cos(angle)*0.55],y=[math.sin(angle)*0.55],mode="markers+text",
                        marker=dict(size=14,color=planet_colors[planet]),text=[lon["planet_symbol"]],
                        textposition="top center",textfont=dict(size=11,color=planet_colors[planet]),
                        name=f"{lon['planet_symbol']} {planet}（{lon['sign']}）",
                        hovertemplate=f"<b>{planet}</b><br>{lon['sign']} {lon['degree']}°<br>第{lon['house']}H<extra></extra>"))
                theta_arr = [math.radians(i) for i in range(361)]
                for rv, col in [(0.65,"#2a2a42"),(0.95,"#2a2a42")]:
                    fig.add_trace(go.Scatter(x=[math.cos(t)*rv for t in theta_arr],y=[math.sin(t)*rv for t in theta_arr],
                        mode="lines",line=dict(color=col,width=1),showlegend=False,hoverinfo="skip"))
                fig.update_layout(paper_bgcolor="rgba(13,13,24,0.95)",plot_bgcolor="rgba(13,13,24,0.95)",
                    xaxis=dict(range=[-1.1,1.1],visible=False,scaleanchor="y"),yaxis=dict(range=[-1.1,1.1],visible=False),
                    height=480,showlegend=True,legend=dict(font=dict(color="#c0a0e0",size=11),bgcolor="rgba(0,0,0,0)"),
                    margin=dict(t=20,b=20,l=20,r=20))
                st.plotly_chart(fig, use_container_width=True)
                for planet in planet_order:
                    p = r["planets"][planet]
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#f0c040;font-weight:700;">{p['planet_symbol']} {planet}</span>
                        <span style="color:#c8c5e0;margin-left:8px;">{p['sign']} {p['degree']}°</span>
                        <span style="color:#8e8ca0;font-size:12px;margin-left:8px;">第{p['house']}H</span>
                        <div style="margin-top:6px;color:#8e8ca0;">{p['sign_meaning']}</div>
                    </div>""", unsafe_allow_html=True)
                if r["aspects"]:
                    st.markdown("#### 🔗 主要アスペクト")
                    ac = {"調和":"#6c63ff","緊張":"#e06060","強化":"#f0c040"}
                    for asp in r["aspects"][:8]:
                        c = ac.get(asp["type"],"#9080b0")
                        st.markdown(f"""<div class="result-card" style="padding:10px 16px;">
                            <span style="color:{c};font-weight:700;">{asp['p1']} × {asp['p2']}</span>
                            <span style="color:#c8c5e0;margin-left:8px;">{asp['angle']}</span>
                            <span style="color:{c};font-size:12px;margin-left:8px;">【{asp['type']}】</span>
                        </div>""", unsafe_allow_html=True)

        elif fortune_key == "shichuu":
            sh_birth = st.date_input("生年月日", key="sh_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
            if st.button("🀄 占う", key="btn_shichuu"):
                increment("shichuu")
                r = get_shichuu(sh_birth)
                st.markdown(f"""<div class="score-box">
                    <div style="font-size:24px;color:#f0c040;">本命五行：{r['honmei_gogyo']}（{r['honmei_inyo']}）</div>
                    <div style="color:#8e8ca0;margin-top:8px;">{r['personality']}</div>
                </div>""", unsafe_allow_html=True)
                for label, val in [("年柱（生まれの運）",r['year_pillar']),("月柱（社会・仕事運）",r['month_pillar']),("日柱（本質・パートナー運）",r['day_pillar'])]:
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#c8c5e0;font-weight:700;">{label}</span>
                        <span style="float:right;color:#f0c040;font-size:24px;font-weight:700;">{val}</span>
                    </div>""", unsafe_allow_html=True)
                elem_colors = {"木":"#60c060","火":"#e06060","土":"#c09040","金":"#c0c0c0","水":"#6090f0"}
                cols5 = st.columns(5)
                for i, (elem, count) in enumerate(r['five_elements'].items()):
                    with cols5[i]:
                        st.markdown(f"""<div style="text-align:center;padding:12px;background:#13131f;border:1px solid #2a2a42;border-radius:8px;">
                            <div style="color:{elem_colors[elem]};font-size:20px;font-weight:700;">{elem}</div>
                            <div style="color:#f0c040;">{"●"*count + "○"*(3-count)}</div>
                            <div style="color:#8e8ca0;font-size:12px;">{count}/3</div>
                        </div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="advice-box" style="margin-top:12px;">
                    <span style="color:#c8c5e0;">今年の年五行：<b style="color:#f0c040;">{r['year_gogyo']}</b></span>
                    <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r['year_luck']}</div>
                </div>""", unsafe_allow_html=True)

        elif fortune_key == "biorhythm":
            bio_birth = st.date_input("生年月日", key="bio_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
            bio_target = st.date_input("調べたい日付", key="bio_target", value=date.today())
            if st.button("📈 バイオリズムを見る", key="btn_bio"):
                increment("biorhythm")
                r = get_biorhythm(bio_birth, bio_target)
                for label, val, lbl, color in [
                    ("💪 身体（23日）",r['physical'],r['physical_label'],r['physical_color']),
                    ("💝 感情（28日）",r['emotional'],r['emotional_label'],r['emotional_color']),
                    ("🧠 知性（33日）",r['intellectual'],r['intellectual_label'],r['intellectual_color']),
                ]:
                    pct = int((val+1)/2*100)
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#c8c5e0;font-weight:700;">{label}</span>
                        <span style="float:right;color:{color};font-weight:700;">{lbl}</span>
                        <div style="background:#0f0820;border-radius:4px;height:10px;margin-top:10px;">
                            <div style="background:{color};width:{pct}%;height:10px;border-radius:4px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                hist = r['history']
                dates_list = [h['date'].strftime('%m/%d') for h in hist]
                fig = go.Figure()
                for k, name, color in [('physical','身体','#a050ff'),('emotional','感情','#ff90b0'),('intellectual','知性','#60c0d0')]:
                    fig.add_trace(go.Scatter(x=dates_list,y=[h[k] for h in hist],name=name,line=dict(color=color,width=2),mode='lines'))
                fig.add_hline(y=0,line_dash="dash",line_color="#2a2a42")
                fig.add_vline(x=dates_list[15],line_dash="dot",line_color="#f0c040",annotation_text="今日")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(13,13,24,0.8)',
                    xaxis=dict(tickfont=dict(color='#706090'),gridcolor='rgba(60,40,120,0.2)'),
                    yaxis=dict(tickfont=dict(color='#706090'),range=[-1.1,1.1],gridcolor='rgba(60,40,120,0.2)'),
                    legend=dict(font=dict(color='#c0a0e0')),margin=dict(t=20,b=20,l=40,r=20),height=280)
                st.plotly_chart(fig, use_container_width=True)

        elif fortune_key == "blood":
            bl_blood = st.selectbox("あなたの血液型", ["A","B","O","AB"], key="bl_blood")
            use_partner = st.checkbox("相手との相性も見る", key="bl_use_partner")
            bl_partner = None
            if use_partner:
                bl_partner = st.selectbox("相手の血液型", ["A","B","O","AB"], key="bl_partner")
            if st.button("🩸 占う", key="btn_blood"):
                increment("blood")
                r = get_blood_fortune(bl_blood, bl_partner)
                st.markdown(f"## {bl_blood}型：{r['title']}")
                st.markdown(f"""<div class="advice-box"><div style="color:#8e8ca0;line-height:1.7;">{r['desc']}</div></div>""", unsafe_allow_html=True)
                for label, val in [("✨ 強み",r['strength']),("⚠️ 弱み",r['weakness']),("🎨 ラッキーカラー",r['lucky_color']),("💕 恋愛傾向",r['love'])]:
                    st.markdown(f"""<div class="advice-box">
                        <span style="color:#c8c5e0;font-weight:700;">{label}</span>
                        <div style="margin-top:6px;color:#8e8ca0;">{val}</div>
                    </div>""", unsafe_allow_html=True)
                if bl_partner and 'compat_score' in r:
                    sc = r['compat_score']
                    bc = "#6c63ff" if sc>=75 else "#f0c040" if sc>=55 else "#e06060"
                    st.markdown(f"""<div class="score-box">
                        <div style="color:#c8c5e0;">{bl_blood}型 × {bl_partner}型 の相性</div>
                        <div class="score-num" style="color:{bc};">{sc}点</div>
                        <div style="color:#8e8ca0;margin-top:8px;">{r['compat_desc']}</div>
                    </div>""", unsafe_allow_html=True)

        elif fortune_key == "tarot":
            spread_name = st.selectbox("スプレッド", list(SPREAD_TYPES.keys()), key="tarot_spread")
            num_cards = SPREAD_TYPES[spread_name]
            if st.button("🃏 カードを引く", key="btn_tarot"):
                increment("tarot")
                import time as _time
                cards = draw_tarot(num_cards, seed=int(_time.time()*1000)%100000)
                for card, pos in zip(cards, SPREAD_POSITIONS[num_cards]):
                    dc = "#e06060" if card['is_reversed'] else "#a050ff"
                    meaning = card['reversed'] if card['is_reversed'] else card['upright']
                    st.markdown(f"""<div class="result-card" style="margin:12px 0;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="font-size:38px;">{card['symbol']}</div>
                            <div>
                                <div style="color:#8e8ca0;font-size:12px;">{pos}</div>
                                <div style="color:#f0c040;font-size:18px;font-weight:700;">{card['num']}. {card['name']}</div>
                                <div style="color:{dc};font-size:13px;">{"逆位置 🔄" if card['is_reversed'] else "正位置 ✨"}</div>
                            </div>
                        </div>
                        <div style="margin-top:10px;color:#8e8ca0;line-height:1.7;">{meaning}</div>
                    </div>""", unsafe_allow_html=True)

        elif fortune_key == "ekikyo":
            eki_question = st.text_input("問い（任意）", key="eki_q", placeholder="例：今の仕事を続けるべきか？")
            if st.button("☯ 卦を立てる", key="btn_eki"):
                increment("ekikyo")
                import time as _time
                hex_r = draw_hexagram(seed=int(_time.time()*1000)%100000)
                if eki_question:
                    st.markdown(f"<p style='color:#8e8ca0;'>問い：{eki_question}</p>", unsafe_allow_html=True)
                st.markdown(f"""<div class="score-box">
                    <div style="font-size:28px;font-weight:700;color:#f0c040;">第{hex_r['number']}卦 {hex_r['kanji']} — {hex_r['theme']}</div>
                    <div style="color:#8e8ca0;margin-top:12px;line-height:1.8;">{hex_r['message']}</div>
                </div>""", unsafe_allow_html=True)
                line_cols = st.columns(6)
                for i, (line_val, col) in enumerate(zip(reversed(hex_r['lines']), line_cols)):
                    is_changing = (6-i) in hex_r['changing_lines']
                    color = "#f0c040" if is_changing else "#c0a0e0"
                    col.markdown(f"""<div style="text-align:center;padding:8px;background:#13131f;border:1px solid #2a2a42;border-radius:6px;">
                        <div style="color:{color};font-size:18px;">{"━━━" if line_val=="陽" else "━ ━"}</div>
                        <div style="color:{color};font-size:11px;">{line_val}{"◉" if is_changing else ""}</div>
                    </div>""", unsafe_allow_html=True)

    st.stop()

# ===== ランキングページ =====
if current_page == "ranking":
    st.markdown("""
    <div class="page-title-bar">
        <h1>🏆 人気占いランキング</h1>
        <p>みんながよく使う占いTOP12</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    left, right = st.columns([2, 1])
    with left:
        render_ranking()
    with right:
        st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-title'>占いを探す</div>", unsafe_allow_html=True)
        for m in FORTUNE_META:
            if st.button(f"{m['icon']} {m['title']}", key=f"rank_go_{m['key']}", use_container_width=True):
                go_page("home", m['key'])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===== 今日の運勢ページ =====
if current_page == "today":
    ZODIAC_LIST = [
        ("♈", "牡羊座", "3/21〜4/19"),
        ("♉", "牡牛座", "4/20〜5/20"),
        ("♊", "双子座", "5/21〜6/21"),
        ("♋", "蟹座",   "6/22〜7/22"),
        ("♌", "獅子座", "7/23〜8/22"),
        ("♍", "乙女座", "8/23〜9/22"),
        ("♎", "天秤座", "9/23〜10/23"),
        ("♏", "蠍座",   "10/24〜11/21"),
        ("♐", "射手座", "11/22〜12/21"),
        ("♑", "山羊座", "12/22〜1/19"),
        ("♒", "水瓶座", "1/20〜2/18"),
        ("♓", "魚座",   "2/19〜3/20"),
    ]
    ZODIAC_COLORS = {
        "牡羊座":"#e05555","牡牛座":"#5a9e5a","双子座":"#d4a020","蟹座":"#5588cc",
        "獅子座":"#e07a20","乙女座":"#6aaa6a","天秤座":"#9966cc","蠍座":"#cc4455",
        "射手座":"#cc7722","山羊座":"#557799","水瓶座":"#3399aa","魚座":"#7766bb",
    }

    st.markdown(f"""
    <div class="page-title-bar">
        <h1>📅 今日の運勢</h1>
        <p>{date.today().strftime('%Y年%m月%d日')}　あなたの星座を選んでください</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    selected = st.session_state.get("today_zodiac", None)

    # 星座グリッド（4列×3行）
    if not selected:
        st.markdown("""
        <style>
        div[data-testid="stColumns"] > div > div > div > button.zodiac-btn {
            background: #13131f; border: 1px solid #2a2a42;
        }
        </style>
        """, unsafe_allow_html=True)

        rows = [ZODIAC_LIST[i:i+4] for i in range(0, 12, 4)]
        for row in rows:
            cols = st.columns(4)
            for j, (sym, name, period) in enumerate(row):
                color = ZODIAC_COLORS[name]
                with cols[j]:
                    st.markdown(f"""
                    <div style="
                        background:#13131f;border:1px solid #2a2a42;border-radius:12px;
                        padding:16px 8px;text-align:center;margin-bottom:4px;cursor:pointer;
                        transition:border-color 0.15s;
                    ">
                        <div style="font-size:32px;color:{color};">{sym}</div>
                        <div style="font-size:14px;font-weight:700;color:#e8e6f0;margin-top:6px;">{name}</div>
                        <div style="font-size:11px;color:#8e8ca0;margin-top:2px;">{period}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("選ぶ", key=f"zod_{name}", use_container_width=True):
                        st.session_state.today_zodiac = name
                        increment("zodiac")
                        st.rerun()
    else:
        # 結果表示
        color = ZODIAC_COLORS.get(selected, "#6c63ff")
        sym = next(s for s, n, _ in ZODIAC_LIST if n == selected)
        r = get_daily_fortune(selected, date.today())

        # 星座ヘッダー
        stars = lambda s: "★" * (s // 20) + "☆" * (5 - s // 20)
        total_stars = stars(r["total"])
        st.markdown(f"""
        <div style="background:#13131f;border:1px solid #2a2a42;border-radius:16px;padding:28px 24px;margin-bottom:20px;">
            <div style="display:flex;align-items:center;gap:20px;">
                <div style="font-size:64px;color:{color};">{sym}</div>
                <div>
                    <div style="font-size:24px;font-weight:700;color:#e8e6f0;">{selected}</div>
                    <div style="font-size:28px;color:#f0c040;letter-spacing:3px;margin-top:4px;">{total_stars}</div>
                    <div style="font-size:13px;color:#8e8ca0;margin-top:4px;">総合運 {r['total']}点　🍀 {r['lucky_color']}　🔢 {r['lucky_number']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4エリア運勢
        area_cols = st.columns(4)
        for i, (area, icon) in enumerate([("恋愛","💕"),("仕事","💼"),("金運","💰"),("健康","💪")]):
            s = r[area]["score"]
            c = "#6c63ff" if s >= 75 else "#f0c040" if s >= 55 else "#e06060"
            with area_cols[i]:
                st.markdown(f"""
                <div style="background:#13131f;border:1px solid #2a2a42;border-radius:10px;padding:16px;text-align:center;">
                    <div style="font-size:22px;">{icon}</div>
                    <div style="font-size:12px;color:#8e8ca0;margin-top:4px;">{area}</div>
                    <div style="font-size:20px;font-weight:700;color:{c};margin-top:6px;">{s}点</div>
                    <div style="font-size:20px;color:{c};letter-spacing:2px;">{"★"*(s//20)}{"☆"*(5-s//20)}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # アドバイス詳細
        for area, icon in [("恋愛","💕"),("仕事","💼"),("金運","💰"),("健康","💪")]:
            s = r[area]["score"]
            c = "#6c63ff" if s >= 75 else "#f0c040" if s >= 55 else "#e06060"
            st.markdown(f"""
            <div class="advice-box" style="margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#e8e6f0;font-weight:700;">{icon} {area}</span>
                    <span style="color:{c};font-size:16px;letter-spacing:2px;">{"★"*(s//20)}{"☆"*(5-s//20)} <span style="font-size:13px;">{s}点</span></span>
                </div>
                <div style="margin-top:8px;color:#8e8ca0;line-height:1.7;">{r[area]['advice']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("← 別の星座を選ぶ", key="back_zodiac"):
            del st.session_state["today_zodiac"]
            st.rerun()

    st.stop()

# ===== ホーム・新着・無料占い（カードグリッド） =====
# ページタイトル
page_titles = {
    "home": ("🔮 すべての占い", "12種類の本格無料占いが全て楽しめます"),
    "new":  ("✨ 新着占い", "最新の占いメニューをチェック"),
    "free": ("🎁 無料占い", "すべて完全無料でお楽しみいただけます"),
}
ptitle, psubtext = page_titles.get(current_page, page_titles["home"])
st.markdown(f"""
<div class="page-title-bar">
    <h1>{ptitle}</h1>
    <p>{psubtext}</p>
</div>
""", unsafe_allow_html=True)

# カテゴリタブ
if "cat_filter" not in st.session_state:
    st.session_state.cat_filter = "すべて"

cat_cols = st.columns(len(CAT_LABELS))
for i, cat in enumerate(CAT_LABELS):
    with cat_cols[i]:
        is_active = st.session_state.cat_filter == cat
        if st.button(cat, key=f"cat_{cat}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.cat_filter = cat
            st.rerun()

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# フィルタリング
filtered = FORTUNE_META if st.session_state.cat_filter == "すべて" else [
    m for m in FORTUNE_META if st.session_state.cat_filter in m["tags"]
]

# メインコンテンツ + サイドバー
main_col, side_col = st.columns([3, 1])

CARD_GRADIENTS = {
    "compat":    "linear-gradient(135deg,#1a1a3e 0%,#3a2060 100%)",
    "zodiac":    "linear-gradient(135deg,#1a2a3e 0%,#204060 100%)",
    "numerology":"linear-gradient(135deg,#1e2a1e 0%,#2a4a30 100%)",
    "kyusei":    "linear-gradient(135deg,#2a1e1e 0%,#4a2a20 100%)",
    "animal":    "linear-gradient(135deg,#1e2a1e 0%,#354a20 100%)",
    "seimei":    "linear-gradient(135deg,#2a2a1e 0%,#4a4020 100%)",
    "horoscope": "linear-gradient(135deg,#1a1a40 0%,#2a2060 100%)",
    "shichuu":   "linear-gradient(135deg,#2a1a1a 0%,#4a2020 100%)",
    "biorhythm": "linear-gradient(135deg,#1a2a2a 0%,#1a4040 100%)",
    "blood":     "linear-gradient(135deg,#2a1a1a 0%,#501520 100%)",
    "tarot":     "linear-gradient(135deg,#1e1a2e 0%,#3a1a50 100%)",
    "ekikyo":    "linear-gradient(135deg,#1a2a2a 0%,#204040 100%)",
}

with main_col:
    # カードグリッド（3列）
    counts = get_counts()
    for row_start in range(0, len(filtered), 3):
        row_items = filtered[row_start:row_start+3]
        cols = st.columns(3)
        for j, meta in enumerate(row_items):
            with cols[j]:
                view_count = counts.get(meta['key'], 0)
                tags_html = "".join(
                    f'<span style="background:#1c1c2e;color:#8e8ca0;font-size:10px;padding:2px 8px;border-radius:4px;margin-right:4px;">{t}</span>'
                    for t in meta['tags']
                )
                grad = CARD_GRADIENTS.get(meta['key'], "linear-gradient(135deg,#1c1c2e,#2a2a42)")
                st.markdown(f"""
                <div class="fortune-card">
                    <div class="card-thumb" style="background:{grad};">
                        <span class="card-badge">{meta['badge']}</span>
                        {meta['icon']}
                    </div>
                    <div class="card-body">
                        <div class="card-meta">{tags_html}</div>
                        <div class="card-title">{meta['title']}</div>
                        <div class="card-subtitle" style="color:#8e8ca0;font-size:11px;margin-bottom:6px;">{meta['subtitle']}</div>
                        <div style="color:#50505e;font-size:11px;">👁 {view_count:,}回</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"占う →", key=f"go_{meta['key']}", use_container_width=True):
                    go_page(current_page, meta['key'])
                    st.rerun()

with side_col:
    # サイドバー：人気ランキング
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>🏆 人気ランキング</div>", unsafe_allow_html=True)
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    medals = ["🥇","🥈","🥉"]
    for i, (key, cnt) in enumerate(sorted_counts[:5]):
        m = next((fm for fm in FORTUNE_META if fm['key'] == key), None)
        if m:
            medal = medals[i] if i < 3 else f"{i+1}."
            st.markdown(f"""<div class='sidebar-item'>{medal} {m['icon']} {m['title']} <span style='color:#50505e;font-size:11px;'>({cnt})</span></div>""", unsafe_allow_html=True)
    if st.button("ランキング詳細 →", key="sidebar_ranking", use_container_width=True):
        go_page("ranking")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # サイドバー：悩み別カテゴリ
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>悩み別で探す</div>", unsafe_allow_html=True)
    for cat in CAT_LABELS[1:]:
        if st.button(cat, key=f"side_cat_{cat}", use_container_width=True):
            st.session_state.cat_filter = cat
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # サイドバー：占術で探す
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>占術で探す</div>", unsafe_allow_html=True)
    for m in FORTUNE_META:
        st.markdown(f"<div class='sidebar-item'>{m['icon']} {m['title']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
