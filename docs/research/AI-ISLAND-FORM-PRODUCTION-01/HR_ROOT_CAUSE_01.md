# HR_ROOT_CAUSE_01(AI-ISLAND-FORM-PRODUCTION-01 委任_05、read-only調査、API 0・JPY0、2026-10-27)

原文: `docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_04.md` §4。対象run=`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`(a2=Standard / b1b=Advanced)、segment=`full_story_part1_k2`(Role=FULL_STORY)。根拠は全て保存データ(`<run>/{a2,b1b}/audit/tts_generation_results.json`、`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl` L7490-7502、`<run>/audit/hr_packet_data_01.json`)。

## 結論(1段落)
本文は無変更。変更されたのは**音声に読ませた文だけ**で、第1部2段落目の主語「The AIs sent to the island…」の `AIs` を、承認済みLocal Rewrite(局所言い換え)がStd=`AI agents`/Adv=`AI systems`に置換した。理由は、Std/Adv とも3回(標準2+fallback1)の生成で、音声認識(OpenAI・Azure)が `AIs` を `AI` と書き起こし続けたこと(Stdは6%減速後の再検証)。言い換え音声は検証を通過したが、**M3 Style Gate の `LOCAL_REWRITE_RECOVERY` は承認済み安全規則で人の承認(`record_human_approval`)以外に解除手段がない**ため、HRとして提示された。音声の品質不良ではない。

## 1. 元原稿
- Std: "The AIs sent to the island had no set tasks or rewards. But their starting settings led them to be curious, explore, and learn. They had no homework, but they were ready to explore."
- Adv: "The AIs sent to the island had no specific tasks or rewards. But their initial settings guided them to be curious, explore, and learn. They had no homework, but they were in exploration mode."(article.mdでは `to “be curious, explore, and learn.”` と引用符あり。TTS入力では引用符除去)
- 場所: Full Story 第1部 `full_story_part1_k2`(2段落目)、Role=FULL_STORY、Level=a2/b1b。Std `canonical_text`=Adv同様に上記(`tts_generation_results.json` segments.full_story_part1_k2.canonical_text)。
- ユーザー確認済み本文との一致: `er019_output/ai_island_temple/run_ai_01/{a2,b1b}/article.md` のLF正規化SHA-256 = `confirmed_selection.json` の `article.text_sha256`(a2 `76f80f62…2376599`、b1b `00f14092…ca324`)に**一致**。rawバイトSHAは `scaffold_article_sha256.json`(a2 `90c66293…`、b1b `a2951b9b…`)= `ARTICLE_EN_{STD,ADV}_01.md` と一致。→ 本文は確認済み版のまま。
- ユーザーが「Advanced末尾に `AI agents` はあるが `AI systems` は無い」と見た件: Adv article.md 20行目「AI agents with island experience did better…」は別の文の本文。`AI systems` は**本文のどこにも無く、音声用の言い換え語**(本文Std/Advとも k2 段落は「AIs」)。

## 2. 置換・書換え
- 本文(article.md・ページ表示): **変更なし**。
- 音声に読ませた文のみ変更(`canonical_text_before_local_rewrite` → `text`):
  - Std Before: "The **AIs** sent to the island had no set tasks or rewards. …" / After: "The **AI agents** sent to the island had no set tasks or rewards. …"(候補1採用)
  - Adv Before: "The **AIs** sent to the island had no specific tasks or rewards. …" / After: "The **AI systems** sent to the island had no specific tasks or rewards. …"(候補2採用)
- 発動工程: TTS retry 3回(標準2+fallback1)後の `er020_tts_retry_local_rewrite_01` Local Rewrite(Luna `gpt-6-luna`、5候補→7 Gate+Natural English QA→採用)。承認根拠: `CURRENT_SPEC.md:2213`(2026-09-26 `APPROVED_FOR_PRODUCTION`)、`CURRENT_SPEC.md:2923`(2026-10-19ユーザー決定、発火条件・書換え後の実送信文を正解とする再検証)。

## 3. TTS retry / Local Rewrite 発動状況
| | Std(a2) | Adv(b1b) |
|---|---|---|
| 標準 | 2回(各回 生成直後は二次ASR/正規化で通過 → 6%減速後再検証が不一致) | 2回(一次・二次とも `AI`) |
| fallback(minimal) | 1回(slot3、`cooldown` 180秒 12:05:05-12:08:05) | 1回(`minimal_fallback`、cooldown 180秒 12:13:19-12:16:19) |
| Local Rewrite | 1回(slot4、候補1採用、再TTS+減速+減速後再検証PASS_WITH_WARNING) | 1回(slot4、候補2採用、一次PASS) |
| `tts_generations_used` | 4 | 4相当(標準2+fallback1+LR1。b1bのキー無し) |
| `slowdown_attempts_log` | attempt1-3 すべて `ASR_VALIDATION_UNCERTAIN`(`post_slowdown_ng=true`) | 減速なし |

