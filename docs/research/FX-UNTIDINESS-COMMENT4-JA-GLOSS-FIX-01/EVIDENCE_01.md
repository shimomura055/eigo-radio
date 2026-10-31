# FX-UNTIDINESS-COMMENT4-JA-GLOSS-FIX-01 EVIDENCE_01(委任_01、2026-10-31、OPEN-634)

対象: Family X `family_x_untidiness_family_resource_01` Advanced(b1b)の公開End User版 Comment 4(`adv_19`、段落id `adv_19-s044`)の日本語訳。発見元=`docs/research/KP-N5-PHRASE-COVERAGE-AUDIT-01/AUDIT_01.md:143-144` J4。

## 1. 現状確認(是正前)
- 英文(`adv_19-s044`): "The story asks us to look at things left out with care, because they may have a purpose."(`user_test/family_x_untidiness_family_resource_01/enduser/data/article.json` adv parts[19])。
- 是正前の訳(`ja[0]`): 「物語は、省かれたものには何か意図があるかもしれないので、注意深く見るよう私たちに促しています。…」。本文(Full Story Part 3 `adv_18-s033`「working things left out」=承認済み原稿の「働く出しっぱなし」)の語義は「出しっぱなし(片づけられず出たままの物)」。**「省かれた」は語義不一致**。
- 訳の出自: `ja_source=generated`(承認済みJA原稿ではない)。End User生成時にLLM(gpt-6-luna)が新規生成する経路 `er135_enduser_page_01.py:839 generate_missing_translations` → `er135_enduser_translate_01.py:491 translate_part`(Prompt雛形・数値検査・構造検査・対訳照合・`ja_generated.json`キャッシュ)。生成日時 2026-10-30T17:05:34(`<run>/enduser_sync_cache/ja_generated.json`、cache鍵=英語段落sha 691113f5…)。
- **JA音声は無い**: Comment 4の音声`audio/adv_19.mp3`(13.0秒)は英語のみ(Charon)。日本語訳は画面表示のみで読み上げられない。devページ(`index.html`)にも日本語訳なし。よって**TTS再生成は不要**(音声不一致は発生しない)。
- ハイライト連動データ依存: `ja_align`(`how=gen`、1文=1群、オフセットは訳連結時に確定、`er135_enduser_translate_01.py` build_ja_fields)。sync_*.json(音声の時刻)は英語音声から作るため訳に依存しない。

## 2. 原因
- `translate_part`の文脈(Prompt「文脈(訳さない。同じパートの他の文)」)は**同一パート内の訳対象外の文**だけ(`er135_enduser_translate_01.py:521`)。Comment 4は1段落3文が全て訳対象で、**文脈が空**。"things left out"単体は「省かれたもの/出しっぱなしの物」の両義で、直前パートの語義が渡らず「省かれた」と訳された。
- 対訳照合(verify)の判定対象は意味の反転・数値・固有名・情報の欠落/追加のみ(`VERIFY_HEAD` :56)で、語義違い(誤訳)は不合格にならない。決定論検査(構造・数値)にも該当しない。= 既存Gateをすり抜けた語義ミス。
- 同系統の潜在リスク(未実証): Preview/Comment/In One Lineの生成訳は全て「文脈なし(または同一パートのみ)」で生成される。

## 3. 是正(経路と差分)
- 経路=**既存の `er135_enduser_translate_01.translate_part` を adv_19 に限定して再実行**(`tools/retranslate_part_01.py`)。雛形・検査・対訳照合・cache保存は既存どおり。追加したのは (a) 文脈欄に直前part(Full Story Part 3、`adv_18`)の英文11文 (b) 既存の「前回の訳への指摘」枠に1番(`things left out`)の語義注記(「片づけられず出したまま・置きっぱなしの物。『省かれた』と訳さない」+前回の訳)の2点のみ。**Prompt雛形(PROMPT_TEMPLATE_SHA256 2da82c87…)は不変**。手打ちの直接編集はしていない。
- 旧entryは `ev01/retranslate/old_entry.json` に保存、LLM入出力は `ev01/retranslate/llm_log.json`、結果は `result.json`。
- LLM呼出: translate 1 + verify 1(いずれも初回合格、retry 0)。費用 ¥0.0461(translate ¥0.0302 + verify ¥0.0159)。stop_scope_check rc=0(開始時・各有料前)。
- 是正後の訳(`ja[0]`、3文): 「この話は、出しっぱなしになっている物にも目的があるかもしれないので、注意深く見るよう私たちに促しています。同時に、その研究ではサプリメントがリマインダーとして役立つかどうかは検証していません。最後のまとめを聞きましょう。」
  - 注: 段落単位のfail-closed生成のため、s045・s046の訳も同時に再生成された(「…機能したか」→「…役立つか」[s045の言い回し]。意味は同等と対訳照合でok)。
