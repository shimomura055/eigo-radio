MARKER: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01 (2026-10-24, Fable→sonnet-worker)

# 管理ID: ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01(OPEN-482 残存2件の原因究明→対策設計→合成検証セット→replay基盤。設計まで。実装はOpus必須レビュー後の委任_02)
# ユーザー指示(2026-10-24、原文は `docs/pm/delegation_log/2026-10-24_FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01_USER_02.md` §1-②〜§5。別agentが同時刻に保存中。未保存なら本委任の末尾§Zを参照): OPEN-482の2件を作品承認と独立した品質改善として**両方とも解決**し、既存承認仕様の不具合修正として解決可能ならX/Z双方のProduction Wiring+runtime evidenceまで完了する。例外登録ではなく、時刻・年号・通常数値を含む既存判定構造の根本原因を解消。同音救済・Primary/Secondary ASR・数値正規化・最終Gateと整合。正常音声を誤NGにせず異常音声を誤PASSにしない。方式は固定しない(最も簡潔で保守性の高い方法)。不要なTTSを避け既存音声・ASR結果・合成テストを優先。品質基準は独断で変更しない。

## 対象2件(OPEN-482残存)
 (1) 純語形 `ten thirty`(原稿) vs ASR `10:30` が EQUAL にならない(UNKNOWN=NG側)。原因候補: `er021_en_asr_semantic_equivalence_production_01.py::_tier1_atoms` / `_parse_bare_number_run` が `ten thirty` を年ペア読みで number 1030 にし、ASR側は time atom 1030 → kind不一致。
 (2) 純語形 `ten thirty` vs `1030`(桁連結の数値) が EQUAL になる既存の穴(年号読みの経路で両方 number 1030 になるため)。
 既往: 第1層 `er006_preprod_hardening_01_validation.py::_convert_cardinal_words`(commit b5138e452)、第2層 `er078_asr_value_guard_01.py::_guard_en` 時刻分岐(commit e0eb13ab4)、影響分析 `docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/OPEN_482_IMPACT_01.md`・`OPEN_482_IMPACT_02.md`、replay/合成script(同フォルダ `replay482.py`/`pairs482.py`/`neg482.py`/`cand482.py`)。同じ問題への3回目の修正になるため、**実装前にOpus必須レビュー(条件A/B)**を入れる。

