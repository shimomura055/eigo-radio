# BERTIE_LEDGER_CANDIDATE_01 (委任_07、2026-10-23) Bertie の Ledger 登録候補(登録は実行していない。--apply禁止)

Status: CANDIDATE_PENDING_USER(人承認はUDR待ち。UDR起票はFable)。Ledger/コード/registry変更0。

## 1. 重要な発見: 承認CLIだけでは「Bertie」を登録できない
- `er103_pronunciation_approve_cli_01.py:24-31` `approve()` は **既存Ledger entryの更新専用**。surface(fold一致・`ledger_disabled`除外)に一致するentryが無いと `{"ok": False, "reason": "NO_MATCHING_LEDGER_ENTRY"}` を返す。さらに非revoke時は `--respelling` と `--approved-by` が必須(:32-34)。
- 現Ledger(`er006_output/pronunciation_ledger_01/ledger.json`、39 entry)に `bertie`/`vera`/`framton` は無い(委任_06で確認、今回も再確認)。Khaiteは既に cascade_unresolved_entity entry(1652efa9f4bdd7e8)が存在したため CLI で human_approved を付与できた(DECISION_LOG 2026-10-22 PNAP 委任_03)。
- 実行制約: 本セッションでは `--dry-run` 相当の実行がauto mode分類器に拒否された(CLIの既定はdry-runだが実行は見送り)。コード上の結果は確定的: `--surface Bertie` は `NO_MATCHING_LEDGER_ENTRY`(rc=2)。`--apply` は一切実行していない。
- 含意: 「綴り供給なし=ASR受理証拠のみ」の登録は、CLIでは不可能。CLIの `--respelling Bertie` を付けて human_approved にすると、B階層の「TTS入力へ綴り置換」(`tts_respelling="Bertie"`、同一綴りへの置換=実質no-opだが「供給適用一覧」に載る)になる。

## 2. 登録に必要なもの(Fable/ユーザーが選ぶ方式)
PNAP の証拠判定は `er103_proper_noun_alarm_policy_01.py:697-712` `ledger_surface_tokens()` が **`ledger_disabled` でない全entryのsurface語(fold)** を集めるだけ(human_approved・confidence・entity_typeは不問)。`proper_noun_evidence` は `t in ledger_surfaces` で `(True,"ledger")`(:176-177)。したがって必要なのは「`ledger_disabled`でない `bertie` surface entry が1件存在すること」のみ。
| 方式 | 内容 | 評価 |
|---|---|---|
| (a) `er006_pronunciation_ledger_01.upsert(LedgerKey("Bertie","person"), {...})` を1回実行(新規entry作成。TTS注入を避けるため `pronunciation_hint=""`、`tts_injection_disabled=True`推奨) | surface=Bertie / entity_type=person / canonical_spelling=Bertie / confidence=high / sources=[原作本文URL] / resolution_method="source_text_human_approved" | 推奨。hint空なので `get_hint_for_text`(:250-296、`pronunciation_hint`が真のentryのみ返す)の対象外=TTS注入0・ASR Phrase List供給0。`human_approved`は付けない(綴り供給なし)。ただしupsert直接呼出は「人承認登録」の操作手段として既存CLIに無い=Fable判断(新手段になるため、使うなら1回限りの運営者操作としてUDRに明記) |
| (b) (a)後に承認CLI `--surface Bertie --respelling Bertie --approved-by <ユーザー名> --apply` | human_approved=True・tts_respelling=Bertie・承認履歴を `er006_output/audio_retry_cascade_prod_01/pronunciation_approvals.jsonl` へ追記 | 承認履歴が残る点は良いが、「綴り置換Bertie→Bertie」は無意味な供給記録を作る。証拠としては(a)で十分 |

