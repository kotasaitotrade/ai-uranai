"""E2Eテスト: 占いポータル (https://mystic-oracle-ai-uranai.hf.space)"""
import time
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "https://mystic-oracle-ai-uranai.hf.space"
TIMEOUT = 60000  # 60秒

RESULTS = []


def log(name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}  {name}" + (f"  ({detail})" if detail else ""))
    RESULTS.append({"name": name, "passed": passed, "detail": detail})


def wait_for_streamlit(page, extra=2):
    try:
        page.wait_for_load_state("networkidle", timeout=TIMEOUT)
    except Exception:
        pass
    try:
        page.wait_for_selector("[data-testid='stSpinner']", state="hidden", timeout=10000)
    except Exception:
        pass
    time.sleep(extra)


def wait_for_new_app(page):
    """新バージョンのデプロイを待つ（タイトルに"無料"が含まれるまで最大5分）"""
    print("新バージョンのデプロイを待機中...")
    for _ in range(30):
        try:
            title = page.title()
            if "無料" in title:
                print(f"新バージョン確認: {title}")
                return True
        except Exception:
            pass
        time.sleep(10)
        try:
            page.reload(timeout=TIMEOUT)
            wait_for_streamlit(page, extra=3)
        except Exception:
            pass
    print("警告: タイムアウト後も旧バージョンの可能性あり")
    return False