## 作業(API 0円。コード変更はDEV/scratch内の検証scriptのみ。Production code変更0)
 A. **判定構造の棚卸し** `docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/STRUCTURE_01.md`: 原稿→TTS入力(数字化)→ASR(Primary/Secondary)→一次分類(er006正規化)→統一Judge(er078 unified judge)→Tier1 atoms(er021)→value_guard最終Gate(er078)→同音救済(er109 orthographic/UKUS)→HR Lock、の経路で**数値・時刻・年号がどこでどう表現(文字列/atom/kind)に変換されるか**を関数・行番号付きで図示。X/Zで経路差があれば明記。retry/fallback/regeneration/resume時に同じ判定が再実行される箇所も確認。
 B. **根本原因** `ROOT_CAUSE_01.md`: (1)(2)それぞれの発生機序を、実際の入力で関数を呼んで再現(scratchで実行、出力を貼る)。「隣接数詞語の読み(年号ペア/時刻/合算/桁連結)を文脈なしに1通りに決めている」構造問題かどうかを判定。原稿側がTTS入力で数字化される経路(c8では `At 10 thirty`)と純語形のまま判定に届く経路の両方があるか、どの経路で(1)が現実に発生し得るかを事実で示す。
 C. **対策設計** `DESIGN_01.md`: 方式候補を2〜3案(例: a.数詞語列の多義展開=1つの語列から{時刻1030(time), 年1030(year), 数10+30, 合算40}の候補集合を作り、相手側atomと**いずれかの読みが同kindで一致すればEQUAL、桁連結数値とは一致させない**/ b.時刻文脈(at/around/by/until/am/pm/o'clock等)で時刻kindを優先/ c.その他)。各案について: 変更箇所と行数見込み、(1)(2)の解消可否、年号(`nineteen ninety nine`/`twenty twenty six`)・金額・通常数値・`twenty one`・`one hundred thirty`・`two thirty`(2:30/230)との衝突、同音救済・Secondary ASR・最終Gateとの整合、誤PASSリスク(異常音声を通さないか)、保守性。**推奨案1つと理由**。例外登録・特定語の個別救済は不可。
 D. **検証セット** `TEST_MATRIX_01.md` + scratch実行結果: 正常系(同一時刻の表記ゆれ: `ten thirty`↔`10:30`/`ten-thirty`/`10 30`/`half past ten`は別語なので非対象と明記/`ten thirty am`↔`10:30 am`/`two fifteen`↔`2:15`)、異常系(`ten thirty`↔`1030`/`10:13`/`10:03`/`11:30`/`40`/`forty`/`ten`/`30`/`10:30 pm` vs `am`)、境界(`twenty twenty`=2020 vs 20:20、`nineteen ninety`↔`1990`、`two thirty`↔`230` 金額/数量文脈、`one thirty`↔`1:30`/`130`、`twelve o'clock`、`twenty one`↔`21`、`ten thirty-five`↔`10:35`、桁連結 `1030` が原稿にある場合の扱い)。各ケースに期待値(EQUAL/非EQUAL)と**根拠となる既存仕様**(同音救済・数値正規化の承認済みルール)を付け、現行コードでの実測結果を並べる(修正前ベースライン)。
 E. **replay基盤**: 既存 `replay482.py`/`pairs482.py` を本管理IDのフォルダへ複製・一般化し、全リポジトリの既存canon/ASR対(前回5,246対)を修正前後で比較できる状態にする(実行は修正後の委任_02。今回はベースライン実行のみ、結果json保存)。
 F. **Production反映計画**: X/Z双方への適用経路(共通moduleなら1箇所で両方に効くことの確認)、runtime evidence の取り方(既存音声・ASR結果の再判定を正式経路の関数で行う方法を優先。新規TTSが不可欠な場合は最小[X 1clip・Z 1clip ≤3円]の理由付き)、flag要否(不具合修正は既定ON・flag不要の方針。ただし既存のX/Z scope guard(`er109_xz_scope_01`)との関係を確認)。
 G. **Opusレビュー依頼文** `OPUS_REVIEW_REQUEST_01.md`: 論点を絞る(多義展開の誤PASSリスク、年号との衝突、桁連結の扱い、Secondary ASR・同音救済との整合、replay基準、X/Z適用)。Fableが起動する。
 H. 記録: `docs/pm/ACTIVE_TASK.md` に本管理IDの行を新設(委任_01、API 0、Production変更0)。**OPEN_ITEMS/DECISION_LOG/CURRENT_SPECは本委任では編集しない**(別agentがClosoutで同時編集中。SSOTは委任_02でまとめて更新)。委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_ASR-TIME-NUMERAL-EQUIVALENCE-01_委任_01.md`(先頭MARKER一致、0始まり)。commit(`docs/research/ASR-TIME-NUMERAL-EQUIVALENCE-01/` と delegation_log のみ、`git commit --only -- <paths>`、`git add -A/-u/-f`禁止、secret grep 0件)→`git push origin HEAD:main`。
 I. 報告 `docs/pm/RESULT_PACKET_ATN1.md`: 原因(1)(2)の機序、推奨案と理由、ベースライン実測(誤NG/誤PASSの現状件数)、Production反映計画、4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去)、判定整合行、所要時間。

## §Z ユーザー指示(OPEN-482該当部、逐語)
### ② OPEN-482 — 未解決の時刻表現検査不具合2件
**作品承認とは独立した品質改善タスクとして、2件とも解決すること。**
対象：
1. `ten thirty` と `10:30` が同じ時刻を表すにもかかわらず、NGになる問題。
2. `ten thirty` と `1030` の桁連結が、誤って一致扱いになる既存の問題。
いずれもFamily X/Z共通の音声検査品質に関係する。
## 2. OPEN-482の対応方針
原因究明 → 対策立案 → Trial検証 → 結果評価 → 必要な修正・再検証を、Fable／Claude側で自律的に実施すること。
単に今回の2表現を例外登録するのではなく、時刻・年号・通常の数値表現を含む既存の判定構造を確認し、問題の根本原因を解消する。
特に以下を満たすこと。
- 同じ時刻を表す表現は、既存の音声判定方針と整合する形で正しく救済する。
- 実際には異なる値や発音を、不適切に一致扱いしない。
- 年号や通常の数値表現との衝突を防ぐ。
- 既存の同音救済仕様、Primary／Secondary ASR、数値正規化、最終品質Gateとの整合を維持する。
- Family X/Zの正常な音声を誤NGにせず、異常な音声を誤PASSにしない。
具体的な実装方式は固定しない。既存機構を最大限活用し、最も簡潔で保守性の高い解決方法を選択すること。
## 3. 自律検証・STOP条件
- 既存仕様の不具合修正と検証は、承認済み作業範囲・開発予算内で自律的に進める。
- Trial回数だけを理由に停止しない。
- 改善が見込めない方法の反復は避け、原因やアプローチを見直す。
- 独立した調査・検証は可能な範囲で並列化し、完成までの時間を最小化する。
- 不要なTTS再生成を避け、既存の音声・ASR結果・合成テストを優先活用する。
- 品質基準を独断で変更しない。
- 新仕様の採用が必要になった場合、重大な品質リスク、承認範囲・予算超過、解決不能なblockerが発生した場合はSTOPしてユーザー判断を求める。
## 4. Production反映と受入条件
既存承認仕様の不具合修正として解決可能な場合は、Family X/Z双方のProduction Wiringまで完了させること。
完了条件：
1. OPEN-482の2件について、原因と解決内容を説明できる。
2. 正常系・異常系・境界ケースのTrial／回帰テストがPASS。
3. 既存の時刻・年号・数値表現について、誤PASS／誤NGの新規発生がない。
4. 正式Production経路に反映され、retry／fallback／regeneration／resumeとも整合。
5. 正式経路での発火・判定について、適切なruntime evidenceを取得。
6. Family X/Z双方の適用状況を確認。
7. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新し、Git反映まで完了。
8. 残存課題や未確認事項を隠さず報告する。
DEV／Trialのみの成功や、コード実装のみでPRODUCTION_WIREDと判断しないこと。