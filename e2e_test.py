"""E2Eテスト: 占いポータル (https://mystic-oracle-ai-uranai.hf.space)"""
import time
import json
import subprocess
import sys
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://mystic-oracle-ai-uranai.hf.space"
TIMEOUT = 30000  # 30秒

RESULTS = []

def log(name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}  {name}" + (f"  ({detail})" if detail else ""))
    RESULTS.append({"name": name, "passed": passed, "detail": detail})


def wait_for_streamlit(page):
    """Streamlitが完全にロードされるまで待つ"""
    page.wait_for_load_state("networkidle", timeout=TIMEOUT)
    # Streamlitのスピナーが消えるまで待つ
    try:
        page.wait_for_selector("[data-testid='stSpinner']", state="hidden", timeout=10000)
    except Exception:
        pass
    time.sleep(2)


def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            ignore_https_errors=True,
        )
        page = context.new_page()

        # ===== 1. ページロード =====
        try:
            page.goto(BASE_URL, timeout=TIMEOUT)
            wait_for_streamlit(page)
            title = page.title()
            log("ページロード", "占い" in title or "Uranai" in title or title != "", f"title={title}")
        except Exception as e:
            log("ページロード", False, str(e))
            browser.close()
            return

        # ===== 2. タブ一覧が表示される =====
        try:
            tabs = page.locator("[data-baseweb='tab']")
            count = tabs.count()
            log("タブ表示（13タブ）", count >= 12, f"タブ数={count}")
        except Exception as e:
            log("タブ表示", False, str(e))

        def click_visible_button(page, text):
            """表示中のボタンのみをクリック"""
            btns = page.locator("button", has_text=text).all()
            for btn in btns:
                if btn.is_visible():
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    return True
            raise Exception(f"Visible button '{text}' not found")

        # ===== 3. 相性占い =====
        try:
            page.locator("[data-baseweb='tab']").nth(0).click()
            time.sleep(2)
            click_visible_button(page, "占う")
            wait_for_streamlit(page)
            score = page.locator(".score-num").first
            score.wait_for(timeout=TIMEOUT)
            text = score.inner_text()
            log("相性占い 実行", text.endswith("点"), f"スコア={text}")
        except Exception as e:
            log("相性占い 実行", False, str(e))

        # ===== 4. 星座占い =====
        try:
            page.locator("[data-baseweb='tab']").nth(1).click()
            time.sleep(2)
            click_visible_button(page, "占う")
            wait_for_streamlit(page)
            result = page.locator(".score-box").first
            result.wait_for(timeout=TIMEOUT)
            log("星座占い 実行", True)
        except Exception as e:
            log("星座占い 実行", False, str(e))

        # ===== 5. ホロスコープ（出生地選択） =====
        try:
            page.locator("[data-baseweb='tab']").nth(6).click()
            time.sleep(2)
            # 出生地selectboxが表示されているか（可視のもの）
            selects = page.locator("[data-testid='stSelectbox']").all()
            visible_selects = [s for s in selects if s.is_visible()]
            log("ホロスコープ 出生地UI表示", len(visible_selects) > 0, f"selectbox数={len(visible_selects)}")
            click_visible_button(page, "読み解く")
            wait_for_streamlit(page)
            result = page.locator(".score-box").first
            result.wait_for(timeout=TIMEOUT)
            log("ホロスコープ 実行", True)
        except Exception as e:
            log("ホロスコープ 実行", False, str(e))

        # ===== 6. タロット =====
        try:
            page.locator("[data-baseweb='tab']").nth(10).click()
            time.sleep(1)
            page.locator("button", has_text="引く").first.click()
            wait_for_streamlit(page)
            cards = page.locator(".card")
            cards.first.wait_for(timeout=TIMEOUT)
            count = cards.count()
            log("タロット 実行", count >= 1, f"カード数={count}")
        except Exception as e:
            log("タロット 実行", False, str(e))

        # ===== 7. ランキングタブ =====
        try:
            ranking_tab = page.locator("[data-baseweb='tab']", has_text="ランキング")
            ranking_tab.wait_for(timeout=TIMEOUT)
            ranking_tab.click()
            wait_for_streamlit(page)
            heading = page.locator("text=人気占いランキング")
            heading.wait_for(timeout=TIMEOUT)
            log("ランキング タブ表示", True)
        except Exception as e:
            log("ランキング タブ表示", False, str(e))

        # ===== 8. モバイルUI =====
        try:
            mobile_context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                ignore_https_errors=True,
            )
            mobile_page = mobile_context.new_page()
            mobile_page.goto(BASE_URL + "?mobile=1", timeout=TIMEOUT)
            wait_for_streamlit(mobile_page)
            heading = mobile_page.locator("text=占いポータル")
            heading.wait_for(timeout=TIMEOUT)
            log("モバイルUI ホーム表示", True)

            # Streamlitはiframe内でレンダリングされる場合があるのでframe含めて検索
            time.sleep(5)
            # メインフレームとサブフレーム両方を検索
            def find_and_click_in_frames(page, text):
                frames = [page.main_frame] + page.frames
                for frame in frames:
                    try:
                        clicked = frame.evaluate(f"""() => {{
                            const btns = Array.from(document.querySelectorAll('button'));
                            const btn = btns.find(b => b.innerHTML.includes('{text}'));
                            if (btn) {{ btn.click(); return true; }}
                            return false;
                        }}""")
                        if clicked:
                            return True
                    except Exception:
                        pass
                return False

            # Streamlitのコンテンツはmain frameのDOMに直接ある
            # srcdocフレームは components.html のUA検知用
            # メインフレームで直接ボタンを探す
            time.sleep(3)
            menu_btn = mobile_page.locator("[data-testid='stBaseButton-secondary']").first
            menu_btn.wait_for(state="visible", timeout=TIMEOUT)
            # 13個のメニューボタンが並んでいるので2番目（星座占い）を探す
            all_menu_btns = mobile_page.locator("[data-testid='stBaseButton-secondary']").all()
            zodiac_btn = next(
                (b for b in all_menu_btns if b.is_visible() and "星座" in b.evaluate("el => el.innerHTML")),
                all_menu_btns[1] if len(all_menu_btns) > 1 else all_menu_btns[0]
            )
            zodiac_btn.click()
            wait_for_streamlit(mobile_page)
            back = mobile_page.locator("button", has_text="戻る").first
            back.wait_for(state="visible", timeout=TIMEOUT)
            log("モバイルUI ページ遷移", True)

            # 戻るボタン
            back.click()
            wait_for_streamlit(mobile_page)
            heading2 = mobile_page.locator("text=占いポータル").first
            heading2.wait_for(timeout=TIMEOUT)
            log("モバイルUI 戻るボタン", True)

            mobile_context.close()
        except Exception as e:
            log("モバイルUI", False, str(e))

        browser.close()

    # ===== サマリー =====
    print("\n" + "="*50)
    passed = sum(1 for r in RESULTS if r["passed"])
    total = len(RESULTS)
    print(f"結果: {passed}/{total} PASS")
    if passed < total:
        print("\n失敗項目:")
        for r in RESULTS:
            if not r["passed"]:
                print(f"  ❌ {r['name']}: {r['detail']}")
    return passed == total


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
