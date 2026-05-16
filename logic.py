import hashlib
import math
from datetime import date, datetime

# ========== 共通ユーティリティ ==========
def _hash_score(key: str, today: date, min_val=50, max_val=100) -> int:
    h = int(hashlib.md5(f"{key}{today.isoformat()}".encode()).hexdigest()[:4], 16)
    return min_val + h % (max_val - min_val + 1)

def digit_sum(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(c) for c in str(n))
    return n

# ========== 西洋占星術 ==========
ZODIAC_LIST = [
    (1, 20, "山羊座"), (2, 19, "水瓶座"), (3, 20, "魚座"), (4, 20, "牡羊座"),
    (5, 21, "牡牛座"), (6, 21, "双子座"), (7, 23, "蟹座"), (8, 23, "獅子座"),
    (9, 23, "乙女座"), (10, 23, "天秤座"), (11, 22, "蠍座"), (12, 22, "射手座"),
    (12, 31, "山羊座"),
]
ZODIAC_ELEMENT = {
    "牡羊座": "火", "獅子座": "火", "射手座": "火",
    "牡牛座": "土", "乙女座": "土", "山羊座": "土",
    "双子座": "風", "天秤座": "風", "水瓶座": "風",
    "蟹座": "水", "蠍座": "水", "魚座": "水",
}
ZODIAC_RULING = {
    "牡羊座": "火星", "牡牛座": "金星", "双子座": "水星", "蟹座": "月",
    "獅子座": "太陽", "乙女座": "水星", "天秤座": "金星", "蠍座": "冥王星",
    "射手座": "木星", "山羊座": "土星", "水瓶座": "天王星", "魚座": "海王星",
}
ZODIAC_KEYWORD = {
    "牡羊座": "情熱・行動力・開拓精神", "牡牛座": "安定・忍耐・美的センス",
    "双子座": "知性・好奇心・コミュニケーション", "蟹座": "感受性・家族愛・直感",
    "獅子座": "創造力・プライド・リーダーシップ", "乙女座": "分析力・誠実・完璧主義",
    "天秤座": "調和・美意識・公平性", "蠍座": "洞察力・意志の強さ・神秘性",
    "射手座": "自由・冒険心・哲学的思考", "山羊座": "実直・野心・忍耐力",
    "水瓶座": "独創性・博愛・革新性", "魚座": "共感力・夢想家・芸術的感性",
}
ELEMENT_COMPAT = {
    ("火", "火"): 80, ("火", "風"): 90, ("火", "土"): 60, ("火", "水"): 40,
    ("土", "土"): 75, ("土", "水"): 85, ("土", "風"): 50,
    ("風", "風"): 70, ("風", "水"): 55, ("水", "水"): 80,
}

def get_zodiac(d: date) -> str:
    for month, day, name in ZODIAC_LIST:
        if (d.month, d.day) <= (month, day):
            return name
    return "山羊座"

def element_compat(z1: str, z2: str) -> int:
    e1, e2 = ZODIAC_ELEMENT[z1], ZODIAC_ELEMENT[z2]
    key = (e1, e2) if (e1, e2) in ELEMENT_COMPAT else (e2, e1)
    return ELEMENT_COMPAT.get(key, 65)

FORTUNE_AREA_ADVICE = {
    "恋愛": {
        "high": ["積極的なアプローチが吉。想いを伝える絶好のタイミングです。", "恋愛運が絶好調！デートの誘いに踏み切って。", "素敵な出会いの予感。笑顔を忘れずに。"],
        "mid": ["恋愛は焦らず自然体で。小さな会話を大切に。", "パートナーとの対話を深める日。", "自分磨きが恋愛運アップの鍵です。"],
        "low": ["恋愛面は慎重に。誤解を生みやすい時期です。", "感情的にならず、落ち着いて行動を。", "今は自分の時間を大切にする時期。"],
    },
    "仕事": {
        "high": ["実力を発揮できる最高の日。新しい挑戦を恐れずに。", "上司や同僚からの評価が上がります。", "クリエイティブな発想が仕事に活きる日。"],
        "mid": ["コツコツと積み重ねることが大切。焦らず着実に。", "チームワークで力を発揮できる日。", "計画を立て直すのに良いタイミングです。"],
        "low": ["無理な仕事は避けて。優先順位を見直して。", "ミスに注意。確認作業を丁寧に行いましょう。", "今日は準備と休息に充てるのがベター。"],
    },
    "金運": {
        "high": ["臨時収入の可能性あり。投資の検討も吉。", "金銭的なチャンスが舞い込む日。直感を信じて。", "節約の努力が実を結ぶ時期。"],
        "mid": ["収支バランスを保つことが大切。無駄遣いに注意。", "計画的な出費なら問題なし。", "将来のための貯蓄を意識して。"],
        "low": ["衝動買いに要注意。大きな出費は避けて。", "財布の紐を締める日。慎重な判断を。", "お金の流れを見直す良い機会です。"],
    },
    "健康": {
        "high": ["エネルギーに満ちた一日。積極的に体を動かして。", "免疫力が高まっています。新しい運動を始めるのも◎。", "心身ともに絶好調！この調子を維持して。"],
        "mid": ["体の声を聞くことが大切。無理をしない範囲で活動を。", "バランスの良い食事と適度な休息を心がけて。", "ストレス発散を意識する日。"],
        "low": ["疲れがたまりやすい時期。早めの就寝を心がけて。", "体調の変化に注意。無理は禁物。", "ゆっくり休養することが最優先です。"],
    },
}

def get_daily_fortune(zodiac: str, today: date) -> dict:
    areas = ["恋愛", "仕事", "金運", "健康"]
    result = {"zodiac": zodiac, "date": today.strftime("%Y年%m月%d日")}
    total = 0
    for area in areas:
        score = _hash_score(f"{zodiac}{area}", today, 45, 100)
        total += score
        h2 = int(hashlib.md5(f"{zodiac}{area}advice{today}".encode()).hexdigest()[:2], 16)
        if score >= 75:
            advice = FORTUNE_AREA_ADVICE[area]["high"][h2 % 3]
        elif score >= 55:
            advice = FORTUNE_AREA_ADVICE[area]["mid"][h2 % 3]
        else:
            advice = FORTUNE_AREA_ADVICE[area]["low"][h2 % 3]
        result[area] = {"score": score, "advice": advice}
    result["total"] = total // 4
    lucky_colors = ["赤", "ピンク", "青", "緑", "黄", "白", "紫", "オレンジ", "金", "銀", "茶", "水色"]
    lc_idx = int(hashlib.md5(f"{zodiac}color{today}".encode()).hexdigest()[:2], 16) % len(lucky_colors)
    result["lucky_color"] = lucky_colors[lc_idx]
    lucky_nums = list(range(1, 10))
    ln_idx = int(hashlib.md5(f"{zodiac}num{today}".encode()).hexdigest()[:2], 16) % len(lucky_nums)
    result["lucky_number"] = lucky_nums[ln_idx]
    return result

# ========== 数秘術 ==========
NUMEROLOGY_PERSONALITY = {
    1: ("開拓者", "強いリーダーシップと独立心を持ちます。新しいことへの挑戦を恐れず、自分の道を切り開く力があります。独創的な発想で周囲を引っ張っていく存在です。"),
    2: ("調停者", "協調性と共感力に優れ、人の気持ちに寄り添うことが得意です。チームの潤滑油として活躍し、繊細な感性で美しいものを大切にします。"),
    3: ("表現者", "豊かな創造力と明るいコミュニケーション能力を持ちます。芸術的センスに優れ、人々に喜びと笑いをもたらす才能があります。"),
    4: ("建設者", "誠実で忍耐強く、地道な努力を積み重ねます。安定と秩序を大切にし、確実に目標を達成する粘り強さを持っています。"),
    5: ("冒険家", "自由を愛し、変化と多様性を求めます。好奇心旺盛で適応力が高く、どんな状況でも柔軟に対応できる能力を持っています。"),
    6: ("奉仕者", "愛情深く責任感が強い性格です。家族や仲間を大切にし、調和のとれた環境を作ることに喜びを感じます。"),
    7: ("探求者", "深い洞察力と直感力を持ちます。真実を追い求める知的好奇心が強く、精神的な成長を大切にする哲学的な性格です。"),
    8: ("成功者", "強い意志と実行力で目標を達成します。ビジネスセンスと物事を大きく動かす力を持ち、物質的な成功を引き寄せます。"),
    9: ("博愛主義者", "広い視野と深い慈悲心を持ちます。人類全体への愛と奉仕の精神を大切にし、精神的な完成度が高い人物です。"),
    11: ("霊感者", "強い直感と霊的な洞察力を持つマスターナンバー。高い精神性と理想主義で、多くの人にインスピレーションを与えます。"),
    22: ("大建築家", "大きなビジョンを現実に変える力を持つマスターナンバー。実用的な夢想家として、社会に永続的な影響を与えます。"),
    33: ("マスター教師", "無条件の愛と精神的な指導力を持つマスターナンバー。深い慈悲と自己犠牲の精神で周囲を癒します。"),
}