## 4. ASR判定
- Std 生成直後(減速前): 試行1 OpenAI "The AI sent…"→Azure "The **AIS** sent…" で `SECONDARY_ASR_CORROBORATED_MATCH`、**試行2 OpenAI "The AIs sent…" `NORMALIZED_MATCH` PASS(TTSが「AIs」を発音できていた)**、試行3 同試行1。
- Std 6%減速後: OpenAI 3回とも "The **AI** sent…"、Azure も3回とも "The AI sent…"(telemetry L7493/L7496/L7501 `corroborated_by: []`)→ Tier3救済不成立 → `ASR_VALIDATION_UNCERTAIN`。
- Adv(減速なし): 試行1-3 すべて OpenAI "The AI sent…" / Azure "The AI sent…"(`NG_BOTH` `secondary_not_accepted`)。
- 採用音声: Std=OpenAI "The AI agents sent … **awards** …"(`TRUE_CONTENT_MISMATCH`)→Azure "…rewards…" `NORMALIZED_MATCH` 救済(`PASS_WITH_WARNING secondary_confirmed`)。Adv=OpenAI "The AI systems sent … initial **setting** guided…" `SECONDARY_ASR_CORROBORATED_MATCH`(`LR_REWRITTEN`警告)。
- 承認済み対策の適用有無と非適用理由:
  - Tier3 corroboration(`CURRENT_SPEC.md:2239`): 評価済み、Azureが `AI` と聞くため不成立。
  - 固有名詞アラーム受理(PNAP、`CURRENT_SPEC.md:3095-3097`): 評価済み `pronunciation_alarm_eval: {accepted:false, reason:"NO_PROPER_NOUN_EVIDENCE", token:"ais"}` → AIsは固有名詞でない。
  - er109 同音異表記: 「AIs/AI」は同音異表記でなく対象外。
  - 発音台帳/Phrase List: `ledger.json` 43件に `AI`/`AIs` 無し、`phrase_list_size=0`、`en_pronunciation_resolver_info.hints_applied=false`、`pronunciation_alarms.json` count=0/supply_applied=[]。台帳は固有名詞(Perplexity調査)用で、略語複数形を原稿不変のまま扱う承認済み手段は現行仕様に無い。
- 同一記事の他の `AIs`(13 AIs with…、the AIs could…、the AIs better、the AIs that)は ASR が `AIs` と認識して PASS(a2 part2_k2、b1b comment_2/3/4・part2_k2)。失敗は「AIs **s**ent」(複数形s + 次語s)の1箇所のみ。**仮説(未検証)**: z+s の連続で話し言葉ではsが融合し「AI sent」に聞こえやすい。

## 5. なぜHRか
- 直接の理由: M3 Style Gate(`er019_family_x_style_profile_01.py:685-760`)が `entry["local_rewrite_recovery"]` を違反とし(`:742-743`)、`_approved`(`:629-634`、`record_human_approval` の canonical text SHA一致)以外で解除しない。Stdは加えて `STD_FALLBACK_USED_OR_UNKNOWN`(`:716-717`)。
- 正式仕様の位置づけ: `CURRENT_SPEC.md:3166`『③/LR採用音声は既存fail-closed Gate(X M3 Gate…)がBLOCK対象として検知(…`LOCAL_REWRITE_RECOVERY`…)。Gate・QA blocking条件は無変更。HR増は「Gate緩和」を提案する場合のみユーザー承認事項』、`:2856`(2026-10-21ユーザー決定: fallback takeの採用はM3 Gateの正規承認記録による個別判断)、先例 OPEN-499(Word Gacha Adv part3、LR採用、UDR #183 (a) でユーザーが個別承認)。
- 区別: 音声品質の問題ではない/原稿整合の問題(本文「AIs」と音声「AI agents/systems」の1語差)であり、ASR認識差が引き金。HR対象音声が確認する内容=その1語差を許容してよいか。
- 注意: `CURRENT_SPEC.md:2213` は LR 成功時 Human Review **Lock** へ進まない(`RESOLVED_BY_LOCAL_REWRITE`)としており、Lockは0件。止めているのはM3 Style Gate(別機構)。ユーザー原文が明示する「正式仕様が明示的にHRを要求する場合は省略しない」に、先例・仕様3166で該当すると判定。M3 Gateの`LOCAL_REWRITE_RECOVERY`ルール自体の導入(OPEN-312、2026-10-12)はFable/Sonnet設計+Opus review。ユーザー原文の明示承認文は確認できていない(先例による黙示的運用)。→ Gate緩和の可否はユーザー判断(判断候補)。

## 6. M3 記録非対称(OPEN-564)の影響 — 実害なし
in-memory模擬(ファイル書込なし、`er019_family_x_style_profile_01.m3_assembly_gate('fx_20261017', level, results, None)`): 実データ Std=BLOCK[`STD_FALLBACK_USED_OR_UNKNOWN`,`LOCAL_REWRITE_RECOVERY`] / Adv=BLOCK[`LOCAL_REWRITE_RECOVERY`]。Std `fallback_used=False` に差替え→なおBLOCK[`LOCAL_REWRITE_RECOVERY`]。LR記録を除去かつfallback False→PASS。→ BLOCK根拠は `LOCAL_REWRITE_RECOVERY` 単独で成立。

## 7. 判定
- 不具合/配線漏れ: なし(DIAG_SLOWDOWN_ASR_01の結論を追認)。承認済み自動処理は全て正しく適用された上で未解消。
- 原稿の未承認変更: なし(音声のみ1語句、本文不変)。