## 3. 登録入力(案)
- surface = `Bertie`(PNAP側は fold で `bertie`)/ entity_type = `person` / canonical_spelling = `Bertie` / 綴り供給なし(ASR受理証拠のみ)。
- 出典: 原作 Saki "The Open Window"(Project Gutenberg #269 `https://www.gutenberg.org/cache/epub/269/pg269.txt`)の歌詞 'Bertie, why do you bound?'(Vera語り+ラスト、本文抜粋 `er026_output/family_z_production_e2e_01/the_open_window/seed/primary_text_excerpt.md:29,49`)。
- Seed内の該当: `seed/seed.json:6`(seed_elements[2])・`:8`(seed_elements[4])・`:33`(`source_essentials.setups_and_payoffs[0].setup`)に歌詞として含まれる。`source_essentials.key_roles`(:37-)の人名リストには入っていない(Framton/Vera等のみ)。
- 発音の根拠: 英語人名 Bertie /ˈbɜːrti/。CMU収録(zipf 3.08、一般語でない)。ASRは同音近似語 `Birdie` に倒れる(Primary gpt-4o-mini-transcribe・Azureとも3回×2clip×2レベル全て Birdie)。

## 4. 登録後の挙動予測(根拠と未検証点を分ける)
- 確認済み(委任_06・API 0): `_noun_checks("bertie","birdie",...)` に `ledger_surfaces=['bertie']` を与えると `(None,'ledger',0.667)`=受理(類似度0.667)。
- **重要な未検証点(今回の追加発見)**: 既存のHR Lock済みclipは **`er109_hr_lock_rejudge_01.py`(API 0)では救えない**。今回実測(`--no-write`): 現状 `NOT_CANDIDATE` 2件(b1b)。in-memory で Bertie entryを足し `run_scope("Z")` 内で再評価しても `NG_BOTH/secondary_not_accepted` のまま。原因: 保存転写の再評価でPNAPを使うのは「元のasr_judgementが `PASS_WITH_PRONUNCIATION_ALARM`」の場合だけ(`er019_family_x_validation_inheritance_01.py:349-352`)。今回の2clipは元状態が NG_BOTH のため対象外。
- よって再開手順は **再生成**(API有料):
  1. ユーザー承認: Bertie Ledger entry登録(上記(a)、必要なら(b))。
  2. HR Lockの人承認 `er011_human_review_lock_01.approve_regenerate`(approved_by=user明示)をb1b/a2の `full_story_part1_c14`・`full_story_part3_c2` の計4 segmentへ。(この承認は「再生成してよい」の承認であり、Lock手解除ではない。Lockが残ったまま `--only-clips` を呼ぶと HUMAN_REVIEW_LOCKED で 0 API になる[er063:881-886 コメント])
  3. `er026_family_z_fiction_production_runner_01.py --story the_open_window --run run_sf_prod_01 --stages tts_b1b --only-clips full_story_part1_c14,full_story_part3_c2 --mode real --approved-budget-jpy <残額> --tts-execution-mode STANDARD`、同様に `--stages tts_a2`。(`er026...:2075` `--only-clips`)
  4. 生成時の cascade で PNAP(run scope Z内)が `ledger` 証拠により `Birdie` を受理しアラーム付き完成(PASS_WITH_PRONUNCIATION_ALARM)になる見込み。またはASRが正しく `Bertie` を聞き取れば通常PASS。**生成時adapter全体での受理は実run前に未検証**(`_noun_checks`単体のみ確認済み)。
  5. 続けて `--stages gate,assemble`(API 0)→ pages(別途)。
- 費用見込み: 今回実績 tts_a2 全39clip=約24.75円(Gemini TTS 52call/OpenAI ASR 67call/Azure 25call/Perplexity発音調査17call[401失敗])。1 clip・1 attempt あたり約0.4〜0.5円。再生成は 2clip×2レベル×1〜3 attempt ≒ **約2〜5円**(上限寄りでも<10円)。Phase 4音声段の累計は現時点61.95円/100円のため範囲内。
- 残リスク: `Birdie` 以外の別語で再び聞き取られた場合はPNAP受理外(再HR Lock)。その場合は(Ledger登録は有効なまま)CMU/類似度閾値の範囲を超えるため別途判断。

## 5. 同原作の他の名前(アラーム集計)
今回の脚本(r2/Std)に現れる人名は **Framton / Vera / Bertie のみ**(Nuttel=0・Sappleton=0・Ronnie=0。writer/r2.md・std.md をgrep)。したがって Nuttel/Sappleton/Ronnie が別語化する懸念は今回の版では発生しない(将来の別版で登場すれば別途)。
| 名前 | Adv(b1b) | Std(a2) | 備考 |
|---|---|---|---|
| Framton | 8 segment(アラーム付き完成、ASR frampton/crampton) | 8 segment(同) | アラーム受理(HR 0) |
| Vera | 11 clip全てASR一致 | PWW 1件: part1_c13 `Veera said more quietly.`(primary_pass+SECONDARY_CORROBORATED、`pass_with_warning_listening_list.json`) | 発音アラーム0 |
| Bertie | 2 clip STOPPED(Birdie) | 2 clip STOPPED(Birdie) | 本件 |
- 「状態9件/報告8件」不一致の9件目: **Bertieではない**。b1b `comment_3`(`Vera told Framton ... What does Framton see ...`)の `asr_judgement.pronunciation_alarm_records` に同一alarm_id(`pnal_4e182dba37180a61`)の `framton` が2件(本文中に2回出現)あり、集計(状態)は2件、報告(`pronunciation_alarms.json`は alarm_id 重複排除)は1件のため。実質は重複排除による表示差で、欠落ではない(a2 は8=8で警告なし)。