PERSONAL_YEAR_MEANING = {
    1: "新しいサイクルの始まり。新しい挑戦を積極的に取り入れ、自分らしい道を切り開く時。",
    2: "人間関係を深める年。パートナーシップや協力関係が重要。焦らず着実に進むことが大切。",
    3: "表現と創造の年。自己表現を楽しみ、社交的な活動が活性化する。明るく前向きに。",
    4: "基盤を固める年。地道な努力と計画的な行動が実を結ぶ。健康管理も大切に。",
    5: "変化と自由の年。新しい経験や変化を積極的に受け入れることで成長できる。",
    6: "愛と責任の年。家族や大切な人との絆を深め、バランスのとれた生活を心がけて。",
    7: "内省と成長の年。自己探求と精神的な成長に集中する時期。一人の時間を大切に。",
    8: "達成と収穫の年。これまでの努力が実を結ぶ時期。キャリアや金運が上昇する。",
    9: "完成と手放しの年。古いものを手放し、新しいサイクルへの準備をする時期。",
    11: "直感と啓示の年。精神的な気づきが多く、人生の転機となる可能性がある。",
    22: "大きな夢を実現する年。野心的な計画が形になりやすい特別な年。",
}

def life_path_number(d: date) -> int:
    return digit_sum(sum(int(c) for c in f"{d.year}{d.month:02d}{d.day:02d}"))

def personal_year_number(d: date, year: int) -> int:
    return digit_sum(d.month + d.day + year)

def get_numerology_full(d: date) -> dict:
    lp = life_path_number(d)
    py = personal_year_number(d, date.today().year)
    name, personality = NUMEROLOGY_PERSONALITY.get(lp, NUMEROLOGY_PERSONALITY[9])
    py_meaning = PERSONAL_YEAR_MEANING.get(py % 9 or 9, PERSONAL_YEAR_MEANING[1])
    return {
        "life_path": lp,
        "name": name,
        "personality": personality,
        "personal_year": py,
        "personal_year_meaning": py_meaning,
    }

# ========== 九星気学 ==========
KYUSEI_NAMES = {
    1: "一白水星", 2: "二黒土星", 3: "三碧木星", 4: "四緑木星", 5: "五黄土星",
    6: "六白金星", 7: "七赤金星", 8: "八白土星", 9: "九紫火星",
}
KYUSEI_ELEMENT = {1: "水", 2: "土", 3: "木", 4: "木", 5: "土", 6: "金", 7: "金", 8: "土", 9: "火"}
KYUSEI_KEYWORD = {
    1: "柔軟・流れる・適応力", 2: "誠実・忍耐・母性", 3: "発展・行動・声",
    4: "信頼・調和・風", 5: "中心・変化・カオス", 6: "権威・完璧・天",
    7: "喜び・楽しみ・金属", 8: "変革・山・蓄積", 9: "情熱・明晰・火",
}
KYUSEI_LUCKY_DIR = {
    1: "北、北北東", 2: "南西、北東", 3: "東、東南東", 4: "東南、南南東",
    5: "中央（移動は控えめに）", 6: "北西、西", 7: "西、北西", 8: "北東、南西", 9: "南、南南東",
}
KYUSEI_PERSONALITY = {
    1: "柔軟性と適応力に優れ、水のように環境に馴染む能力があります。知性と感受性が高く、芸術的センスも豊か。内面は熱く、外見は穏やかな二面性を持ちます。",
    2: "誠実で忍耐強く、縁の下の力持ちタイプ。母性的な愛情を持ち、人の世話をすることに喜びを感じます。地道な努力が報われやすい運を持ちます。",
    3: "活発で行動力があり、新しいことに挑戦するパイオニア気質。明るく社交的で、周囲を元気にする力があります。スピード感と直感力が武器。",
    4: "信頼と誠実さを大切にし、長期的な視点で物事を考えます。コミュニケーション能力が高く、縁を結ぶ仲介役として活躍します。",
    5: "波乱万丈な運命を歩む中心的存在。強いカリスマ性と影響力を持ちますが、感情の浮き沈みが激しい面も。変化を楽しむ力が強みです。",
    6: "完璧主義で高い理想を持ちます。リーダーシップと決断力に優れ、組織の中で実力を発揮。プライドが高く、品格を大切にします。",
    7: "明るく社交的で、人を楽しませる才能があります。弁が立ち、交渉上手。楽しむことに長け、金銭的なセンスも持ち合わせています。",
    8: "粘り強く変革を好む性格。一度決めたことは最後までやり遂げる意志の強さがあります。精神的な強さと蓄積する力を持ちます。",
    9: "情熱的で直感力が強く、物事の本質を見抜く力があります。表現力豊かで注目を集めやすく、芸術や美への感性が高い。",
}

def get_kyusei(d: date) -> int:
    year = d.year if d.month >= 2 else d.year - 1
    return (11 - (year - 1984) % 9) % 9 or 9

def get_year_center(year: int) -> int:
    return (10 - (year - 2024) % 9) % 9 or 9

KYUSEI_YEAR_FORTUNE = {
    (1, 1): "基盤固めの年。無理せず自分らしいペースで進むことが大切です。",
    (1, 2): "人間関係が豊かになる年。新しい縁が仕事にも恋愛にも影響します。",
    (1, 3): "活気に満ちた年。積極的に行動することで運が開けます。",
    (1, 4): "安定と調和の年。信頼関係を大切にすることで発展します。",
    (1, 5): "変化の多い年。柔軟に対応することが成功の鍵です。",
    (1, 6): "実力が認められる年。権威ある人物との縁が生まれます。",
    (1, 7): "楽しみが増える年。趣味や娯楽を通じて運気が上がります。",
    (1, 8): "変革を迫られる年。古い習慣を手放し新しい自分へ。",
    (1, 9): "輝きの年。実力を存分に発揮できるチャンスが訪れます。",
}

def get_kyusei_fortune(birth: date, today: date) -> dict:
    star = get_kyusei(birth)
    year_center = get_year_center(today.year)
    key = (star % 9 or 9, year_center)
    rkey = (star % 9 or 9, (star + year_center) % 9 or 9)
    base_fortune = KYUSEI_YEAR_FORTUNE.get(key, KYUSEI_YEAR_FORTUNE.get((1, year_center), "変化を前向きに受け入れることで運が開ける年です。"))
    month_score = _hash_score(f"{star}month{today.year}{today.month}", today.replace(day=1), 50, 95)
    return {
        "star": star,
        "star_name": KYUSEI_NAMES[star],
        "element": KYUSEI_ELEMENT[star],
        "keyword": KYUSEI_KEYWORD[star],
        "personality": KYUSEI_PERSONALITY[star],
        "lucky_direction": KYUSEI_LUCKY_DIR[star],
        "year_fortune": base_fortune,
        "month_score": month_score,
        "year": today.year,
        "month": today.month,
    }

# ========== 干支 ==========
JUNISHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
JUNISHI_ANIMAL = {
    "子": "🐭 ねずみ", "丑": "🐮 うし", "寅": "🐯 とら", "卯": "🐰 うさぎ",
    "辰": "🐲 たつ", "巳": "🐍 へび", "午": "🐴 うま", "未": "🐑 ひつじ",
    "申": "🐵 さる", "酉": "🐔 とり", "戌": "🐶 いぬ", "亥": "🐗 いのしし",
}

def get_junishi(d: date) -> str:
    year = d.year if d.month >= 2 else d.year - 1
    return JUNISHI_LIST[year % 12]

