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
