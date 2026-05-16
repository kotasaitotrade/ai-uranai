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
    PLANET_MEANING, HOUSE_MEANING, BLOOD_PERSONALITY, SPREAD_TYPES, SPREAD_POSITIONS,
)

st.set_page_config(page_title="占いポータル", page_icon="🔮", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0d0d2b 0%, #1a1a4e 100%); color: #f0e6ff; }
    h1, h2, h3 { color: #d4b8ff; }
    .score-box {
        background: rgba(100, 60, 180, 0.3);
        border: 1px solid #7b5ea7;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .score-num { font-size: 48px; font-weight: bold; color: #f0c040; }
    .card {
        background: rgba(60, 40, 100, 0.4);
        border: 1px solid #5a3d8a;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    .advice-box {
        background: rgba(60, 40, 100, 0.4);
        border-left: 3px solid #9b6dff;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }
    .luck-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6a0dad, #9b6dff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 40px;
        font-size: 16px;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] { color: #c9a0ff; }
    .stTabs [aria-selected="true"] { color: #ffffff; border-bottom: 2px solid #9b6dff; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔮 占いポータル")
st.markdown("<p style='text-align:center;color:#a090c0;'>12の占いで、あなたの運命を多角的に読み解く</p>", unsafe_allow_html=True)

tabs = st.tabs([
    "💫 相性占い", "⭐ 星座占い", "🔢 数秘術", "☯️ 九星気学",
    "🐾 動物占い", "✍️ 姓名判断", "🌌 ホロスコープ",
    "🀄 四柱推命", "📈 バイオリズム", "🩸 血液型", "🃏 タロット", "☯ 易経",
])

# ===================== 相性占い =====================
with tabs[0]:
    st.markdown("### 💫 相性占い")
    st.markdown("<p style='color:#a090c0;'>生年月日から2人の関係性を5つの軸で分析</p>", unsafe_allow_html=True)
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
        n1 = name1 or "あなた"
        n2 = name2 or "相手"
        r = calc_compatibility(n1, birth1, n2, birth2)

        st.markdown(f"## ✨ {n1} × {n2} の相性結果")
        st.markdown(f"""<div class="score-box">
            <div style="color:#c9a0ff;font-size:16px;">総合相性スコア</div>
            <div class="score-num">{r['total']}点</div>
            <div style="color:#a090c0;">{r['total_comment']}</div>
        </div>""", unsafe_allow_html=True)

        axes = ["シンクロ", "価値観", "ノリ", "ミライ", "運命"]
        scores = [r['synchro'], r['values'], r['vibe'], r['future'], r['fate']]
        fig = go.Figure(data=go.Scatterpolar(
            r=scores + [scores[0]], theta=axes + [axes[0]],
            fill='toself', fillcolor='rgba(155,109,255,0.3)',
            line=dict(color='#9b6dff', width=2), marker=dict(color='#f0c040', size=8)
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(20,10,40,0.8)',
                radialaxis=dict(visible=True, range=[0,100], tickfont=dict(color='#a090c0'), gridcolor='rgba(150,100,255,0.2)'),
                angularaxis=dict(tickfont=dict(color='#d4b8ff', size=13), gridcolor='rgba(150,100,255,0.2)')
            ),
            paper_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=40,b=40,l=60,r=60)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 5つの軸")
        for title, key, score in [
            ("💫 シンクロ（波長の一致）", "synchro", r['synchro']),
            ("🧭 価値観（考え方の近さ）", "values", r['values']),
            ("🎉 ノリ（コミュニケーション）", "vibe", r['vibe']),
            ("🌱 ミライ（将来性）", "future", r['future']),
            ("🔮 運命（関係の引力）", "fate", r['fate']),
        ]:
            bar_color = "#9b6dff" if score >= 70 else "#f0c040" if score >= 50 else "#e06060"
            st.markdown(f"""<div class="advice-box">
                <span style="color:#c9a0ff;font-weight:bold;">{title}</span>
                <span style="float:right;color:{bar_color};font-size:20px;font-weight:bold;">{score}点</span>
                <div style="margin-top:8px;color:#c8b8e0;">{r[key+'_advice']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 🔯 占術詳細")
        ca, cb = st.columns(2)
        with ca:
            st.markdown(f"**{n1}**")
            st.markdown(f"- 星座：{r['zodiac1']}  \n- 数秘：{r['life_path1']}  \n- 九星：{r['kyusei1']}  \n- 干支：{r['junishi1']}  \n- 五行：{r['gogyo1']}")
        with cb:
            st.markdown(f"**{n2}**")
            st.markdown(f"- 星座：{r['zodiac2']}  \n- 数秘：{r['life_path2']}  \n- 九星：{r['kyusei2']}  \n- 干支：{r['junishi2']}  \n- 五行：{r['gogyo2']}")

# ===================== 星座占い =====================
with tabs[1]:
    st.markdown("### ⭐ 星座占い（今日の運勢）")
    birth_z = st.date_input("生年月日", key="z_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,4,1))
    if st.button("⭐ 占う", key="btn_zodiac"):
        today = date.today()
        zodiac = get_zodiac(birth_z)
        r = get_daily_fortune(zodiac, today)
        element = ZODIAC_ELEMENT[zodiac]
        ruling = ZODIAC_RULING[zodiac]
        keyword = ZODIAC_KEYWORD[zodiac]

        st.markdown(f"## {zodiac}")
        st.markdown(f"""<div class="card">
            <span style="color:#a090c0;">属性：</span><span style="color:#f0e6ff;">{element}</span>
            <span style="color:#a090c0;">支配星：</span><span style="color:#f0e6ff;">{ruling}</span>
            <span style="color:#a090c0;">キーワード：</span><span style="color:#f0e6ff;">{keyword}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"#### 📅 {r['date']} の運勢")
        st.markdown(f"""<div class="score-box">
            <div style="color:#c9a0ff;">総合運</div>
            <div class="score-num">{r['total']}点</div>
            <div style="color:#f0c040;">🍀 ラッキーカラー：{r['lucky_color']}　🔢 ラッキーナンバー：{r['lucky_number']}</div>
        </div>""", unsafe_allow_html=True)

        area_icons = {"恋愛": "💕", "仕事": "💼", "金運": "💰", "健康": "💪"}
        for area, icon in area_icons.items():
            s = r[area]['score']
            bar_color = "#9b6dff" if s >= 75 else "#f0c040" if s >= 55 else "#e06060"
            stars = "★" * (s // 20) + "☆" * (5 - s // 20)
            st.markdown(f"""<div class="advice-box">
                <span style="color:#c9a0ff;font-weight:bold;">{icon} {area}</span>
                <span style="float:right;color:{bar_color};">{stars} {s}点</span>
                <div style="margin-top:8px;color:#c8b8e0;">{r[area]['advice']}</div>
            </div>""", unsafe_allow_html=True)

# ===================== 数秘術 =====================
with tabs[2]:
    st.markdown("### 🔢 数秘術")
    birth_n = st.date_input("生年月日", key="n_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("🔢 占う", key="btn_num"):
        r = get_numerology_full(birth_n)
        st.markdown(f"## ライフパスナンバー：{r['life_path']}")
        st.markdown(f"""<div class="score-box">
            <div style="color:#f0c040;font-size:28px;font-weight:bold;">{r['life_path']} — {r['name']}</div>
            <div style="color:#c8b8e0;margin-top:12px;line-height:1.7;">{r['personality']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"#### 📅 {date.today().year}年 パーソナルイヤーナンバー：{r['personal_year']}")
        st.markdown(f"""<div class="advice-box">
            <div style="color:#c8b8e0;line-height:1.7;">{r['personal_year_meaning']}</div>
        </div>""", unsafe_allow_html=True)

# ===================== 九星気学 =====================
with tabs[3]:
    st.markdown("### ☯️ 九星気学")
    birth_k = st.date_input("生年月日", key="k_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("☯️ 占う", key="btn_kyusei"):
        today = date.today()
        r = get_kyusei_fortune(birth_k, today)
        st.markdown(f"## 本命星：{r['star_name']}")
        st.markdown(f"""<div class="card">
            <span style="color:#a090c0;">五行：</span><span style="color:#f0e6ff;">{r['element']}</span>
            <span style="color:#a090c0;">キーワード：</span><span style="color:#f0e6ff;">{r['keyword']}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="advice-box">
            <span style="color:#c9a0ff;font-weight:bold;">性格・特徴</span>
            <div style="margin-top:8px;color:#c8b8e0;line-height:1.7;">{r['personality']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"#### 🧭 吉方位")
        st.markdown(f"""<div class="score-box">
            <div style="color:#f0c040;font-size:22px;">🧭 {r['lucky_direction']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"#### 📅 {r['year']}年の運勢")
        st.markdown(f"""<div class="advice-box">
            <div style="color:#c8b8e0;line-height:1.7;">{r['year_fortune']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"#### 📆 {r['year']}年{r['month']}月の運気スコア")
        bar_color = "#9b6dff" if r['month_score'] >= 75 else "#f0c040" if r['month_score'] >= 55 else "#e06060"
        st.markdown(f"""<div class="score-box">
            <div class="score-num" style="color:{bar_color};">{r['month_score']}点</div>
        </div>""", unsafe_allow_html=True)

# ===================== 動物占い =====================
with tabs[4]:
    st.markdown("### 🐾 動物占い")
    birth_a = st.date_input("生年月日", key="a_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("🐾 占う", key="btn_animal"):
        r = get_animal_fortune(birth_a)
        st.markdown(f"## あなたの動物タイプ")
        st.markdown(f"""<div class="score-box">
            <div style="font-size:36px;font-weight:bold;color:#f0c040;">{r['animal']}</div>
            <div style="color:#c9a0ff;margin-top:8px;font-size:18px;">{r['sub_type']}</div>
            <div style="color:#a090c0;margin-top:4px;">干支：{JUNISHI_ANIMAL.get(r['junishi'], r['junishi'])}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="advice-box">
            <span style="color:#c9a0ff;font-weight:bold;">🐾 動物の特徴</span>
            <div style="margin-top:8px;color:#c8b8e0;line-height:1.7;">{r['personality']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="advice-box">
            <span style="color:#c9a0ff;font-weight:bold;">🧠 {r['sub_type']}の特徴</span>
            <div style="margin-top:8px;color:#c8b8e0;line-height:1.7;">{r['sub_personality']}</div>
        </div>""", unsafe_allow_html=True)

# ===================== 姓名判断 =====================
with tabs[5]:
    st.markdown("### ✍️ 姓名判断")
    st.markdown("<p style='color:#a090c0;'>苗字と名前の合計画数を入力してください</p>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        surname = st.text_input("苗字（例：山田）", key="s_surname", placeholder="山田")
        surname_strokes = st.number_input("苗字の総画数", key="s_strokes1", min_value=1, max_value=81, value=12)
    with col_s2:
        given = st.text_input("名前（例：太郎）", key="s_given", placeholder="太郎")
        given_strokes = st.number_input("名前の総画数", key="s_strokes2", min_value=1, max_value=81, value=14)

    st.caption("※ 画数は漢字辞典の旧字体画数を使用してください")

    if st.button("✍️ 占う", key="btn_seimei"):
        r = get_seimei_fortune(int(surname_strokes), int(given_strokes))
        full_name = f"{surname} {given}" if surname and given else "入力された名前"
        st.markdown(f"## {full_name} の姓名判断")

        luck_color = {"大吉": "#f0c040", "最高運": "#ff6090", "吉": "#9b6dff", "小吉": "#60b0f0", "努力運": "#a0a0a0"}
        overall_color = luck_color.get(r['overall'], "#a0a0a0")
        st.markdown(f"""<div class="score-box">
            <div style="color:#c9a0ff;">総合運</div>
            <div style="font-size:40px;font-weight:bold;color:{overall_color};">{r['overall']}</div>
            <div style="color:#a090c0;">吉数：{r['lucky_count']}格 / 5格</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("#### 📊 五格分析")
        kaku_labels = [
            ("天格", r['tenkaku'], "祖先から受け継いだ運勢・家系の運"),
            ("地格", r['chikaku'], "自分自身の才能・幼少期〜中年期の運"),
            ("人格", r['jinkaku'], "社会的な運勢・中心となる最重要格"),
            ("外格", r['sotokaku'], "対人関係・社会的環境の運"),
            ("総格", r['sokaku'], "人生全体・晩年の運勢"),
        ]
        for label, data, desc in kaku_labels:
            lc = luck_color.get(data['luck'], "#a0a0a0")
            st.markdown(f"""<div class="advice-box">
                <span style="color:#c9a0ff;font-weight:bold;">{label}（{data['value']}画）</span>
                <span style="float:right;color:{lc};font-weight:bold;">{data['luck']}</span>
                <div style="color:#a090c0;font-size:12px;margin-top:2px;">{desc}</div>
                <div style="margin-top:6px;color:#c8b8e0;">{data['desc']}</div>
            </div>""", unsafe_allow_html=True)

# ===================== ホロスコープ =====================
with tabs[6]:
    st.markdown("### 🌌 ホロスコープ")
    st.markdown("<p style='color:#a090c0;'>生年月日から9天体の配置を計算し、あなたの天宮図を読み解きます</p>", unsafe_allow_html=True)

    h_birth = st.date_input("生年月日", key="h_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,4,5))
    h_hour = st.slider("出生時刻（不明な場合は12時のまま）", 0, 23, 12, key="h_hour",
                       format="%d時")

    if st.button("🌌 ホロスコープを読み解く", key="btn_horo"):
        r = get_horoscope(h_birth, h_hour)

        # サマリー
        st.markdown(f"""<div class="score-box">
            <div style="font-size:22px;color:#f0c040;">
                ☉ 太陽星座：{r['sun_sign']}
                ☽ 月星座：{r['moon_sign']}
                ↑ ASC：{r['ascendant']['sign']}
            </div>
            <div style="color:#a090c0;margin-top:8px;">
                支配エレメント：{r['dominant_element']}　支配サイン：{r['dominant_sign']}
            </div>
        </div>""", unsafe_allow_html=True)

        # ホロスコープチャート（円形）
        st.markdown("#### 🌐 天体配置チャート")
        planet_order = ["太陽", "月", "水星", "金星", "火星", "木星", "土星", "天王星", "海王星"]
        planet_colors = {
            "太陽": "#f0c040", "月": "#c8c8ff", "水星": "#80c080",
            "金星": "#ff90b0", "火星": "#ff6060", "木星": "#f0a030",
            "土星": "#b0b060", "天王星": "#60c0d0", "海王星": "#6080ff",
        }

        fig = go.Figure()
        # 黄道帯（12サイン）
        sign_syms = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
        for i, sym in enumerate(sign_syms):
            angle = math.radians(i * 30 + 15)
            fig.add_annotation(x=math.cos(angle)*0.82, y=math.sin(angle)*0.82,
                               text=sym, showarrow=False,
                               font=dict(size=16, color="#9b6dff"))
            # 分割線
            a0 = math.radians(i * 30)
            fig.add_shape(type="line", x0=math.cos(a0)*0.65, y0=math.sin(a0)*0.65,
                          x1=math.cos(a0)*0.95, y1=math.sin(a0)*0.95,
                          line=dict(color="#5a3d8a", width=1))

        # 天体プロット
        for planet in planet_order:
            lon = r["planets"][planet]
            deg = lon["degree"] + (["牡羊座","牡牛座","双子座","蟹座","獅子座","乙女座",
                                     "天秤座","蠍座","射手座","山羊座","水瓶座","魚座"].index(lon["sign"]) * 30)
            angle = math.radians(deg)
            x = math.cos(angle) * 0.55
            y = math.sin(angle) * 0.55
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                marker=dict(size=14, color=planet_colors[planet], symbol="circle"),
                text=[PLANET_MEANING.get(planet, planet)[0] + lon["planet_symbol"]],
                textposition="top center",
                textfont=dict(size=10, color=planet_colors[planet]),
                name=f"{lon['planet_symbol']} {planet}（{lon['sign']}）",
                hovertemplate=f"<b>{planet}</b><br>{lon['sign']} {lon['degree']}°<br>第{lon['house']}ハウス<extra></extra>",
            ))

        # 円
        theta_arr = [math.radians(i) for i in range(361)]
        for r_val, color in [(0.65, "#3a2a6a"), (0.95, "#5a3d8a")]:
            fig.add_trace(go.Scatter(
                x=[math.cos(t)*r_val for t in theta_arr],
                y=[math.sin(t)*r_val for t in theta_arr],
                mode="lines", line=dict(color=color, width=1),
                showlegend=False, hoverinfo="skip",
            ))

        fig.update_layout(
            paper_bgcolor="rgba(10,5,30,0.9)",
            plot_bgcolor="rgba(10,5,30,0.9)",
            xaxis=dict(range=[-1.1,1.1], visible=False, scaleanchor="y"),
            yaxis=dict(range=[-1.1,1.1], visible=False),
            height=480,
            showlegend=True,
            legend=dict(font=dict(color="#c9a0ff", size=11), bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=20, b=20, l=20, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # 天体詳細
        st.markdown("#### 🪐 天体配置詳細")
        for planet in planet_order:
            p = r["planets"][planet]
            st.markdown(f"""<div class="advice-box">
                <span style="color:#f0c040;font-weight:bold;">{p['planet_symbol']} {planet}</span>
                <span style="color:#c9a0ff;margin-left:8px;">{p['sign']} {p['degree']}°</span>
                <span style="color:#a090c0;font-size:12px;margin-left:8px;">第{p['house']}ハウス</span>
                <div style="color:#a090c0;font-size:11px;margin-top:2px;">{p['planet_meaning']}</div>
                <div style="margin-top:6px;color:#c8b8e0;">{p['sign_meaning']}</div>
            </div>""", unsafe_allow_html=True)

        # アスペクト
        if r["aspects"]:
            st.markdown("#### 🔗 主要アスペクト")
            aspect_colors = {"調和": "#9b6dff", "緊張": "#e06060", "強化": "#f0c040"}
            for asp in r["aspects"][:8]:
                color = aspect_colors.get(asp["type"], "#a090c0")
                st.markdown(f"""<div class="card" style="padding:10px 16px;">
                    <span style="color:{color};font-weight:bold;">{asp['p1']} ☍ {asp['p2']}</span>
                    <span style="color:#c9a0ff;margin-left:8px;">{asp['angle']}</span>
                    <span style="color:{color};font-size:12px;margin-left:8px;">【{asp['type']}】</span>
                    <span style="color:#a090c0;font-size:11px;margin-left:4px;">orb {asp['orb']}°</span>
                </div>""", unsafe_allow_html=True)

# ===================== 四柱推命 =====================
with tabs[7]:
    st.markdown("### 🀄 四柱推命")
    st.markdown("<p style='color:#a090c0;'>生年月日から年柱・月柱・日柱と五行バランスを読み解きます</p>", unsafe_allow_html=True)
    sh_birth = st.date_input("生年月日", key="sh_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    if st.button("🀄 占う", key="btn_shichuu"):
        r = get_shichuu(sh_birth)
        st.markdown(f"""<div class="score-box">
            <div style="font-size:24px;color:#f0c040;">本命五行：{r['honmei_gogyo']}（{r['honmei_inyo']}）</div>
            <div style="color:#c8b8e0;margin-top:8px;">{r['personality']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("#### 📊 三柱")
        for label, val in [("年柱（生まれの運）", r['year_pillar']),
                            ("月柱（社会・仕事運）", r['month_pillar']),
                            ("日柱（本質・パートナー運）", r['day_pillar'])]:
            st.markdown(f"""<div class="advice-box">
                <span style="color:#c9a0ff;font-weight:bold;">{label}</span>
                <span style="float:right;color:#f0c040;font-size:24px;font-weight:bold;">{val}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 🌿 五行バランス")
        elem_colors = {"木": "#60c060", "火": "#e06060", "土": "#c09040", "金": "#c0c0c0", "水": "#6090f0"}
        cols = st.columns(5)
        for i, (elem, count) in enumerate(r['five_elements'].items()):
            with cols[i]:
                bar = "●" * count + "○" * (3 - count)
                st.markdown(f"""<div style="text-align:center;padding:12px;background:rgba(60,40,100,0.4);border-radius:8px;">
                    <div style="color:{elem_colors[elem]};font-size:20px;font-weight:bold;">{elem}</div>
                    <div style="color:#f0c040;font-size:18px;">{bar}</div>
                    <div style="color:#a090c0;font-size:12px;">{count}/3</div>
                </div>""", unsafe_allow_html=True)

        st.markdown(f"#### 📅 {date.today().year}年の運勢")
        st.markdown(f"""<div class="advice-box">
            <span style="color:#c9a0ff;">今年の年五行：<b style="color:#f0c040;">{r['year_gogyo']}</b></span>
            <div style="margin-top:8px;color:#c8b8e0;line-height:1.7;">{r['year_luck']}</div>
        </div>""", unsafe_allow_html=True)

# ===================== バイオリズム =====================
with tabs[8]:
    st.markdown("### 📈 バイオリズム")
    st.markdown("<p style='color:#a090c0;'>身体(23日)・感情(28日)・知性(33日)の3つの周期で今日のコンディションを分析</p>", unsafe_allow_html=True)
    bio_birth = st.date_input("生年月日", key="bio_birth", min_value=date(1920,1,1), max_value=date(2010,12,31), value=date(1990,1,1))
    bio_target = st.date_input("調べたい日付", key="bio_target", value=date.today())
    if st.button("📈 バイオリズムを見る", key="btn_bio"):
        r = get_biorhythm(bio_birth, bio_target)
        st.markdown(f"#### {bio_target.strftime('%Y年%m月%d日')} のバイオリズム")

        for label, val, lbl, color in [
            ("💪 身体リズム（23日周期）", r['physical'], r['physical_label'], r['physical_color']),
            ("💝 感情リズム（28日周期）", r['emotional'], r['emotional_label'], r['emotional_color']),
            ("🧠 知性リズム（33日周期）", r['intellectual'], r['intellectual_label'], r['intellectual_color']),
        ]:
            pct = int((val + 1) / 2 * 100)
            st.markdown(f"""<div class="advice-box">
                <span style="color:#c9a0ff;font-weight:bold;">{label}</span>
                <span style="float:right;color:{color};font-weight:bold;">{lbl}</span>
                <div style="background:#2a1a4a;border-radius:4px;height:12px;margin-top:10px;">
                    <div style="background:{color};width:{pct}%;height:12px;border-radius:4px;"></div>
                </div>
                <div style="color:#a090c0;font-size:12px;margin-top:4px;">スコア：{val:+.2f}（-1.0〜+1.0）</div>
            </div>""", unsafe_allow_html=True)

        # 折れ線グラフ（30日間）
        st.markdown("#### 📊 前後15日間のグラフ")
        hist = r['history']
        dates = [h['date'].strftime('%m/%d') for h in hist]
        fig = go.Figure()
        for key, name, color in [('physical','身体','#9b6dff'), ('emotional','感情','#ff90b0'), ('intellectual','知性','#60c0d0')]:
            vals = [h[key] for h in hist]
            fig.add_trace(go.Scatter(x=dates, y=vals, name=name, line=dict(color=color, width=2), mode='lines'))
        fig.add_hline(y=0, line_dash="dash", line_color="#5a3d8a")
        today_idx = 15
        fig.add_vline(x=dates[today_idx], line_dash="dot", line_color="#f0c040", annotation_text="今日")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,5,30,0.8)',
            xaxis=dict(tickfont=dict(color='#a090c0'), gridcolor='rgba(100,80,160,0.2)'),
            yaxis=dict(tickfont=dict(color='#a090c0'), range=[-1.1,1.1], gridcolor='rgba(100,80,160,0.2)'),
            legend=dict(font=dict(color='#c9a0ff')),
            margin=dict(t=20,b=20,l=40,r=20), height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

# ===================== 血液型 =====================
with tabs[9]:
    st.markdown("### 🩸 血液型占い")
    bl_blood = st.selectbox("あなたの血液型", ["A", "B", "O", "AB"], key="bl_blood")
    use_partner = st.checkbox("相手との相性も見る", key="bl_use_partner")
    bl_partner = None
    if use_partner:
        bl_partner = st.selectbox("相手の血液型", ["A", "B", "O", "AB"], key="bl_partner")
    if st.button("🩸 占う", key="btn_blood"):
        r = get_blood_fortune(bl_blood, bl_partner)
        st.markdown(f"## {bl_blood}型：{r['title']}")
        st.markdown(f"""<div class="advice-box">
            <div style="color:#c8b8e0;line-height:1.7;">{r['desc']}</div>
        </div>""", unsafe_allow_html=True)
        for label, val in [("✨ 強み", r['strength']), ("⚠️ 弱み", r['weakness']),
                            ("🎨 ラッキーカラー", r['lucky_color']), ("💕 恋愛傾向", r['love'])]:
            st.markdown(f"""<div class="advice-box">
                <span style="color:#c9a0ff;font-weight:bold;">{label}</span>
                <div style="margin-top:6px;color:#c8b8e0;">{val}</div>
            </div>""", unsafe_allow_html=True)
        if bl_partner and 'compat_score' in r:
            score = r['compat_score']
            bar_color = "#9b6dff" if score >= 75 else "#f0c040" if score >= 55 else "#e06060"
            st.markdown(f"""<div class="score-box" style="margin-top:16px;">
                <div style="color:#c9a0ff;">{bl_blood}型 × {bl_partner}型 の相性</div>
                <div class="score-num" style="color:{bar_color};">{score}点</div>
                <div style="color:#c8b8e0;margin-top:8px;">{r['compat_desc']}</div>
            </div>""", unsafe_allow_html=True)

# ===================== タロット =====================
with tabs[10]:
    st.markdown("### 🃏 タロット占い（大アルカナ22枚）")
    spread_name = st.selectbox("スプレッド（展開法）", list(SPREAD_TYPES.keys()), key="tarot_spread")
    num_cards = SPREAD_TYPES[spread_name]
    if st.button("🃏 カードを引く", key="btn_tarot"):
        import time as _time
        seed_val = int(_time.time() * 1000) % 100000
        cards = draw_tarot(num_cards, seed=seed_val)
        positions = SPREAD_POSITIONS[num_cards]
        st.markdown(f"#### {spread_name}")
        for i, (card, pos) in enumerate(zip(cards, positions)):
            direction = "逆位置 🔄" if card['is_reversed'] else "正位置 ✨"
            dir_color = "#e06060" if card['is_reversed'] else "#9b6dff"
            meaning = card['reversed'] if card['is_reversed'] else card['upright']
            st.markdown(f"""<div class="card" style="margin:12px 0;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="font-size:36px;">{card['symbol']}</div>
                    <div>
                        <div style="color:#a090c0;font-size:12px;">{pos}</div>
                        <div style="color:#f0c040;font-size:18px;font-weight:bold;">{card['num']}. {card['name']}</div>
                        <div style="color:{dir_color};font-size:13px;">{direction}</div>
                    </div>
                </div>
                <div style="margin-top:10px;color:#c8b8e0;line-height:1.7;">{meaning}</div>
            </div>""", unsafe_allow_html=True)

# ===================== 易経 =====================
with tabs[11]:
    st.markdown("### ☯ 易経（六十四卦）")
    st.markdown("<p style='color:#a090c0;'>心を静めて問いを浮かべ、ボタンを押してください</p>", unsafe_allow_html=True)
    eki_question = st.text_input("問い（任意）", key="eki_q", placeholder="例：今の仕事を続けるべきか？")
    if st.button("☯ 卦を立てる", key="btn_eki"):
        import time as _time
        seed_val = int(_time.time() * 1000) % 100000
        hex_r = draw_hexagram(seed=seed_val)

        st.markdown(f"#### 第{hex_r['number']}卦：{hex_r['kanji']}（{hex_r['name']}）")
        if eki_question:
            st.markdown(f"<p style='color:#a090c0;'>問い：{eki_question}</p>", unsafe_allow_html=True)

        st.markdown(f"""<div class="score-box">
            <div style="font-size:28px;font-weight:bold;color:#f0c040;">{hex_r['kanji']} — {hex_r['theme']}</div>
            <div style="color:#c8b8e0;margin-top:12px;line-height:1.8;font-size:15px;">{hex_r['message']}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("#### 六爻（上から順）")
        line_cols = st.columns(6)
        for i, (line_val, col) in enumerate(zip(reversed(hex_r['lines']), line_cols)):
            is_changing = (6 - i) in hex_r['changing_lines']
            color = "#f0c040" if is_changing else "#c9a0ff"
            symbol = "━━━" if line_val == "陽" else "━ ━"
            mark = "◉" if is_changing else ""
            col.markdown(f"""<div style="text-align:center;padding:8px;background:rgba(60,40,100,0.4);border-radius:6px;">
                <div style="color:{color};font-size:18px;">{symbol}</div>
                <div style="color:{color};font-size:11px;">{line_val}{mark}</div>
            </div>""", unsafe_allow_html=True)

        if hex_r['changing_lines']:
            st.markdown(f"<p style='color:#f0c040;margin-top:8px;'>変爻：第{', '.join(map(str, hex_r['changing_lines']))}爻が動いています。変化の兆しを示しています。</p>", unsafe_allow_html=True)
