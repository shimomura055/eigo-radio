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

## §2b 是正後再開(委任_02、2026-10-21)
- 是正: `ANNOTATION_FIX_01.md`(NUMのドット区切り数値列対応、`er053_b3_deterministic_producer_01.py:169`、commit 35c3c450f)。rules_sha256 旧525f2309…→新3b4b7fdf8dc6816cf8368b538c4b85485dba33ed2a114a8319b13a060050f723。出力不変証明: coffee run_fxpw_01 / mey run_mey_02 / paycheck run_pp_01 で旧版と新版の注記出力がバイト同一(rules_sha256除く)。API 0。
- 記事Aとの版差: 記事Aのtext(run_pp_01)は是正前の旧rules_sha(525f2309…)で完了済み。記事Aの注記内容は新旧同一(上記証明)。記事B(run_byus_01)の注記artifactは新sha(3b4b7fdf…)。
- 再開: `--stage all`(同一引数、console_text_02.txt)。Research/Ledger/B3は既存artifactを再利用(「既存Ledgerを再利用」「既存Selected Fact Briefを再利用」、再課金0、runner L97-103/L452-458)。producer通過(`producer=deterministic_v2 rules_sha=3b4b7fdf8dc6 facts=4`、LLM 0 call)。text再開 JST 12:59:32〜13:04:42(約5分、rc=0)。
- text CP(再開分):
  - Research試行1回(run_byus_01のみ)。regenerate writer使用0。Ledger: facts14、VERIFIED13/AMBIGUOUS1(F13、新規利用者105%増)/REJECTED0。B3 selected=F01,F03,F07,F14(全VERIFIED)。
  - Writer: W-1(gpt-6.1-sol)R0→R1→R2、symbol_qa findings 0、R2 rerun 0、echo 0、Std/Advともstructure/IOL(In one line)あり。
  - CP-B1: 本文は「運営会社が発表した」「The company says」の帰属を保持。10月19日の発表日は本文に出さず(B3が「提供開始日と同一とは断定しない」と指示)、「リリースした」とは書かず "announced the launch"。ただしIOLは "LINE Manga has launched byUs"(発表の要約表現。Fable判断対象)。
  - CP-B2: Character Chat(キャラチャット)とbyUsを区別、"The company says" 帰属付き。CP-B3: Official Story("official story")とファンストーリー("fan story")を区別。CP-B4: 「原作者に承認された作品・キャラのみ」+Help記載の正式契約(F03)を保持。無断利用と誤解させる表現なし。
  - CP-B5: 利用実績数値(F11/F12/F13)はB3で不採用のため本文に出ない。利用者反応・感想の創作なし(仮定の独白は「〜かもしれない」型の読者向け問いかけ)。
  - CP-B6(Angle): B3 storylineが「読者参加体験」を中心(F14: 「物語への参加」を提供範囲に限定)。本文は「読者席から物語作りの舞台へ」「読む人→作り手の顔」で候補Angleを採用(全LINEマンガ作品で使える/正史を書き換えられるとは書かず)。判定はFable。
  - CP-B7: 数値は「2作品・4キャラクター」のみ(F14、Ledger内)。発音「バイアス/bias」はF01 Ledger内。RF候補: Adv(b1b) 2件(s19 "you can continue an official story in the service"、s38 "Until now…"のみ可能と言える)/Std(a2) 4件(s10 "announced a new service"、s14 "make your own stories based on their works"、s23 official story、s31 "keep them private, or let someone else read them")。いずれも非Blocking、合否判定はFable。review_queue/post_en/manga_ai_chat_byus__run_byus_01/。

## §3 音声(委任_02、audio run `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/`)
- 実行: `er019_family_x_audio_production_runner_01.py --slug manga_ai_chat_byus --run run_byus_01 --level both --stage all --budget-jpy 70`(`TTS_EXECUTION_MODE=STANDARD`、backend既定speech_metadata_flash_lite、profile fx_20261017)。JST 13:05:39〜13:41、rc=0、約36分(うちb1b full_story_part3の既存retry cascade 3回NG後の600秒cooldown約10分)。
- 結果: Std(a2) 322.207秒 / Adv(b1b) 301.98秒、assemble status OK、clipping無し。style_profile_gate PASS(両level、blocked 0)、key_phrase_source_gate PASS(5/5)、M2-FALLBACK発生なし、Audio Validation全segment OK。Human Review/Lock=RESOLVEDのみ(blocking 0)。LR(Local Rewrite)発火0。PASS_WITH_WARNING(事後試聴リスト、非ブロッキング): Std 2件/Adv 3件。cumulative TTS attempts>1: Std comment_3(2)、Adv full_story_part1(3)・part3(3)。WARN: `a2_derived_from_advanced_sha_mismatch`(観測のみ、警告記録のみ)。
- Std 6%減速: 配線あり(`generate_a2_segment_with_slowdown`、Full Story 4 segmentで slowdown_applied=true、target 6.0%、actual 5.961〜5.98%)。
- 試聴ページ: `er019_byus_page_01.py`→`user_test/manga_ai_chat_byus_e2e_01/`(commit 78e780eaf)。URL=https://shimomura055.github.io/eigo-radio/user_test/manga_ai_chat_byus_e2e_01/index.html 。再生evidence=`pages_play_evidence_01.json`(audio 51本全再生OK、seek OK、http>=400なし、console error 0、通し尺 Std 322.21 / Adv 301.98秒)。

## §5 費用(出典: cost.json / audio runner累計 / raw_usage_log)
- text: 40.913円(Research 9.21、Ledger 7.455、B3 9.39[是正前の26.05を含む]、Writer w1_r0 8.262 / r1 2.039 / r2 2.305、Advanced 0.275、Standard 0.369、RF 計約1.58)。provider: openai 39.99 / gemini 0.923。是正後の再開分の追加はWriter以降のみ約14.86円。
- audio: 53.03円(openai 14.59、gemini 17.12、openai_asr 4.40、azure 16.92)。Std 28.78 / Adv 24.25。
- 本記事合計 93.94円(1生成セット総原価、目標70円に対し超過+23.94円。主因=audio 53.03が見積23〜30円の約2倍[Adv full_story_part1/3が各3回TTS+ASR、Azure等]、text 40.91はMEY 32.5より高い)。Guardrail 150円内。当日累計(daily_dev_cost_01、並行agent分含む)=275.17円/1,000円。

## §X 是正の記録
ANNOTATION_FIX_01.md参照。残置/撤去: 旧規則の撤去なし(NUMの量化子のみ変更)。SURF_RE等の他規則・find_all・閾値・fallback経路は無変更。