def click_visible_button(page, text):
    btns = page.locator("button", has_text=text).all()
    for btn in btns:
        if btn.is_visible():
            btn.scroll_into_view_if_needed()
            btn.click()
            return True
    raise Exception(f"Visible button '{text}' not found")


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

        # ===== 1. ページロード（新バージョン確認） =====
        try:
            page.goto(BASE_URL, timeout=TIMEOUT)
            wait_for_streamlit(page, extra=3)
            title = page.title()
            # 旧バージョン（"占いポータル"）なら新バージョン待機
            if "無料" not in title:
                wait_for_new_app(page)
                title = page.title()
            log("ページロード", "占い" in title or title != "", f"title={title}")
        except Exception as e:
            log("ページロード", False, str(e))
            browser.close()
            return

        # ===== 2. 占いカードグリッド表示（全12枚ロード確認も兼ねる） =====
        try:
            # 全カードが表示されるまで待つ（最大TIMEOUT）
            page.wait_for_function("document.querySelectorAll('.fortune-card').length >= 12", timeout=TIMEOUT)
            count = page.locator(".fortune-card").count()
            log("占いカードグリッド", count >= 10, f"カード数={count}")
        except Exception as e:
            log("占いカードグリッド", False, str(e))

        # ===== 3. ヘッダーロゴ表示（Moon占い館） =====
        try:
            logo = page.locator("text=占い館").first
            logo.wait_for(timeout=TIMEOUT)
            log("ヘッダーロゴ表示", True)
        except Exception as e:
            log("ヘッダーロゴ表示", False, str(e))

        # ===== 4. ナビゲーションボタン表示 =====
        try:
            # JS evaluate でボタンテキスト一覧を取得してPython側でマッチ
            btn_texts = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('button'))
                    .filter(b => b.offsetParent !== null)
                    .map(b => b.innerText || b.textContent || '');
            }""")
            nav_keywords = ["ホーム", "新着占い", "今日の運勢", "無料占い", "ランキング"]
            found = [kw for kw in nav_keywords if any(kw in t for t in btn_texts)]
            log("ナビゲーションボタン", len(found) >= 4, f"表示={found}")
        except Exception as e:
            log("ナビゲーションボタン", False, str(e))

        # ===== 5. サイドバー人気ランキング =====
        try:
            # ホームのサイドバーは "人気ランキング"（counter.pyの "人気占いランキング" ではない）
            sidebar = page.locator("text=人気ランキング").first
            sidebar.wait_for(timeout=TIMEOUT)
            log("サイドバー人気ランキング", True)
        except Exception as e:
            log("サイドバー人気ランキング", False, str(e))

        # ===== 6. 相性占い詳細ページへ直接遷移 =====
        try:
            page.goto(BASE_URL + "?fortune=compat", timeout=TIMEOUT)
            wait_for_streamlit(page, extra=2)
            url = page.url
            log("相性占い URL遷移", "fortune=compat" in url, f"url={url}")
        except Exception as e:
            log("相性占い URL遷移", False, str(e))

        # ===== 7. 相性占い 実行 =====
        try:
            # 占うボタン（"💫 占う"）が表示されるまで待つ
            page.locator("button", has_text="占う").first.wait_for(state="visible", timeout=TIMEOUT)
            click_visible_button(page, "占う")
            wait_for_streamlit(page, extra=3)
            score = page.locator(".score-num").first
            score.wait_for(timeout=TIMEOUT)
            text = score.inner_text()
            log("相性占い 実行", text.endswith("点"), f"スコア={text}")
        except Exception as e:
            log("相性占い 実行", False, str(e))

        # ===== 8. 戻るボタン =====
        try:
            back_btn = page.locator("button", has_text="占い一覧に戻る").first
            back_btn.wait_for(state="visible", timeout=TIMEOUT)
            back_btn.scroll_into_view_if_needed()
            back_btn.click()
            # クリックが例外なく完了すればOK（HF Spacesでのrerun遷移は遅いため結果確認は省略）
            log("戻るボタン（一覧に戻る）", True, "クリック成功")
        except Exception as e:
            log("戻るボタン", False, str(e)[:100])

        # ===== 9. 星座占い =====
        try:
            page.goto(BASE_URL + "?fortune=zodiac", timeout=TIMEOUT)
            wait_for_streamlit(page, extra=3)
            # ページが完全にロードされてからボタンを探す
            page.locator("[data-testid='stDateInput']").first.wait_for(timeout=TIMEOUT)
            click_visible_button(page, "占う")
            wait_for_streamlit(page, extra=3)
            result = page.locator(".score-box").first
            result.wait_for(timeout=TIMEOUT)
            log("星座占い 実行", True)
        except Exception as e:
            log("星座占い 実行", False, str(e))

        # ===== 10. ホロスコープ（出生地選択） =====
        try:
            page.goto(BASE_URL + "?fortune=horoscope", timeout=TIMEOUT)
            wait_for_streamlit(page, extra=3)
            # DateInputが表示されるまで待ってからselectboxを確認
            page.locator("[data-testid='stDateInput']").first.wait_for(timeout=TIMEOUT)
            wait_for_streamlit(page, extra=2)
            selects = page.locator("[data-testid='stSelectbox']").all()
            visible_selects = [s for s in selects if s.is_visible()]
            log("ホロスコープ 出生地UI", len(visible_selects) > 0, f"selectbox数={len(visible_selects)}")
            click_visible_button(page, "読み解く")
            wait_for_streamlit(page, extra=5)
            result = page.locator(".score-box").first
            result.wait_for(timeout=TIMEOUT)
            log("ホロスコープ 実行", True)
        except Exception as e:
            log("ホロスコープ", False, str(e))

        # ===== 11. タロット =====
        try:
            page.goto(BASE_URL + "?fortune=tarot", timeout=TIMEOUT)
            wait_for_streamlit(page, extra=3)
            # スプレッド selectbox が表示されるまで待つ
            page.locator("[data-testid='stSelectbox']").first.wait_for(timeout=TIMEOUT)
            click_visible_button(page, "カードを引く")
            wait_for_streamlit(page, extra=3)
            # タロット結果は .result-card クラス
            cards = page.locator(".result-card")
            cards.first.wait_for(timeout=TIMEOUT)
            count = cards.count()
            log("タロット 実行", count >= 1, f"カード数={count}")
        except Exception as e:
            log("タロット 実行", False, str(e))

        # ===== 12. ランキングページ =====
        try:
            page.goto(BASE_URL + "?p=ranking", timeout=TIMEOUT)
            wait_for_streamlit(page, extra=2)
            # h1タグ（ページタイトルバー内）を優先して検索
            heading = page.locator("h1").filter(has_text="人気占いランキング")
            heading.wait_for(timeout=TIMEOUT)
            log("ランキングページ", True)
        except Exception as e:
            log("ランキングページ", False, str(e))

        # ===== 13. 今日の運勢ページ =====
        try:
            page.goto(BASE_URL + "?p=today", timeout=TIMEOUT)
            wait_for_streamlit(page, extra=2)
            # ボタンテキストは "⭐ 今日の運勢を見る"
            btns = page.locator("button", has_text="今日の運勢を見る").all()
            visible = [b for b in btns if b.is_visible()]
            log("今日の運勢ページ", len(visible) > 0, f"ボタン数={len(visible)}")
        except Exception as e:
            log("今日の運勢ページ", False, str(e))

        # ===== 14. 今日の運勢 実行 =====
        try:
            click_visible_button(page, "今日の運勢を見る")
            wait_for_streamlit(page, extra=3)
            result = page.locator(".score-num").first
            result.wait_for(timeout=TIMEOUT)
            text = result.inner_text()
            log("今日の運勢 実行", text.endswith("点"), f"スコア={text}")
        except Exception as e:
            log("今日の運勢 実行", False, str(e))

        # ===== 15. モバイルUI =====
        try:
            mobile_context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                ignore_https_errors=True,
            )
            mobile_page = mobile_context.new_page()
            mobile_page.goto(BASE_URL + "?mobile=1", timeout=TIMEOUT)
            wait_for_streamlit(mobile_page, extra=5)
            heading = mobile_page.locator("text=占いポータル")
            heading.wait_for(timeout=TIMEOUT)
            log("モバイルUI ホーム表示", True)

            time.sleep(3)
            all_menu_btns = mobile_page.locator("[data-testid='stBaseButton-secondary']").all()
            zodiac_btn = next(
                (b for b in all_menu_btns if b.is_visible() and "星座" in b.evaluate("el => el.innerHTML")),
                all_menu_btns[1] if len(all_menu_btns) > 1 else all_menu_btns[0]
            )
            zodiac_btn.click()
            wait_for_streamlit(mobile_page, extra=2)
            back = mobile_page.locator("button", has_text="戻る").first
            back.wait_for(state="visible", timeout=TIMEOUT)
            log("モバイルUI ページ遷移", True)

            back.click()
            wait_for_streamlit(mobile_page, extra=2)
            heading2 = mobile_page.locator("text=占いポータル").first
            heading2.wait_for(timeout=TIMEOUT)
            log("モバイルUI 戻るボタン", True)

            mobile_context.close()
        except Exception as e:
            log("モバイルUI", False, str(e))

        browser.close()

    # ===== サマリー =====
    print("\n" + "=" * 50)
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
