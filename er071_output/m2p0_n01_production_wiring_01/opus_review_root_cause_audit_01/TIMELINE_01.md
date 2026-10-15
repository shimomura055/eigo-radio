# TIMELINE_01: gloss再整合段 仕様設計〜採用提案の時系列(KP-GLOSS-OPUS-REVIEW-ROOT-CAUSE-AUDIT-01 委任_01)

表記: 日時はJST(= セッション記録のUTC timestamp + 9h)。「SJ」= セッション記録 `f2c17cf7-6207-4666-abec-016808eac6d3.jsonl`(原本は非commit)の行番号、「VERB」= 本ディレクトリ `OPUS_REQUEST_AND_FINDINGS_VERBATIM_01.md`。[確認]=一次記録あり、[未確認]=記録なし。Fableの内部思考はセッション記録上redacted(thinking長=0)で復元不能。

| # | 日時(JST) | イベント | 実行者 | 委任ID/commit | 証拠 |
|---|---|---|---|---|---|
| 1 | 2026-10-14 20:03:23 | ユーザーが「KP-gloss整合は基本品質要件。G1〜G3から選ばせない。Humanに戻さない。既存機構優先・自動整合・新仕様が本当に必要な場合のみユーザー判断」と指示 | ユーザー | - | SJ L12761(timestamp 11:03:23Z) / `docs/pm/delegation_log/2026-10-14_FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01_委任_04.md` §0 [確認] |
| 2 | 20:06:07 | 仕様設計+実装を**1つの**Sonnet委任で開始(設計の事前Opus条件Aレビューなし) | Fable→Sonnet | FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04 | SJ L12767 [確認] |
| 3 | 20:47:10 | 実装・test・Production配線(`run_key_phrase_canonicalization`内)をmainへcommit。原設計: 失敗時はKPを候補へ戻す。再整合Promptにスロット限定文「key_phrase自体が『someone's』『something』等を持つ場合に限り『～』の使用を許可」(L123-125)を既に含む | Sonnet | 3b64e5632 | `git show 3b64e5632:er003_key_words_gloss_alignment.py` L10,L123-125; `GLOSS_ROOT_CAUSE_AND_FIX_04.md` §3 [確認] |
| 4 | 20:57:27 | SSOT反映+CHECKLIST_05。行11「Opus条件A…未実施」と自己記録(`PRODUCTION_WIRED`不付与) | Sonnet | 9f40c1a62 | `CHECKLIST_05.md` L3,L17,L24 [確認] |
| 5 | 20:58:05 | Sonnet委任_04のhand-back(Fableへ) | Sonnet | - | SJ L12882(11:58:05Z) [確認] |
| 6 | 20:58:59 | **Opus依頼(条件A/C、実装・配線・push後)**。約3,000字のカスタム依頼文(12観点ブロック・context packet未使用) | Fable→Opus | opus-consultant agentId a3087934ca4984bd4 | SJ L12890; VERB §A [確認] |
| 7 | 20:59〜21:02 | Opus実作業: Read/Grep/Glob計25 tool_use(コード・GLOSS_ROOT_CAUSE・CHECKLIST_05・census・OPEN_ITEMS・CURRENT_SPEC・PM_GOVERNANCEを参照)。テスト実行・git実行なし(ツール上不可) | Opus | - | `subagents/agent-a3087934ca4984bd4.jsonl` L11〜L82(25 tool_use) [確認] |
| 8 | 21:02:05 | Opus所見(OF-225〜235)hand-back | Opus→Fable | - | SJ L12904; VERB §B [確認] |
| 9 | 21:02:58 | Opus所見を全件「採用」(225/226のみ記録のみ)としてSonnetへ是正委任(所見受領から約53秒。この間のFableのtool_use=0) | Fable→Sonnet | KP-GLOSS-ALIGNMENT-PRODUCTION-01 委任_01(agentId aeb4f672f13bca62f) | SJ L12912; VERB §D [確認] |
| 10 | 21:03:39 | ユーザー向け統合報告(Opus依頼中である旨・7項目) | Fable | - | SJ L12921 [確認] |
| 11 | 21:22:49 | 是正・有効性検証(実API 12呼出、JPY1.18)・Regression・SSOT(OPUS_FINDINGS_LEDGER OF-225〜235を含む)をcommit/push | Sonnet | a337d8acc | `git show --stat a337d8acc` [確認] |
| 12 | 21:23:31 | Sonnet hand-back(FIX_01/VALIDATION_01/Q1_Q3_DRAFT)。「課題指示文と承認規則の『～』文言が緊張関係。実装は課題指示文側」と自己申告 | Sonnet→Fable | - | SJ L12926; VERB §E [確認] |
| 13 | 21:24:08 | Fableがユーザーへ採否判断(Q1〜Q3)を提示。hand-backから**37秒**、この間のtool_use=0 | Fable→ユーザー | - | SJ L12934(12:24:08Z); VERB §G [確認] |
| 14 | 21:24以降〜 | **a337d8acc後の再Opusレビュー: セッション記録に無し** | - | - | EXTRACT_01.json(opus-consultant呼出はrecord 1のみ。10-15の別目的レビューrecord 27は設計草案KGDC用) [確認] |
| 15 | 2026-10-15 10:03 | ユーザーが設計欠陥2件とレビュー不全の調査を指示(KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01) | ユーザー | - | `a66c19e8-....jsonl` L99(01:03:25Z) [確認] |

所要: ユーザー指示(20:03)からQ1〜Q3提示(21:24)まで約81分。うちOpusレビュー約3分、Opus所見→是正完了約20分。

## 設計段階の事実
- 仕様設計(原設計)から実装・配線・pushまでが同一Sonnet委任内で完結し(#2〜#4)、Opus条件A(PM_GOVERNANCE 11-3「実装前」)は設計・配線後に実施された(#6)。設計時点のOpus/Fable事前レビューの記録は未確認(セッション記録にも該当なし)。
- 「『～』をスロット語KPに限る」文言は#3(Opus以前)に存在した。