- 再produce: 既存の正式手順 `er135_enduser_page_01.py produce`(`hook_run`、asset rev01-h、cache再利用=translate/verify API 0、cache_hits 7)。`ev01/enduser_produce.log`・`enduser_page_result.json`。
- 差分Gate `tools/ech02_diff_gate_01.py`: ok、NG 0、変更=`enduser/data/article.json`・`enduser/build_info.json`のみ。article.jsonの値差分は adv parts[19] の `ja[0]` と `ja_align`のオフセット(47→53, 94→96, 108→110)のみ。他part・英文・承認済み訳・sync_*.json・index/app.js/style.css・音声は無変更(`ev01/ech02_diff_gate.log`)。build_infoの変化は article.json sha・`generated_translation.parts.adv.adv_19.ja_sha256`・`ja_align.input_sha256.adv.adv_19`・syncの`source_sha256`(所要時間を含むためrun毎に変わる)・asr/build wall時間のみ。

## 4. 検証
- ローカル(Playwright PC+mobile模擬): 268チェック NG 0(`ev01/enduser_page_result_browser.json`)。
- 公開(commit 8fa6d811e をpush後、Pages反映を確認): `enduser/index.html`・`?lv=adv`・`data/article.json`・`build_info.json`・`audio/adv_19.mp3` すべて HTTP 200。
  - 公開ページのComment 4表示(Playwright PC/mobile、`ev01/live_dom_check.json`): 英文3文+「日本語訳」欄に新訳が表示、旧訳「省かれた」は0、console error 0。
  - 公開 verify-only(PC+mobile模擬、ハイライト連動・既存機能含む): TOTAL 268 NG 0(`ev01/live_verify_only.json/.log`)。F1/F2既知欠陥(別件)は対象外。

## 5. 同種の不一致の有無(同記事)
- `left out/leave out/leaving out/省かれ` を article.json 全体(Std/Adv、vocab、grammar、全part)で走査: 英文の該当は std_19(「left out that are still doing a job」)・adv_05(Preview)・adv_18(Full Story Part 3「working things left out」)・adv_19の4か所。訳は std_19/adv_18=承認済みJA原稿(「働く出しっぱなし」)、adv_05=生成訳「置きっぱなしになっている物」で**いずれも語義一致**。不一致は adv_19 のみだった。
- 生成訳7part(std_21・adv_05/13/15/17/19/20)の全訳文を英文と目視照合: adv_19以外に語義ミスなし(全文は `ev01/` ではなくarticle.json参照)。
- `省かれ`を含む日本語訳は是正前のadv_19のみ(Std/Adv全part)。

## 6. 範囲外・残件
- 訳生成Promptの一般的変更(文脈として直前partの英文を渡す等)はしていない(JA-GLOSS-NUANCE-01の判断事項)。→ 再発リスクの記録: 同記事を **cacheなしで再produceすると、新規生成訳が再び「省かれた」になりうる**。**mainツリーの未追跡run dir cache(`er019_output/family_x_audio_production_wiring_01/untidiness_family_resource__run_fx4_01/enduser_sync_cache/ja_generated.json`)は旧訳のまま**(読み取り専用方針のため未編集)。是正済みcacheの写し=`ev01/ja_generated_corrected_01.json`(同pathへ置換すれば再produceで新訳が再利用される)。
- 他記事の修正・学習項目glossの変更はしていない。
- 作業環境: C:空き僅少のためsparse worktreeを使用(`git add`は自分のfileのみ)。