JUNISHI_COMPAT_GOOD = [
    {"子", "辰", "申"}, {"丑", "巳", "酉"}, {"寅", "午", "戌"}, {"卯", "未", "亥"},
]
JUNISHI_COMPAT_BAD = [
    ("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
]

def junishi_compat(j1: str, j2: str) -> int:
    for g in JUNISHI_COMPAT_GOOD:
        if j1 in g and j2 in g:
            return 90
    for a, b in JUNISHI_COMPAT_BAD:
        if {j1, j2} == {a, b}:
            return 40
    return 65

# ========== 動物占い（60種） ==========
ANIMAL_NAMES = [
    "🐭 チャーミングなねずみ", "🐮 おっとりしたうし", "🐯 頼れるとら", "🐰 優しいうさぎ",
    "🐲 カリスマたつ", "🐍 神秘的なへび", "🐴 自由なうま", "🐑 穏やかなひつじ",
    "🐵 機敏なさる", "🐔 情熱的なとり", "🐶 誠実ないぬ", "🐗 勇気あるいのしし",
]
ANIMAL_SUB = ["理性型", "感性型", "行動型", "思索型", "社交型"]
ANIMAL_PERSONALITY = {
    "🐭 チャーミングなねずみ": "機転が利き、社交上手。好奇心旺盛でチャンスをつかむ能力に長けています。情報収集と人脈構築が得意です。",
    "🐮 おっとりしたうし": "粘り強く誠実。一度決めたことをやり遂げる忍耐力があります。信頼されるペースメーカーとして活躍します。",
    "🐯 頼れるとら": "勇気と行動力で前進するリーダー。直感が鋭く、困難な状況でも果敢に挑戦します。",
    "🐰 優しいうさぎ": "温かみがあり人に好かれる性格。繊細な感受性と審美眼を持ち、平和的な解決を好みます。",
    "🐲 カリスマたつ": "強いカリスマ性と向上心。大きな夢を掲げ、周囲を巻き込む力があります。",
    "🐍 神秘的なへび": "洞察力と直感力に優れた戦略家。静かながら強い意志を持ち、目標に向かって着実に進みます。",
    "🐴 自由なうま": "エネルギッシュで自由を愛します。行動力とスピードが武器で、変化を楽しめる適応力があります。",
    "🐑 穏やかなひつじ": "協調性が高く、芸術的センスに優れます。温かな心で人を癒す才能を持っています。",
    "🐵 機敏なさる": "知性と機敏さで問題を解決します。好奇心と器用さで多彩な才能を発揮するマルチプレイヤー。",
    "🐔 情熱的なとり": "勤勉で完璧主義。細部まで気を配り、高い理想を追いかける情熱があります。",
    "🐶 誠実ないぬ": "誠実で義理堅く、信頼の厚い人格者。チームのために尽くし、大切な人を守る意識が強い。",
    "🐗 勇気あるいのしし": "純粋で一本気。一度決めたら突き進む行動力と、曲がったことを嫌う正義感が特徴です。",
}
SUB_PERSONALITY = {
    "理性型": "論理的思考と分析力に優れ、感情に流されず冷静な判断ができます。",
    "感性型": "豊かな感受性と共感力を持ち、芸術的なセンスや人の気持ちへの理解が深いです。",
    "行動型": "考えるより先に動くフットワークの軽さと、パワフルな実行力が魅力です。",
    "思索型": "深く考えてから行動するタイプ。計画性と洞察力で着実な成果を上げます。",
    "社交型": "人との関わりを大切にし、コミュニケーションの中で輝きます。人脈が強みです。",
}

def get_animal_fortune(d: date) -> dict:
    year = d.year if d.month >= 2 else d.year - 1
    animal_idx = year % 12
    sub_idx = (d.month - 1) // 2 % 5
    animal = ANIMAL_NAMES[animal_idx]
    sub = ANIMAL_SUB[sub_idx]
    return {
        "animal": animal,
        "sub_type": sub,
        "personality": ANIMAL_PERSONALITY[animal],
        "sub_personality": SUB_PERSONALITY[sub],
        "junishi": JUNISHI_LIST[year % 12],
    }

# ========== 姓名判断 ==========
LUCKY_NUMBERS = {
    1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29,
    31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 58, 63, 65, 67, 68, 81,
}
KAKUREI = {
    1: "元始の気力を持つ数。リーダーシップと独立心に恵まれます。",
    3: "表現力と才能に恵まれた数。明るく社交的で、多くの人に愛されます。",
    5: "五行の中心、安定と変化を兼ね備えた強運数です。",
    6: "愛情と責任感が強く、家族的なつながりを大切にします。",
    7: "神秘的な魅力と深い洞察力を持つ数。精神性が高いです。",
    8: "物質的成功をもたらす数。努力が確実に実を結びます。",
    11: "直感力と霊的感覚に優れたマスターナンバー。",
    13: "変革と再生の力を持ちます。困難を乗り越える強さがあります。",
    15: "愛と美に満ちた数。芸術的才能と対人運に恵まれます。",
    16: "情熱的で独立心が旺盛。リーダーとして活躍します。",
    17: "勝利と名誉を示す数。目標達成力が高いです。",
    18: "経済的成功をもたらす数。ビジネスセンスがあります。",
    21: "輝かしい成功を示す数。強い意志と行動力があります。",
    23: "創造力と表現力に恵まれた才能の数。",
    24: "家庭的幸福と財運に恵まれます。",
    25: "明晰な頭脳と企画力を持つ数。",
    29: "智恵と影響力を持つ数。人を導く力があります。",
    31: "粘り強く目標を達成する力があります。",
    32: "縁に恵まれ、多くの人に助けられます。",
}

def get_luck(n: int) -> str:
    return "大吉" if n in LUCKY_NUMBERS else "凶"

def get_seimei_fortune(surname_strokes: int, given_strokes: int) -> dict:
    tenkaku = surname_strokes
    chikaku = given_strokes
    jinkaku = (tenkaku % 10 or 10) + (chikaku // 10 * 10 + 1 if chikaku >= 10 else 1)
    jinkaku = tenkaku % 10 + (chikaku // (10 ** (len(str(chikaku)) - 1)))
    sotokaku = max(1, tenkaku - (tenkaku % 10 or 10)) + max(1, chikaku - (chikaku % 10 or chikaku))
    if sotokaku == 0:
        sotokaku = 1
    sokaku = tenkaku + chikaku

    def desc(n):
        base = KAKUREI.get(n, "")
        luck = get_luck(n)
        return {"value": n, "luck": luck, "desc": base or ("努力と忍耐が実を結ぶ数です。" if luck == "大吉" else "困難を乗り越えることで成長できる数です。")}

    total_lucky = sum(1 for n in [tenkaku, chikaku, jinkaku, sotokaku, sokaku] if n in LUCKY_NUMBERS)
    if total_lucky >= 4:
        overall = "最高運"
    elif total_lucky == 3:
        overall = "大吉"
    elif total_lucky == 2:
        overall = "吉"
    elif total_lucky == 1:
        overall = "小吉"
    else:
        overall = "努力運"

    return {
        "tenkaku": desc(tenkaku),
        "chikaku": desc(chikaku),
        "jinkaku": desc(jinkaku),
        "sotokaku": desc(sotokaku),
        "sokaku": desc(sokaku),
        "overall": overall,
        "lucky_count": total_lucky,
    }

# ========== 相性占い（既存） ==========
NUMEROLOGY_COMPAT = {
    (1, 1): 55, (1, 2): 70, (1, 3): 85, (1, 4): 60, (1, 5): 80,
    (1, 6): 75, (1, 7): 65, (1, 8): 70, (1, 9): 60,
    (2, 2): 80, (2, 3): 70, (2, 4): 85, (2, 5): 65, (2, 6): 90,
    (2, 7): 75, (2, 8): 60, (2, 9): 80,
    (3, 3): 70, (3, 4): 55, (3, 5): 85, (3, 6): 75, (3, 7): 80,
    (3, 8): 65, (3, 9): 85,
    (4, 4): 75, (4, 5): 60, (4, 6): 80, (4, 7): 85, (4, 8): 90,
    (4, 9): 65,
    (5, 5): 65, (5, 6): 70, (5, 7): 75, (5, 8): 65, (5, 9): 80,
    (6, 6): 85, (6, 7): 70, (6, 8): 75, (6, 9): 80,
    (7, 7): 80, (7, 8): 65, (7, 9): 90,
    (8, 8): 70, (8, 9): 75, (9, 9): 85,
}

def numerology_compat(n1: int, n2: int) -> int:
    n1 = n1 % 9 or 9
    n2 = n2 % 9 or 9
    key = (min(n1, n2), max(n1, n2))
    return NUMEROLOGY_COMPAT.get(key, 70)

KYUSEI_COMPAT = {
    (1, 6): 90, (1, 7): 85, (2, 8): 90, (2, 9): 80, (3, 4): 85,
    (3, 9): 75, (6, 1): 90, (7, 1): 85, (8, 2): 90, (9, 2): 80, (9, 3): 75,
}

def kyusei_compat(k1: int, k2: int) -> int:
    key = (k1, k2)
    rkey = (k2, k1)
    if key in KYUSEI_COMPAT:
        return KYUSEI_COMPAT[key]
    if rkey in KYUSEI_COMPAT:
        return KYUSEI_COMPAT[rkey]
    diff = abs(k1 - k2)
    return {0: 70, 1: 75, 2: 65, 3: 72, 4: 68, 5: 60, 6: 72, 7: 65, 8: 75}.get(diff, 68)

GOGYO_YEAR = {0: "金", 1: "金", 2: "水", 3: "水", 4: "木", 5: "木", 6: "火", 7: "火", 8: "土", 9: "土"}
GOGYO_COMPAT = {
    ("木", "火"): 85, ("火", "土"): 80, ("土", "金"): 80, ("金", "水"): 85, ("水", "木"): 85,
    ("木", "土"): 45, ("土", "水"): 45, ("水", "火"): 45, ("火", "金"): 45, ("金", "木"): 45,
    ("木", "木"): 70, ("火", "火"): 70, ("土", "土"): 70, ("金", "金"): 70, ("水", "水"): 70,
}

def get_gogyo(d: date) -> str:
    return GOGYO_YEAR[d.year % 10]

def gogyo_compat(g1: str, g2: str) -> int:
    key = (g1, g2)
    rkey = (g2, g1)
    return GOGYO_COMPAT.get(key, GOGYO_COMPAT.get(rkey, 65))

def clamp(v: int) -> int:
    return max(0, min(100, v))

def get_total_comment(score: int) -> str:
    if score >= 85:
        return "最高の相性です！運命的な出会いかもしれません ✨"
    elif score >= 75:
        return "とても良い相性です。素敵な関係が期待できます 💕"
    elif score >= 65:
        return "良い相性です。お互いを理解し合える関係です 🌟"
    elif score >= 55:
        return "普通の相性です。努力次第で良い関係になれます 🌱"
    else:
        return "個性の違いが大きい2人です。理解し合う努力が大切です 🤝"

def get_axis_advice(axis: str, score: int, name1: str, name2: str) -> str:
    advices = {
        "synchro": {
            80: f"{name1}さんと{name2}さんは波長がとても合っています。言葉がなくても通じ合える関係です。",
            60: f"2人の波長はまずまずです。お互いのペースを尊重することで、居心地よい関係が築けます。",
            0: f"波長の違いがありますが、それが新鮮さにもなります。相手のリズムを理解する姿勢が大切です。",
        },
        "values": {
            80: f"価値観の一致度が高く、大切な決断もスムーズに進みます。",
            60: f"価値観に似た部分もありますが違う面もあります。違いを成長の機会と捉えましょう。",
            0: f"価値観の違いが目立つかもしれません。相手の考えをまず受け入れることから始めましょう。",
        },
        "vibe": {
            80: f"コミュニケーションの相性が抜群です。一緒にいると自然と笑顔になれる関係です。",
            60: f"会話のテンポはまずまずです。相手に合わせると、もっと楽しい時間が過ごせます。",
            0: f"コミュニケーションに工夫が必要です。相手の言葉をしっかり聞くことが関係改善の鍵です。",
        },
        "future": {
            80: f"2人の将来性はとても明るいです。共通の目標を持つことでさらに絆が深まります。",
            60: f"将来に向けて着実に絆を深めていける関係です。",
            0: f"将来像の擦り合わせが必要かもしれません。率直に話し合うことが大切です。",
        },
        "fate": {
            80: f"強い縁で結ばれた2人です。この関係を大切に育てることで人生が豊かになるでしょう。",
            60: f"縁のある2人です。関係を丁寧に育てることで素敵な絆が生まれます。",
            0: f"縁は育てるものでもあります。小さな積み重ねが大きな縁を生み出します。",
        },
    }
    thresholds = advices[axis]
    for threshold in sorted(thresholds.keys(), reverse=True):
        if score >= threshold:
            return thresholds[threshold]
    return ""

def calc_compatibility(name1: str, birth1: date, name2: str, birth2: date) -> dict:
    z1, z2 = get_zodiac(birth1), get_zodiac(birth2)
    lp1, lp2 = life_path_number(birth1), life_path_number(birth2)
    k1, k2 = get_kyusei(birth1), get_kyusei(birth2)
    j1, j2 = get_junishi(birth1), get_junishi(birth2)
    g1, g2 = get_gogyo(birth1), get_gogyo(birth2)

    zs = element_compat(z1, z2)
    ns = numerology_compat(lp1, lp2)
    ks = kyusei_compat(k1, k2)
    js = junishi_compat(j1, j2)
    gs = gogyo_compat(g1, g2)

    synchro = clamp(int(zs * 0.5 + ks * 0.5))
    values = clamp(int(ns * 0.6 + gs * 0.4))
    vibe = clamp(int(zs * 0.4 + js * 0.6))
    future = clamp(int(ns * 0.4 + ks * 0.3 + gs * 0.3))
    fate = clamp(int(js * 0.4 + gs * 0.3 + zs * 0.3))
    total = clamp((synchro + values + vibe + future + fate) // 5)

    return {
        "total": total, "total_comment": get_total_comment(total),
        "synchro": synchro, "values": values, "vibe": vibe, "future": future, "fate": fate,
        "synchro_advice": get_axis_advice("synchro", synchro, name1, name2),
        "values_advice": get_axis_advice("values", values, name1, name2),
        "vibe_advice": get_axis_advice("vibe", vibe, name1, name2),
        "future_advice": get_axis_advice("future", future, name1, name2),
        "fate_advice": get_axis_advice("fate", fate, name1, name2),
        "zodiac1": z1, "zodiac2": z2,
        "life_path1": lp1, "life_path2": lp2,
        "kyusei1": KYUSEI_NAMES[k1], "kyusei2": KYUSEI_NAMES[k2],
        "junishi1": j1, "junishi2": j2,
        "gogyo1": g1, "gogyo2": g2,
    }

# ========== ホロスコープ ==========
# 惑星の黄道経度を簡易計算（J2000.0基準）
def _julian_day(d: date) -> float:
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def _planet_longitude(d: date) -> dict:
    jd = _julian_day(d)
    T = (jd - 2451545.0) / 36525.0  # J2000.0からのユリウス世紀

    def norm(deg):
        return deg % 360

    # 太陽
    L0 = 280.46646 + 36000.76983 * T
    M0 = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    M0r = math.radians(M0 % 360)
    C = (1.914602 - 0.004817 * T) * math.sin(M0r) + 0.019993 * math.sin(2 * M0r)
    sun = norm(L0 + C)

    # 月
    Lm = 218.3165 + 481267.8813 * T
    moon = norm(Lm)

    # 水星
    mercury = norm(252.2509 + 149472.6674 * T)

    # 金星
    venus = norm(181.9798 + 58517.8156 * T)

    # 火星
    mars = norm(355.4330 + 19140.2993 * T)

    # 木星
    jupiter = norm(34.3515 + 3034.9057 * T)

    # 土星
    saturn = norm(50.0774 + 1222.1138 * T)

    # 天王星
    uranus = norm(314.0550 + 428.4882 * T)

    # 海王星
    neptune = norm(304.3487 + 218.4862 * T)

    return {
        "太陽": sun, "月": moon, "水星": mercury, "金星": venus,
        "火星": mars, "木星": jupiter, "土星": saturn,
        "天王星": uranus, "海王星": neptune,
    }

SIGN_NAMES = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座",
]
SIGN_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
PLANET_SYMBOLS = {
    "太陽": "☉", "月": "☽", "水星": "☿", "金星": "♀", "火星": "♂",
    "木星": "♃", "土星": "♄", "天王星": "⛢", "海王星": "♆",
}

PLANET_MEANING = {
    "太陽": "自我・生命力・目的意識",
    "月": "感情・無意識・本能的反応",
    "水星": "思考・コミュニケーション・知性",
    "金星": "愛情・美・調和・価値観",
    "火星": "行動力・情熱・欲望",
    "木星": "拡大・幸運・成長・哲学",
    "土星": "制限・責任・試練・規律",
    "天王星": "革新・自由・突破",
    "海王星": "夢・直感・霊性",
}

SIGN_IN_PLANET = {
    "太陽": {
        "牡羊座": "強い意志と行動力。リーダーシップを発揮し、新しいことへ果敢に挑戦します。",
        "牡牛座": "安定と現実を重視。忍耐強く、美しいものへの感受性が豊かです。",
        "双子座": "知的好奇心が旺盛。コミュニケーション上手で多才な面があります。",
        "蟹座": "感受性が高く家族を大切にします。直感が鋭く共感力があります。",
        "獅子座": "創造力とカリスマ性があります。表現力豊かで人を引き付けます。",
        "乙女座": "分析力と細やかな気配りが得意。誠実で実務能力が高いです。",
        "天秤座": "調和と公平さを重んじます。美意識が高く対人関係が得意です。",
        "蠍座": "強い意志と洞察力。感情が深く、変革を恐れない精神力があります。",
        "射手座": "自由と探求を愛します。哲学的思考と楽観的な精神が特徴です。",
        "山羊座": "野心と実直さを持ちます。着実な努力で高い目標を達成します。",
        "水瓶座": "独創性と博愛精神。革新的なアイデアで社会に貢献します。",
        "魚座": "深い共感力と想像力。芸術的感性と霊的な感受性があります。",
    },
    "月": {
        "牡羊座": "感情的に素直で衝動的。情熱的な反応をします。",
        "牡牛座": "安定した感情。心地よさと安全を求めます。",
        "双子座": "感情を言葉で表現。知的刺激で心が満たされます。",
        "蟹座": "感情豊かで養育的。家庭や家族に安らぎを求めます。",
        "獅子座": "感情を堂々と表現。認められることで活力が生まれます。",
        "乙女座": "感情を分析的に処理。細部への気配りで安心を得ます。",
        "天秤座": "調和の中に安らぎを求めます。感情的なバランスを重視します。",
        "蠍座": "感情が深く強烈。変容を通じて成長します。",
        "射手座": "楽観的で自由な感情。冒険と哲学に心が動きます。",
        "山羊座": "感情をコントロールします。達成感が感情的な満足につながります。",
        "水瓶座": "感情を客観的に見ます。独立性と友情に安らぎを感じます。",
        "魚座": "共感力が極めて高い。夢と直感で感情が動きます。",
    },
}

HOUSE_MEANING = [
    "第1ハウス（自己・外見）", "第2ハウス（財産・価値観）", "第3ハウス（コミュニケーション）",
    "第4ハウス（家庭・ルーツ）", "第5ハウス（創造・恋愛）", "第6ハウス（健康・仕事）",
    "第7ハウス（パートナーシップ）", "第8ハウス（変容・遺産）", "第9ハウス（哲学・旅）",
    "第10ハウス（社会的地位）", "第11ハウス（友人・希望）", "第12ハウス（無意識・秘密）",
]

ASPECT_NAMES = {0: "コンジャンクション(合)", 60: "セクスタイル(六分)", 90: "スクエア(四分)",
                120: "トライン(三分)", 180: "オポジション(対)"}
ASPECT_TYPE = {0: "強化", 60: "調和", 90: "緊張", 120: "調和", 180: "緊張"}
ASPECT_ORB = {0: 8, 60: 6, 90: 8, 120: 8, 180: 8}

def _get_sign(lon: float) -> tuple:
    idx = int(lon // 30) % 12
    degree = lon % 30
    return SIGN_NAMES[idx], SIGN_SYMBOLS[idx], degree

def _calc_aspect(lon1: float, lon2: float):
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    for angle, orb in ASPECT_ORB.items():
        if abs(diff - angle) <= orb:
            return angle, abs(diff - angle)
    return None

def _asc_degree(birth_date: date, birth_hour: int = 12) -> float:
    # 簡易アセンダント：LST近似
    jd = _julian_day(birth_date)
    lst = (100.4606184 + 36000.77004 * (jd - 2451545.0) / 36525.0 + birth_hour * 15) % 360
    return lst

def get_horoscope(birth_date: date, birth_hour: int = 12) -> dict:
    lons = _planet_longitude(birth_date)
    asc_lon = _asc_degree(birth_date, birth_hour)

    planets = {}
    for planet, lon in lons.items():
        sign, symbol, degree = _get_sign(lon)
        house = int((lon - asc_lon) % 360 // 30) + 1
        meaning_in_sign = SIGN_IN_PLANET.get(planet, {}).get(sign, PLANET_MEANING[planet])
        planets[planet] = {
            "sign": sign,
            "sign_symbol": symbol,
            "degree": round(degree, 1),
            "house": house,
            "planet_symbol": PLANET_SYMBOLS[planet],
            "planet_meaning": PLANET_MEANING[planet],
            "sign_meaning": meaning_in_sign,
        }

    # アスペクト計算（主要惑星間）
    main_planets = ["太陽", "月", "水星", "金星", "火星", "木星", "土星"]
    aspects = []
    planet_list = list(lons.items())
    for i in range(len(main_planets)):
        for j in range(i + 1, len(main_planets)):
            p1, p2 = main_planets[i], main_planets[j]
            result = _calc_aspect(lons[p1], lons[p2])
            if result:
                angle, orb = result
                aspects.append({
                    "p1": p1, "p2": p2,
                    "angle": ASPECT_NAMES[angle],
                    "type": ASPECT_TYPE[angle],
                    "orb": round(orb, 1),
                })

    # アセンダント星座
    asc_sign, asc_symbol, asc_deg = _get_sign(asc_lon)

    # 強調サイン（最多惑星）
    sign_count: dict = {}
    for p in planets.values():
        sign_count[p["sign"]] = sign_count.get(p["sign"], 0) + 1
    dominant_sign = max(sign_count, key=lambda s: sign_count[s])

    # 強調エレメント
    elem_count: dict = {}
    for p in planets.values():
        elem = ZODIAC_ELEMENT.get(p["sign"], "")
        if elem:
            elem_count[elem] = elem_count.get(elem, 0) + 1
    dominant_element = max(elem_count, key=lambda e: elem_count[e]) if elem_count else "火"

    return {
        "planets": planets,
        "aspects": aspects,
        "ascendant": {"sign": asc_sign, "symbol": asc_symbol, "degree": round(asc_deg, 1)},
        "dominant_sign": dominant_sign,
        "dominant_element": dominant_element,
        "sun_sign": planets["太陽"]["sign"],
        "moon_sign": planets["月"]["sign"],
        "mercury_sign": planets["水星"]["sign"],
        "venus_sign": planets["金星"]["sign"],
        "mars_sign": planets["火星"]["sign"],
    }

# ========== 四柱推命 ==========
TENKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
CHISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TENKAN_GOGYO = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
                "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
TENKAN_INYO = {"甲": "陽", "乙": "陰", "丙": "陽", "丁": "陰", "戊": "陽",
               "己": "陰", "庚": "陽", "辛": "陰", "壬": "陽", "癸": "陰"}
CHISHI_GOGYO = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
                "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

GOGYO_PERSONALITY = {
    "木": "成長と発展を象徴します。向上心が強く、柔軟性と創造力があります。人情味があり、正義感が強いリーダー気質です。",
    "火": "情熱と知性を象徴します。直感力が鋭く、行動力があります。明るく社交的で、周囲に活力を与えます。",
    "土": "安定と信頼を象徴します。誠実で忍耐強く、周囲から頼りにされます。バランス感覚に優れた調停者です。",
    "金": "意志の強さと決断力を象徴します。几帳面で責任感が強く、目標に向かってブレずに進みます。",
    "水": "知恵と適応力を象徴します。洞察力が鋭く、物事の本質を見抜きます。柔軟な発想で難局を乗り越えます。",
}
GOGYO_LUCK_THIS_YEAR = {
    ("木", "木"): "同じ気が重なり、積極的に動けば大きな成果が出る年です。",
    ("木", "火"): "相生の関係。あなたの努力が次のステージへの扉を開きます。",
    ("木", "土"): "相剋。焦らず土台を固めることが成功への近道です。",
    ("木", "金"): "相剋を受ける年。健康と体力の管理に注意を払いましょう。",
    ("木", "水"): "相生を受ける年。周囲のサポートで運気が上昇します。",
    ("火", "木"): "相生を受ける年。新しい挑戦が実を結ぶ可能性が高い年です。",
    ("火", "火"): "情熱が高まる年。勢いに乗りすぎず、冷静さも保ちましょう。",
    ("火", "土"): "相生の関係。アイデアが形になりやすく、評価が上がります。",
    ("火", "金"): "相剋。計画を丁寧に進め、強引な行動は避けましょう。",
    ("火", "水"): "相剋を受ける年。感情的にならず冷静な判断が求められます。",
    ("土", "木"): "相剋を受ける年。人間関係に注意し、誠実さで乗り越えましょう。",
    ("土", "火"): "相生を受ける年。実力が認められ安定した年になります。",
    ("土", "土"): "安定の年。地道な努力が着実に積み重なります。",
    ("土", "金"): "相生の関係。財運・仕事運ともに上向きの年です。",
    ("土", "水"): "相剋。無理なく自分のペースで進むことが大切です。",
    ("金", "木"): "相剋の年。新たな挑戦より現状維持と内面充実を重視して。",
    ("金", "火"): "相剋を受ける年。健康に気をつけ、無理を避けましょう。",
    ("金", "土"): "相生を受ける年。周囲からの援助で仕事が進みます。",
    ("金", "金"): "意志力が高まる年。決断と実行のタイミングが合いやすいです。",
    ("金", "水"): "相生の関係。知恵と実行力が融合し成果が出やすい年です。",
    ("水", "木"): "相生の関係。アイデアが形になり新しい展開が期待できます。",
    ("水", "火"): "相剋。感情と理性のバランスを保つことが重要です。",
    ("水", "土"): "相剋を受ける年。慎重に物事を進め、基盤を固めましょう。",
    ("水", "金"): "相生を受ける年。人脈と情報が広がり運気が向上します。",
    ("水", "水"): "知恵が磨かれる年。深い洞察から新しい道が開けます。",
}

def _year_gogyo(year: int) -> str:
    return TENKAN_GOGYO[TENKAN[year % 10]]

def get_shichuu(d: date) -> dict:
    # 年柱
    year_tenkan = TENKAN[(d.year - 4) % 10]
    year_chishi = CHISHI[(d.year - 4) % 12]
    # 月柱（簡易：月序で計算）
    month_offset = (d.year - 2000) * 12 + d.month - 1
    month_tenkan = TENKAN[month_offset % 10]
    month_chishi = CHISHI[(d.month - 1 + (d.year % 5) * 2) % 12]
    # 日柱
    jd = int(_julian_day(d))
    day_tenkan = TENKAN[jd % 10]
    day_chishi = CHISHI[jd % 12]

    honmei_gogyo = TENKAN_GOGYO[year_tenkan]
    today_year_gogyo = _year_gogyo(date.today().year)
    luck_key = (honmei_gogyo, today_year_gogyo)
    year_luck = GOGYO_LUCK_THIS_YEAR.get(luck_key, "変化の多い年。柔軟な対応が鍵です。")

    return {
        "year_pillar": f"{year_tenkan}{year_chishi}",
        "month_pillar": f"{month_tenkan}{month_chishi}",
        "day_pillar": f"{day_tenkan}{day_chishi}",
        "honmei_gogyo": honmei_gogyo,
        "honmei_inyo": TENKAN_INYO[year_tenkan],
        "personality": GOGYO_PERSONALITY[honmei_gogyo],
        "year_gogyo": today_year_gogyo,
        "year_luck": year_luck,
        "five_elements": {
            "木": sum(1 for t in [year_tenkan, month_tenkan, day_tenkan] if TENKAN_GOGYO[t] == "木"),
            "火": sum(1 for t in [year_tenkan, month_tenkan, day_tenkan] if TENKAN_GOGYO[t] == "火"),
            "土": sum(1 for t in [year_tenkan, month_tenkan, day_tenkan] if TENKAN_GOGYO[t] == "土"),
            "金": sum(1 for t in [year_tenkan, month_tenkan, day_tenkan] if TENKAN_GOGYO[t] == "金"),
            "水": sum(1 for t in [year_tenkan, month_tenkan, day_tenkan] if TENKAN_GOGYO[t] == "水"),
        },
    }

# ========== バイオリズム ==========
def get_biorhythm(birth: date, target: date) -> dict:
    days = (target - birth).days
    physical = math.sin(2 * math.pi * days / 23)
    emotional = math.sin(2 * math.pi * days / 28)
    intellectual = math.sin(2 * math.pi * days / 33)

    def level(v):
        if v > 0.7:   return "高調期", "#9b6dff"
        if v > 0.2:   return "上昇期", "#60c090"
        if v > -0.2:  return "臨界期", "#f0c040"
        if v > -0.7:  return "下降期", "#f09040"
        return "低調期", "#e06060"

    ph_label, ph_color = level(physical)
    em_label, em_color = level(emotional)
    in_label, in_color = level(intellectual)

    # 過去30日分のデータ
    history = []
    for i in range(-15, 16):
        d2 = date.fromordinal(target.toordinal() + i)
        dd = (d2 - birth).days
        history.append({
            "date": d2,
            "physical": round(math.sin(2 * math.pi * dd / 23), 3),
            "emotional": round(math.sin(2 * math.pi * dd / 28), 3),
            "intellectual": round(math.sin(2 * math.pi * dd / 33), 3),
        })

    return {
        "physical": round(physical, 3), "physical_label": ph_label, "physical_color": ph_color,
        "emotional": round(emotional, 3), "emotional_label": em_label, "emotional_color": em_color,
        "intellectual": round(intellectual, 3), "intellectual_label": in_label, "intellectual_color": in_color,
        "history": history,
    }

# ========== 血液型占い ==========
BLOOD_PERSONALITY = {
    "A": {
        "title": "几帳面な完璧主義者",
        "desc": "責任感が強く、細部まで気を配る性格。計画通りに物事を進めることを好み、誠実で信頼されます。完璧を求めるあまりストレスをためやすい面も。",
        "strength": "計画性・誠実さ・責任感・几帳面",
        "weakness": "心配性・融通が利きにくい・完璧主義",
        "lucky_color": "白・青・緑",
        "love": "真剣な恋愛を好み、相手に誠実に向き合います。じっくり時間をかけて関係を深めます。",
    },
    "B": {
        "title": "自由奔放なマイペース型",
        "desc": "好奇心旺盛で自分のペースを大切にします。興味を持ったことに集中する能力が高く、独創的な発想が得意です。マイペースに見られることも。",
        "strength": "個性・好奇心・集中力・独創性",
        "weakness": "飽きっぽい・自分本位・空気を読まない",
        "lucky_color": "赤・オレンジ・黄",
        "love": "自分らしさを大切にする恋愛スタイル。束縛を嫌い、自由な関係を好みます。",
    },
    "O": {
        "title": "頼れるリーダー型",
        "desc": "大らかで包容力があり、人をまとめる力があります。目標に向かって粘り強く進む行動力が魅力。直感力が高く、勝負強さがあります。",
        "strength": "リーダーシップ・包容力・行動力・直感",
        "weakness": "大雑把・頑固・ライバル意識が強い",
        "lucky_color": "赤・黒・金",
        "love": "情熱的で一途な恋愛をします。一度好きになると深く愛する献身的なタイプ。",
    },
    "AB": {
        "title": "ミステリアスな二面性型",
        "desc": "A型とB型の特性を合わせ持つ複雑な性格。合理的な思考と豊かな感受性が共存します。独自の価値観を持ち、芸術的センスがあります。",
        "strength": "合理性・感受性・芸術センス・独自性",
        "weakness": "気分にムラがある・二面性・神経質",
        "lucky_color": "紫・銀・ピンク",
        "love": "理想が高く、心から信頼できる相手を求めます。関係が深まると非常に献身的になります。",
    },
}

BLOOD_COMPAT = {
    ("A", "A"): (90, "価値観が合い、安定した関係を築けます。お互いの繊細さを理解し合えます。"),
    ("A", "B"): (55, "正反対の性格ですが、B型の自由さにA型が戸惑うことも。お互いの個性を尊重して。"),
    ("A", "O"): (80, "O型のリーダーシップにA型がサポートに回る理想的な組み合わせ。"),
    ("A", "AB"): (70, "AB型の二面性をA型が受け入れられれば、深い絆が生まれます。"),
    ("B", "B"): (75, "お互いのマイペースを尊重できる自由な関係。衝突は少ないです。"),
    ("B", "O"): (85, "B型の個性をO型が包み込む大らかな関係。相性は抜群です。"),
    ("B", "AB"): (80, "B型の自由さとAB型の合理性がうまく噛み合う相性です。"),
    ("O", "O"): (70, "お互いリーダー気質なので衝突も。しかし認め合えれば最強のパートナーに。"),
    ("O", "AB"): (75, "O型の行動力とAB型の思慮深さが補い合う良いバランス。"),
    ("AB", "AB"): (80, "同じ複雑さを持つ者同士。深いところで理解し合える特別な関係です。"),
}

def get_blood_fortune(blood: str, partner_blood: str = None) -> dict:
    info = BLOOD_PERSONALITY[blood]
    result = {"blood": blood, **info}
    if partner_blood:
        key = (min(blood, partner_blood, key=lambda x: ["A","B","O","AB"].index(x)),
               max(blood, partner_blood, key=lambda x: ["A","B","O","AB"].index(x)))
        # 正規化
        pair = tuple(sorted([blood, partner_blood], key=lambda x: ["A","B","O","AB"].index(x)))
        compat = BLOOD_COMPAT.get(pair, (65, "個性の違いを楽しみながら関係を育てましょう。"))
        result["compat_score"] = compat[0]
        result["compat_desc"] = compat[1]
        result["partner_blood"] = partner_blood
    return result

# ========== タロット ==========
TAROT_MAJOR = [
    {"name": "愚者", "num": "0", "symbol": "🃏",
     "upright": "新しい始まり・冒険・無限の可能性。恐れずに一歩を踏み出す時です。",
     "reversed": "無謀・準備不足・リスクへの無関心。もう少し計画を立ててから行動を。"},
    {"name": "魔術師", "num": "I", "symbol": "🎩",
     "upright": "意志力・スキル・集中力。あなたには成功に必要な全てのツールが揃っています。",
     "reversed": "操作・欺き・能力の無駄遣い。自分の力を正しい方向に使うよう心がけて。"},
    {"name": "女教皇", "num": "II", "symbol": "📖",
     "upright": "直感・内なる知識・神秘。内なる声に耳を傾けることが大切な時期です。",
     "reversed": "秘密・表面的な知識・無視された直感。自分の感覚を信じることを忘れずに。"},
    {"name": "女帝", "num": "III", "symbol": "👑",
     "upright": "豊かさ・母性・創造性。愛情と豊かさが満ちる時期。自然の恵みを受け取って。",
     "reversed": "依存・過保護・創造性の停滞。自立心を養い、自分自身を大切に。"},
    {"name": "皇帝", "num": "IV", "symbol": "⚔️",
     "upright": "権威・安定・父性的な保護。しっかりとした基盤と秩序をもたらす時期です。",
     "reversed": "支配・硬直・権威の乱用。柔軟性を持ち、独断を避けましょう。"},
    {"name": "教皇", "num": "V", "symbol": "✝️",
     "upright": "精神的な指導・伝統・信念。伝統的な価値観の中に答えがあります。",
     "reversed": "反体制・個人的な信念・柔軟性。既存のルールを疑い、自分の道を探して。"},
    {"name": "恋人", "num": "VI", "symbol": "💕",
     "upright": "愛・選択・調和。大切な選択の時。心の声に従って選びましょう。",
     "reversed": "不調和・誤った選択・コミュニケーション不足。慎重に選択を見直して。"},
    {"name": "戦車", "num": "VII", "symbol": "🏆",
     "upright": "勝利・意志力・統制。困難を乗り越える強さがあります。前進あるのみ。",
     "reversed": "攻撃性・制御の喪失・敗北。感情のコントロールを取り戻しましょう。"},
    {"name": "力", "num": "VIII", "symbol": "🦁",
     "upright": "勇気・忍耐・内なる力。優しさと強さで状況をコントロールできます。",
     "reversed": "自信喪失・弱さ・恐れ。自分の中の強さを信じて立ち向かって。"},
    {"name": "隠者", "num": "IX", "symbol": "🔦",
     "upright": "内省・孤独・内なる知恵。一人の時間を大切にし、自分を見つめ直す時期。",
     "reversed": "孤立・内向きすぎる・孤独の拒否。自分の殻から出て人とつながりましょう。"},
    {"name": "運命の輪", "num": "X", "symbol": "☸️",
     "upright": "変化・運命・チャンス。人生の転換点。変化を受け入れ流れに乗りましょう。",
     "reversed": "不運・抵抗・停滞。変化への抵抗が問題を長引かせています。"},
    {"name": "正義", "num": "XI", "symbol": "⚖️",
     "upright": "公正・真実・因果応報。誠実な行動が正しい結果をもたらします。",
     "reversed": "不正・偏見・不公平。自分の行動の結果を冷静に見直しましょう。"},
    {"name": "吊られた男", "num": "XII", "symbol": "🙃",
     "upright": "一時停止・新たな視点・自己犠牲。視点を変えることで新しい答えが見えます。",
     "reversed": "停滞・無駄な犠牲・消極性。決断を先送りするのをやめましょう。"},
    {"name": "死神", "num": "XIII", "symbol": "💀",
     "upright": "変容・終わりと始まり・移行。古いものを手放し、新しい段階へ進む時です。",
     "reversed": "変化への抵抗・停滞・行き詰まり。変化を恐れず受け入れることが成長への道。"},
    {"name": "節制", "num": "XIV", "symbol": "⚗️",
     "upright": "バランス・調和・忍耐。焦らず中庸を保つことで物事がうまくいきます。",
     "reversed": "不均衡・過剰・不節制。バランスを取り戻すための見直しが必要です。"},
    {"name": "悪魔", "num": "XV", "symbol": "😈",
     "upright": "束縛・物質主義・影の自己。何かに縛られていませんか？自由になる力はあなたの中に。",
     "reversed": "解放・束縛からの自由・悟り。執着を手放すことで新しい世界が広がります。"},
    {"name": "塔", "num": "XVI", "symbol": "⚡",
     "upright": "突然の変化・崩壊・啓示。衝撃的な変化が起きても、それは必要なリセットです。",
     "reversed": "変化への抵抗・災難の回避・個人的な変容。内なる変革で外の嵐を乗り越えて。"},
    {"name": "星", "num": "XVII", "symbol": "⭐",
     "upright": "希望・インスピレーション・再生。暗いトンネルを抜けた先に光があります。",
     "reversed": "絶望・失望・自己不信。希望を失わず、小さな光を見つけましょう。"},
    {"name": "月", "num": "XVIII", "symbol": "🌙",
     "upright": "幻想・恐れ・無意識。見えないものに惑わされています。真実を見極めて。",
     "reversed": "混乱の解消・恐れの克服・明晰さ。霧が晴れ、真実が見えてきます。"},
    {"name": "太陽", "num": "XIX", "symbol": "☀️",
     "upright": "喜び・成功・活力。明るいエネルギーに満ちた時期。自信を持って輝いて。",
     "reversed": "楽観的すぎる・一時的な暗雲・自己表現の抑制。内なる光を信じて。"},
    {"name": "審判", "num": "XX", "symbol": "📯",
     "upright": "覚醒・再生・内なる呼び声。人生の重要な決断の時。自分の真の使命に気づいて。",
     "reversed": "自己疑惑・無視された呼び声・後悔。過去を手放し、新しい自分を受け入れて。"},
    {"name": "世界", "num": "XXI", "symbol": "🌍",
     "upright": "完成・達成・全体性。一つのサイクルの完成。達成を祝い次のステージへ。",
     "reversed": "未完成・停滞・近道を求める。最後まで諦めず完成させましょう。"},
]

SPREAD_TYPES = {
    "1枚引き（今日のメッセージ）": 1,
    "3枚引き（過去・現在・未来）": 3,
    "5枚引き（状況・障害・アドバイス・隠れた影響・結果）": 5,
}
SPREAD_POSITIONS = {
    1: ["今日のメッセージ"],
    3: ["過去", "現在", "未来"],
    5: ["現在の状況", "障害・課題", "アドバイス", "隠れた影響", "最終的な結果"],
}

import random as _random

def draw_tarot(num_cards: int, seed: int = None) -> list:
    rng = _random.Random(seed)
    cards = _random.sample(TAROT_MAJOR, num_cards) if seed is None else rng.sample(TAROT_MAJOR, num_cards)
    result = []
    for card in cards:
        is_reversed = (rng if seed else _random).choice([True, False])
        result.append({**card, "is_reversed": is_reversed})
    return result

# ========== 易経（六十四卦） ==========
HEXAGRAMS = [
    ("乾", "乾為天", "天", "天の力・創造・積極性。大きな力が動き始めます。強い意志で進んでください。"),
    ("坤", "坤為地", "地", "地の力・受容・忍耐。受け入れ、育てる時期です。柔軟に対応しましょう。"),
    ("水雷屯", "屯", "困難の始まり", "困難の中に芽吹きあり。初期の苦労が後の成功の礎となります。"),
    ("山水蒙", "蒙", "啓蒙", "学びと成長の時。謙虚に教えを受け入れることが大切です。"),
    ("水天需", "需", "待機", "時を待て。焦らず準備を整えることが成功への近道です。"),
    ("天水訟", "訟", "争い", "対立を避け、妥協点を見つける智恵が必要です。"),
    ("地水師", "師", "軍師", "統率力を発揮する時。組織をまとめ目標に向かいましょう。"),
    ("水地比", "比", "親しむ", "人との絆を大切に。協力し合うことで大きな力が生まれます。"),
    ("風天小畜", "小畜", "小さな蓄積", "小さな積み重ねが大きな力となります。今は準備の時です。"),
    ("天沢履", "履", "礼", "礼儀と誠実さで道を切り開く時。正しい行いが運を開きます。"),
    ("地天泰", "泰", "平和・繁栄", "平和と繁栄の時。積極的に動くことで幸運をつかめます。"),
    ("天地否", "否", "停滞", "一時的な停滞期。内面を整え次の飛躍に備えましょう。"),
    ("天火同人", "同人", "同志", "志を同じくする仲間と力を合わせましょう。協力が成功の鍵です。"),
    ("火天大有", "大有", "大きな所有", "豊かさと成功が訪れる時。謙虚さを忘れずに大きく動きましょう。"),
    ("地山謙", "謙", "謙虚", "謙虚さが最大の強み。奢らず誠実に行動することで運が開けます。"),
    ("雷地豫", "豫", "喜び・準備", "喜びと活力に満ちた時。前向きな行動が周囲に伝播します。"),
    ("沢雷随", "随", "随う", "時の流れに随うことが大切。変化に柔軟に対応しましょう。"),
    ("山風蠱", "蠱", "腐敗の修正", "問題の根本を見直す時。勇気を持って改革に取り組みましょう。"),
    ("地沢臨", "臨", "臨む", "大きな機会が近づいています。準備を整え積極的に臨んでください。"),
    ("風地観", "観", "観察", "静かに観察することで本質が見えてきます。焦らず見極めて。"),
    ("火雷噬嗑", "噬嗑", "噛み砕く", "障害を克服する時。正面から問題に取り組む勇気を持って。"),
    ("山火賁", "賁", "飾り", "外見だけでなく内面の充実も大切。本質的な美しさを磨きましょう。"),
    ("山地剥", "剥", "剥ぎ取り", "古いものが剥がれ落ちる時期。変化を恐れず受け入れましょう。"),
    ("地雷復", "復", "回復", "回復と再生の時。エネルギーが戻り、新しい始まりが来ます。"),
    ("天雷无妄", "无妄", "無為自然", "自然の流れに任せることが大切。作為を捨て誠実に行動を。"),
    ("山天大畜", "大畜", "大きな蓄積", "知識と力を蓄える時。学びと経験が財産になります。"),
    ("山雷頤", "頤", "養い", "心身を養う時期。食事と休息を大切に、英気を養いましょう。"),
    ("沢風大過", "大過", "大きな過ち", "限界を超えた状態。無理をせず一歩引くことも勇気です。"),
    ("坎為水", "坎", "水・危険", "困難な状況ですが、誠実さと冷静さで乗り越えられます。"),
    ("離為火", "離", "火・明晰", "明るく燃える火のように輝く時。知性と情熱で前進しましょう。"),
    ("沢山咸", "咸", "感応", "感受性が高まる時。人との心のつながりを大切にしましょう。"),
    ("雷風恒", "恒", "恒久", "継続と恒久の時。粘り強く続けることで大きな成果が生まれます。"),
    ("天山遁", "遁", "退く", "一時的な退却が最善の策。力を蓄えて再起の時を待ちましょう。"),
    ("雷天大壮", "大壮", "大いなる壮大", "強大な力が満ちています。ただし慎重さも忘れずに。"),
    ("火地晋", "晋", "前進", "快調な前進の時。積極的に行動することで目標に近づきます。"),
    ("地火明夷", "明夷", "光の傷", "困難な時期ですが、内なる光を守りましょう。必ず夜明けは来ます。"),
    ("風火家人", "家人", "家族", "家庭と仲間を大切にする時。身近な人との絆が力の源です。"),
    ("火沢睽", "睽", "背離", "意見の相違があっても、共通点を見つけることで前進できます。"),
    ("水山蹇", "蹇", "足の不自由", "困難な道のりですが、粘り強く進むことで道が開けます。"),
    ("雷水解", "解", "解放", "問題が解決に向かう時。束縛から解放され自由が訪れます。"),
    ("山沢損", "損", "損なう", "今は与える時期。自己犠牲が将来の大きな利益につながります。"),
    ("風雷益", "益", "益する", "得られる時期。チャンスを掴み、積極的に行動しましょう。"),
    ("沢天夬", "夬", "決断", "決断の時が来ました。迷わず行動することで状況が打開されます。"),
    ("天風姤", "姤", "出会い", "予期せぬ出会いがあります。縁を大切にしましょう。"),
    ("沢地萃", "萃", "集まり", "人が集まる時。リーダーシップを発揮しましょう。"),
    ("地風升", "升", "上昇", "着実な上昇の時期。地道な努力が実を結びます。"),
    ("沢水困", "困", "困窮", "苦境にあっても希望を持ち続けて。必ず出口があります。"),
    ("水風井", "井", "井戸", "深い知恵を汲み上げる時。学びを深めましょう。"),
    ("沢火革", "革", "革命", "大きな変革の時。古いものを手放し新しい時代を切り開きましょう。"),
    ("火風鼎", "鼎", "鼎", "新しい体制と文化を作る時。創造的な活動が実を結びます。"),
    ("震為雷", "震", "雷・震動", "衝撃と覚醒の時。震えを恐れず、その後の静けさを活かして。"),
    ("艮為山", "艮", "山・停止", "立ち止まって内省する時。焦らず自分を見つめ直しましょう。"),
    ("風山漸", "漸", "漸進", "一歩一歩着実に進む時。急がず自然のペースで前進しましょう。"),
    ("雷沢帰妹", "帰妹", "嫁ぐ", "新しい関係への移行の時。誠実さを持って新たな一歩を。"),
    ("雷火豊", "豊", "豊かさ", "豊かさと充実の最高潮。この恵みを周囲と分かち合いましょう。"),
    ("火山旅", "旅", "旅", "変化と移動の時。柔軟に対応し新しい経験を積みましょう。"),
    ("巽為風", "巽", "風・謙虚", "柔軟な思考と謙虚な行動で物事を進めましょう。"),
    ("兌為沢", "兌", "沢・喜び", "喜びと交流の時。笑顔と積極的なコミュニケーションが鍵です。"),
    ("風水渙", "渙", "散らす", "硬直した状況を解きほぐす時。固執を手放しましょう。"),
    ("水沢節", "節", "節制", "節度を持った行動が大切。無理のない範囲で着実に進みましょう。"),
    ("風沢中孚", "中孚", "誠信", "誠実さと信頼が力になる時。真心を持って行動しましょう。"),
    ("雷山小過", "小過", "小さな過ち", "小さなミスに気をつけて。慎重さと謙虚さを忘れずに。"),
    ("水火既済", "既済", "既に成る", "目標達成の時。成功を確かなものにし、次の準備を始めましょう。"),
    ("火水未済", "未済", "未だ成らず", "もう少しで完成。諦めずに最後まで取り組みましょう。"),
]

def draw_hexagram(seed: int = None) -> dict:
    rng = _random.Random(seed) if seed else _random
    idx = rng.randint(0, 63)
    changing_lines = sorted(rng.sample(range(1, 7), rng.randint(0, 3)))
    hex_data = HEXAGRAMS[idx]
    return {
        "number": idx + 1,
        "kanji": hex_data[0],
        "name": hex_data[1],
        "theme": hex_data[2],
        "message": hex_data[3],
        "changing_lines": changing_lines,
        "lines": [("陽" if (idx >> (5 - i)) & 1 else "陰") for i in range(6)],
    }
