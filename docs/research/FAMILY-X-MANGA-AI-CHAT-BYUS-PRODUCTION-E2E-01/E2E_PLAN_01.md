# FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 E2E_PLAN_01(委任_01、2026-10-21)

性質: 正式Production経路の記事生成(text+audio)。新仕様探索ではない。記事B(slug=manga_ai_chat_byus、run=run_byus_01)。並行: 記事A(paycheck_personality)・Family Z Voice Trial。Detective Pattern A/B/Cは不採用・適用なし。

## §0 受入条件(CP)の事前固定(実走前。以後変更しない)
- CP-B1(発表と動作の区別): 本文(Std/Adv/IOL/Key Phrases/Std日本語Support)で、2026-10-19発表内容(予定・提供開始・対象作品等)と「実際に確認できた動作」を混同していない。帰属(LINEマンガ/運営会社発表、ITmedia報道)が保たれている。
- CP-B2(byUs≠キャラチャット): 「byUs」と既存「キャラチャット」を混同・同一視していない(両方が本文に出る場合は区別が明示。片方のみでも誤帰属なし)。
- CP-B3(Official Story/ファンストーリー): 両者の違いがLedgerにあれば本文で混同していない。
- CP-B4(原作者承認作品): 「原作者が承認した作品を対象とする」条件がLedgerに登録され、本文で歪められていない(無断利用と誤解させる表現なし)。
- CP-B5(公表実績と独立確認): サービス提供者が公表した利用実績(数値)は「〜が公表/発表」の帰属付きで、独立確認事実と区別。利用者の反応・感想の創作なし。
- CP-B6(Angle観測): B3が選んだAngleと「読む人→参加する人」候補との関係を記録(採用/部分/不採用)。合否はFable。不採用でも再生成理由にしない。
- CP-B7(Ledger外事実・帰属・RF): 本文の数値・固有名詞・因果はLedger内かつ帰属保持。RF候補の件数・内容を記録(合否はFable)。
- Research再試行条件: 発表日/対象作品条件(原作者承認)/提供状況の基本FactがLedgerに無い、またはB3採用FactがbyUsの発表内容を含まない場合に限り、同一条件で再試行(最大2回: run_byus_02/03)。語数・文体・Angle理由の再試行禁止。
- 許可regeneration: CP-B1/B2/B4/B5違反をSonnet CPで検出した場合のみ `--stage writer --regenerate-stage writer`(+advanced/standard)を1回だけ。2回目はSTOP。手動Fact挿入・Ledger/B3手編集・storyline_b3再抽選・HR/Lock/BLOCK迂回は禁止。
- 費用Guardrail: JPY150(本記事新規支出合算)。次stage前に「既使用+次stage見積」が150超見込みならそのstageを開始せずSTOP。runner --budget-jpy: text 120 / audio 70。
- Std 6%減速: Family X音声runner/assembleのGrepで有無確認。無ければ事実のみ記録し追加しない。

## §1 開始条件(S0、2026-10-21)
- 当日既使用: `daily_dev_cost_01.py --date 2026-10-21` adopted_jpy=90.54(並行agent分含む)。
- 出力dir `er019_output/manga_ai_chat_byus/` 非存在を確認。
- runner引数実在: entertainment `--theme --slug --out-dir --source-note --run-label --budget-jpy --stage --regenerate-stage --stop-after`、audio `--slug --run --level --stage --budget-jpy --tts-backend --style-profile`を`--help`で確認。
- 作業前`git status --porcelain`: 1137行(既存他run差分、明示addのみ)。branch=work/post-merge-01。
- T-0: 委任文 `docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_01.md`(19842 bytes、12055 chars)。check=FAIL(見出し名不一致の既知偽陽性)。ユーザー原文 `..._FAMILY-X-TWO-ARTICLES-PARALLEL-PRODUCTION-E2E_USER.md` を新規保存(本文2586字、sha256[本文のみ]=07f85daa4d877f58d831ddc59ea57ed21421cccf207d012e5952b0fd21bf26cf)。

## §2 試行1記録(run_byus_01、2026-10-21 JST 12:40:51〜12:45:07、約4分)
- Research: gpt-6-luna、facts=14、web_search_calls=5。Ledger: VERIFIED 13 / AMBIGUOUS 1 / REJECTED 0(kept 14)。
- B3(gpt-6.1-sol、attempts 1、validation_errors 0): selected_fact_ids=[F01, F03, F07, F14]。selected_storyline=「LINEマンガが原作者承認の作品を使う「byUs」のリリースを発表し、会話に加えて物語を創作できる点で既存の「キャラチャット」と異なる読者参加体験を、まず2作品・4キャラクターで提供する。」(Angle観測CP-B6: 「読む人→参加する人」と実質同方向=採用寄り、合否はFable)。基本Fact(発表日/原作者承認/提供状況)はLedger内に存在(再試行条件に非該当)。
- **rc=1(STOP)**: runner L466 `run_annotation_producer(out_dir)`(storyline_b3確定直後、LLM/API呼出なしの決定論producer、`er053_b3_deterministic_producer_01.py:890`)が `[STOP] ANNOTATION_PRODUCER_FAILED: internal check b_numbers: ["extracted number '26.10' (F14) has no mark in the annotated text", "extracted number '10以上' (F14) has no mark ..."]; e_sidecar: ["sidecar number '26.10' has no marked occurrence", "...'10以上'..."]`。Writer以降は未実行。
- 原因観測: 採用Fact F14のconditions(ledger L90)に「アプリバージョン26.10.10以上」が含まれる(F09 L49/L51/L52にも同じ。F09は未採用)。`extract_surfaces`(SURF_RE、L220-226/L375)にドット区切りバージョン番号のパターンが無く、`NUM_C+UNIT+HEDGE_POST`が「26.10」と「10以上」へ2分割して抽出する。一方、マーキング側`find_all`(L248-269)は「数字で終わる表記の直後が'.'+数字」なら出現と認めない(5.5の中の5を除く規則)ため「26.10」(直後'.10')を注記できず、「10以上」(直前'.')も同様に不可。抽出器と注記器の整合不良(version番号という入力型の未対応)。LLM非依存の決定論エラーで、同一Ledger/B3では再実行しても再現する。
- 費用: text 約26.05(Research+Ledger 16.66、B3 9.39、raw_usage_log由来、cost.json未生成)。当日累計(daily_dev_cost_01)=158.87。
- 状態: HR/Lock/BLOCK迂回なし、再実行なし、手編集なし。
