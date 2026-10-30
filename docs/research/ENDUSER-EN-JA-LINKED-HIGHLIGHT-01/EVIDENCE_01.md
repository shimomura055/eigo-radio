# ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_02 EVIDENCE(2026-10-30)

対象=X/Y story部(訳表示あり)の英語文<->日本語訳 連動ハイライト。asset=rev01-f(DEV app.jsは不変、`derive_assets_01.py` EDITS J19-J25/C5)。Z=訳なしのため対象外(コード経路のみ、ja_align applicable=false)。

## 実装(file:line)
- `er135_enduser_align_01.py`(新規): split_ja 89 / numbers_ok 175 / EmbedStore 213 / _dp 282 / _Para 329 / align_paragraph 417 / align_part 488 / build_article_align 534 / check_part_align 582 / verify_article_align 648。offsetはUTF-16 code unit、訳文は無改変、埋め込み=text-embedding-3-large 1024次元・sha256キャッシュ。失敗=全null+degraded(M5)、page_verifyはAPI 0(キャッシュ欠落は不合格、M3)。
- `er135_enduser_page_01.py`: FROZEN_ASSET_DIRS 45 / build_enduser_data 804(align 860) / validate_output Y 1:1 assert 1039 / build_enduser 1176 / verify_consistency 1212(ja_align再計算 ~1257)。
- `er135_enduser_page_verify_01.py`: expect_maps 382 / linked_checks 419(call 350)。
- `enduser_page_assets/rev01-f/app.js`: jgEls 14 / jaHtml 41 / render hook 131-133 / jaLight 243 / gapGroup 250(M9) / highlight 258 / tick 286。rev01-eは凍結残置(藪の中=FROZEN)。

## 精度(ゴールド=原文を読んで人手作成、アルゴリズム出力を見ずに作成)
| 集合 | 段落/EN文 | emit群 | 誤対応 | 合成ずらし受理 | 文数一致modeの誤ペア受理 | coverage |
|---|---|---|---|---|---|---|
| 調整用3記事(moon/fee/sur) | 50/265 | 168 | 0 | 0/336 | 0/67 | 71.3%(Std 61.6/Adv 84.2) |
| 未見(pp+mg+ig) | 56/223 | 171 | 0 | 0/282 | 0/79 | 85.2% |
| 完全未見ig | 22/76 | 60 | 0 | 0/94 | 0/33 | 88.2% |
段落取り違え(別段落JAと組合せ): 調整用 1/368、未見 0/476。
開示: (1)igはEN側veto(-0.10)導入時に1/94受理が見つかり、そのパラメータに限りigを調整に用いた(以後ig準未見)。(2)文数一致mode分析にpp/mgを使用。(3)ゴールドは同一作成者。別Agentによる二重確認は未実施(Agent tool無し)。`gold/GOLD_READABLE_01.txt`を別Workerへ委任可能。(4)X新規記事での未見検証は、fx4の4記事がscaffold段階で不可。pp/mg/ig(既存X記事)で代替。
PARAMS最終値は`er135_enduser_align_01.py` PARAMS(lam2.0/tau0.50/tau_para0.55/tau_floor0.40/EN側veto-0.10 ほか)。

## 再produce(既公開4dir、API 0、埋め込みはゴールドキャッシュ再利用=費用0円)
| dir | Std coverage | Adv coverage | degraded | page_verify | diff Gate |
|---|---|---|---|---|---|
| X月 | 56.5%(26/46) | 80.0%(28/35) | なし | 222 NG0 | OK |
| Y再配達 | 56.9%(29/51) | 78.4%(29/37) | なし | 218 NG0 | OK |
| Y姓 | 70.4%(38/54) | 92.9%(39/42) | なし | 226 NG0(正式hook `er121 --stages pages,page_verify`でも226/0) | OK |
| Z melos | N/A | N/A | applicable=false | 174 NG0 | OK |
Std 85%目標は未達(安全側null優先)。null理由の内訳はbuild_info.json ja_align.coverage.reasons。M8(LLM判定)は未実装、後続候補。
diff Gate(`tools/ejh02_diff_gate_01.py`、git HEAD比): ja_align・build_info(asset_build/assets/cost/files/ja_align)以外の差分0(dev index.html・sync_*.json・音声不変)。
テスト: er135 align 44 + page + hook = 177 PASS。
注: 5 Playwright並列時にX月でG検査2件の競合flake(単独再実行222/0)。最終は全て直列/少数並列で0 NG。

## 可視性(残余リスク)と実測
訳ブロックは英文partの下にある。lit時にJAが画面内に見えた割合(PC/mobile同傾向): X月Adv 0/17-18(0%)、Y再配達 6/14-9/16(約40-56%)、Y姓 9/15-11/15(60-73%)。X月Stdのサンプルpartは連動null群のみ(lit無し)。スクリーンショット=`evidence_02/shots/`(x_moon pc/mobile adv、y_fee pc/mobile std)。自動scrollは追加していない(UI仕様変更=判断候補)。
結果JSON=`evidence_02/*_result.json`。
