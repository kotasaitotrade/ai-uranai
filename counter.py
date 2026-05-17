"""占いビュー数カウンター（Google Drive永続化）"""
import json
import io
import os
import streamlit as st

FORTUNE_KEYS = [
    "compat", "zodiac", "numerology", "kyusei", "animal",
    "seimei", "horoscope", "shichuu", "biorhythm", "blood", "tarot", "ekikyo",
]

FORTUNE_LABELS = {
    "compat":     "💫 相性占い",
    "zodiac":     "⭐ 星座占い",
    "numerology": "🔢 数秘術",
    "kyusei":     "☯️ 九星気学",
    "animal":     "🐾 動物占い",
    "seimei":     "✍️ 姓名判断",
    "horoscope":  "🌌 ホロスコープ",
    "shichuu":    "🀄 四柱推命",
    "biorhythm":  "📈 バイオリズム",
    "blood":      "🩸 血液型",
    "tarot":      "🃏 タロット",
    "ekikyo":     "☯ 易経",
}

COUNTER_FILENAME = "uranai_view_counts.json"

def _get_drive_service():
    """Service Accountを使ってGoogle Drive APIを初期化"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        sa_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not sa_info:
            print("[counter] GOOGLE_SERVICE_ACCOUNT_JSON not set")
            return None

        sa_dict = json.loads(sa_info)
        creds = service_account.Credentials.from_service_account_info(
            sa_dict,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        svc = build("drive", "v3", credentials=creds)
        print("[counter] Drive service initialized OK")
        return svc
    except Exception as e:
        print(f"[counter] Drive init error: {e}")
        return None


def _get_folder_id():
    return os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")


def _find_file(service, folder_id):
    """カウンターファイルのIDを検索"""
    try:
        q = f"name='{COUNTER_FILENAME}' and trashed=false"
        if folder_id:
            q += f" and '{folder_id}' in parents"
        res = service.files().list(q=q, fields="files(id)").execute()
        files = res.get("files", [])
        return files[0]["id"] if files else None
    except Exception:
        return None


def _load_from_drive(service, file_id):
    """DriveからJSONをダウンロードしてdictで返す"""
    try:
        from googleapiclient.http import MediaIoBaseDownload
        fh = io.BytesIO()
        req = service.files().get_media(fileId=file_id)
        dl = MediaIoBaseDownload(fh, req)
        done = False
        while not done:
            _, done = dl.next_chunk()
        fh.seek(0)
        return json.loads(fh.read().decode("utf-8"))
    except Exception:
        return {}


def _save_to_drive(service, data: dict, file_id=None, folder_id=""):
    """dictをJSONとしてDriveに保存（上書き or 新規作成）"""
    try:
        from googleapiclient.http import MediaIoBaseUpload
        content = json.dumps(data, ensure_ascii=False).encode("utf-8")
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
        if file_id:
            service.files().update(fileId=file_id, media_body=media).execute()
        else:
            meta = {"name": COUNTER_FILENAME}
            if folder_id:
                meta["parents"] = [folder_id]
            service.files().create(body=meta, media_body=media, fields="id").execute()
    except Exception:
        pass


@st.cache_resource
def _get_counts_resource():
    """セッションをまたいでカウントを保持するリソース（Streamlitプロセス内共有）"""
    service = _get_drive_service()
    folder_id = _get_folder_id()
    counts = {k: 0 for k in FORTUNE_KEYS}

    if service:
        file_id = _find_file(service, folder_id)
        if file_id:
            remote = _load_from_drive(service, file_id)
            for k in FORTUNE_KEYS:
                counts[k] = remote.get(k, 0)

    return {"counts": counts, "service": service, "folder_id": folder_id}


def increment(key: str):
    """指定した占いのビュー数を+1してDriveに保存"""
    if key not in FORTUNE_KEYS:
        return
    res = _get_counts_resource()
    res["counts"][key] = res["counts"].get(key, 0) + 1

    service = res["service"]
    if service:
        folder_id = res["folder_id"]
        file_id = _find_file(service, folder_id)
        _save_to_drive(service, res["counts"], file_id, folder_id)


def get_counts() -> dict:
    """全占いのビュー数を返す"""
    return dict(_get_counts_resource()["counts"])


def render_ranking():
    """ランキングをStreamlit UIとして表示"""
    counts = get_counts()
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    total = sum(counts.values()) or 1

    st.markdown("### 🏆 人気占いランキング")
    medals = ["🥇", "🥈", "🥉"]

    for i, (key, count) in enumerate(sorted_items):
        label = FORTUNE_LABELS.get(key, key)
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        pct = count / total * 100
        bar_w = max(int(pct), 1)
        color = "#f0c040" if i == 0 else "#c0c0c0" if i == 1 else "#cd7f32" if i == 2 else "#9b6dff"
        st.markdown(f"""
<div style='display:flex;align-items:center;gap:10px;margin:6px 0;'>
  <div style='min-width:28px;font-size:18px;text-align:center;'>{medal}</div>
  <div style='min-width:130px;color:#d4b8ff;font-size:14px;'>{label}</div>
  <div style='flex:1;background:#1a1040;border-radius:6px;height:16px;'>
    <div style='background:{color};width:{bar_w}%;height:16px;border-radius:6px;'></div>
  </div>
  <div style='min-width:55px;text-align:right;color:{color};font-size:13px;font-weight:bold;'>{count:,}回</div>
</div>""", unsafe_allow_html=True)
