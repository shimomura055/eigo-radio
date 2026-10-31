# SPEC_HISTORY_01(JA-TRANSLATION-LITERALNESS-AUDIT-01 委任_01A 調査①、2026-10-31、API 0)

調査対象: CURRENT_SPEC.md / DECISION_LOG.md / OPEN_ITEMS.md / docs/pm/delegation_log/ / docs/research/ / コード(origin/main 013d0fab2 のsparse worktree。行番号はこの版)。
Grep語: 逐語訳|対訳|意訳|要約|英日連動|ja_align|R2|日本語訳|translation|translate_part|generated|approved。

## 0. 結論(先に)
- **「逐語訳」「意訳」を含む決定・仕様は、SSOT3ファイル(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS)に1件も無い**(`grep -c 逐語訳`=0/0/0、`意訳`=0/0/0)。ユーザー原文(delegation_log/*_USER*.md)で「逐語訳」を含むのは次の3文書のみで、**いずれも「機械的な逐語訳を強制しない」「意味を無視した逐語訳は不適切」という逆方向の指示**(KP日本語意味=gloss用): `2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_USER.md:27` / `2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md:34` / 同`_USER_03.md:59`。
- したがって「ユーザーが承認した、日本語訳を逐語訳にする/意訳・要約を禁止する」仕様は**存在しない(確認できた範囲)**。近い承認済み仕様は下記A群(忠実英訳=JA→EN方向、承認済み訳のみ表示、生成訳の情報追加/省略禁止Prompt)。
- 今回の2か所(X Std story)は、**英語→日本語の翻訳ではなく、日本語原稿(R2)が原本で、英語が派生物**(JA→Advanced英語[忠実英訳]→Standard英語[A2書き直し])。ページはR2段落をそのまま「日本語」として英語段落の横に置く(`ja_source=approved_ja_manuscript`)。詳細はPATH_TRACE_01.md。

## 1. 承認済み仕様(APPROVED_FOR_PRODUCTION)で、本件に関係するもの
| # | 決定(原文引用) | 出典 | 日付 | 対象Family/Level/種別 | 現在有効 | Production配線 |
|---|---|---|---|---|---|---|
| A1 | **忠実英訳**: 「Translate the Japanese article below into English, paragraph by paragraph, staying as close to the original as natural English allows. Do not add new ideas…Do not remove any fact, claim, or causal link…exactly the same number of paragraphs…」(Production定数。Trial `er045` Promptの逐語転記) | CURRENT_SPEC.md:1406-1412(「新記事構造…忠実英訳…`APPROVED_FOR_PRODUCTION`→`PRODUCTION_WIRED`、2026-09-29、FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 W1」)/ DECISION_LOG.md:12680-12690(Trial記録)・12967(採用)/ コード `er003_v1_n3_01_advanced_adaptation_generate.py:522-560` | 2026-09-28ユーザー正式決定、09-29配線 | X Advanced(JA R2→EN)。YもAdvanced英訳に同関数を使用(`er121_family_y_runner_01.py:389`) | 有効 | PRODUCTION_WIRED。**段落単位**の忠実性。文単位対応・「逐語」の要求は無い |
| A2 | **Standard(A2)=Advanced英語を書き直す**: 「Rebuild the sentences…Split long clauses…Do not turn the article into a summary…Do not add new facts…Keep every fact exactly as it is…Keep the same paragraph structure」。**入力は日本語R2ではなくAdvanced英語** | `er003_v1_n3_01_standard_a2_generate.py:506-528`(`FAMILY_X_STANDARD_A2_NO_HEADING_PROMPT`)、:541-600 | 2026-09-29(W5で構造Gate対称化) | X/Y Standard英語 | 有効 | PRODUCTION_WIRED。文を意図的に再分割する設計(文数が日本語と合わなくなる) |
| A3 | **End Userページの日本語=承認済み日本語原稿/正式な翻訳データのみ**: 「承認済みの日本語原稿・正式な翻訳データを使用する。DEV版の未承認翻訳11ブロックをそのまま正式採用しない。…未承認の翻訳方式を独断で導入しない」 | `docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01_USER.md:56-63`、CURRENT_SPEC.md:3292(「訳の非表示: 承認済みデータのみ(X Full Story=ja_writer/revision2.md段落、Y=dev page内の承認済み日本語原稿)」) | 2026-10-29 | X/Y story=日本語原稿。それ以外は当時非表示 | 有効(A4で一部拡張) | PRODUCTION_WIRED_PENDING_FABLE(OPEN-597) |
| A4 | **英日連動ハイライト**: 「英語1文と、その文に対応する日本語訳を連動させる。文の区切りが一致しない場合も、意味的に対応する日本語部分をハイライトする。文の対応が不明確な場合、誤った日本語をハイライトしない。**英語・日本語の本文内容や翻訳そのものを、今回の表示変更のために書き換えない。**」 | `2026-10-30_ENDUSER-EN-JA-LINKED-HIGHLIGHT-01_USER.md:35-40`、CURRENT_SPEC.md:3300 | 2026-10-30 | X/Y/Z×Std/Adv(訳があるパート) | 有効 | X/Y story=PRODUCTION_WIRED_PENDING_FABLE(OPEN-618)。**対応づけ(表示)の仕様であって、訳の逐語性の仕様ではない** |
| A5 | **不足訳のみ生成**: 「既存の日本語訳を再利用し、実際に不足している部分のみ補う。…承認済みの日本語訳を不要に再生成しない。新規生成が必要な場合は既存の翻訳品質Gateを適用する。英語の意味を正しく反映する。正式初回…だけでなく、再生成・再開経路にも適用する」。ユーザーは「基本的には英語本文に対応する日本語文が存在するはずであり、英日対応が大きくずれるのは例外的なケースと考えている」 | `2026-10-30_ENDUSER-EN-JA-LINKED-HIGHLIGHT-01_USER_02.md:40,120-136`、CURRENT_SPEC.md:3301 | 2026-10-30 | 訳の無いパート(X Adv Preview/Comment、X In One Line、Z story等)=`ja_source=generated` | 有効 | 03Bで配線(PRODUCTION_WIRED_PENDING_FABLE相当、OPEN-618)。生成訳Promptは「意味を正確に訳す。意味を変えず、情報の追加・省略をしない」(`er135_enduser_translate_01.py:41-42`)。**「逐語」「意訳禁止」の語は無い** |
| A6 | **KP「本文引用英文の日本語訳」**(T1専用翻訳工程) | CURRENT_SPEC.md:2112(2026-10-25ユーザー正式承認、`er003_kp_source_sentence_ja_01.py`) | 2026-10-25 | Z/X Key Phrase解説の引用英文訳 | 有効 | PRODUCTION_WIRED(OPEN-512)。入力=引用英文のみ。構造検査のみ |
| A7 | **KP日本語意味(gloss)は逐語訳を強制しない** | `2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_USER.md:27`「機械的な逐語訳を強制せず、自然な日本語と原文の意味の両方を守る」/ `2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER.md:34`「本文の意味を無視した逐語訳は不適切」 | 2026-10-19/23 | KP日本語意味(X/Y/Z) | 有効 | CURRENT_SPEC.md:1642(人称整合module)ほか |

## 2. Trial成功のみ・未承認・棄却(混同禁止)
| 項目 | 状態 | 出典 |
|---|---|---|
| 生成訳Prompt改善案B3 | **REJECTED**(再採用しない) | OPEN-636/638、ENDUSER-TRANSLATION-CONTEXT-TRIAL-01_USER.md §2 |
| 生成訳への文脈付与(方式A〜E+F) | **未承認Trial**(INVESTIGATING、Production変更0) | OPEN-638 |
| 日本語訳品質アラーム(独立チェック+HR赤字警告) | **未承認Trial**(INVESTIGATING) | OPEN-636 |
| JA/EN paired rewrite(J-1)等の対訳Trial | 旧Family A系Trial(本件対象外) | DECISION_LOG.md:14645,14709 |
| 旧Fact Checker / Ledger Deviation Check(英訳後のJA-EN照合) | **2026-10-10 Production撤去済み**(SUPERSEDED) | CURRENT_SPEC.md:1194-1196、OPEN_ITEMS.md:416 |
| 「逐語訳必須」「意訳・要約の禁止」(日本語訳表示向け) | **どこにも未決定・未承認**(原文・SSOTとも該当なし) | 上記Grep |

## 3. 既存の翻訳QA/Validator/Regressionが検査する内容(file:line)
| 対象 | 検査 | 検査しないこと |
|---|---|---|
| 生成訳(`ja_source=generated`)`er135_enduser_translate_01.py` | ①数値決定論照合 :259-269 ②構造検査(空/CJK/同一/禁止/文結合疑い) :291-311 ③LLM対訳照合 :56-65(反転・数値・固有名・**情報の欠落/追加**を ok=false、言い回しは不問)+不合格はretry(MAX_VERIFY_ROUNDS=2 :35、指摘注記 :314-319)→段落fail-closed(英語のみ+warning) | 文脈無し(:521)で語義違いを見ない(OPEN-634/638)。**承認済み訳(X/Y story)には一切適用されない** |
| 承認済み訳の取込 `er135_enduser_page_01.py:625-657` | X: 段落数一致(:638-643、不一致はSTOP)/ Y: dev page日本語とsplit_y_articleの空白除去一致(:651-655) | **内容の対応(欠落・追加・要約)は検査しない**。段落数が合えば通る |
| 連動 `ja_align`(`er135_enduser_align_01.py`、検証は`er135_enduser_page_01.py:1463`) | 整列の整合(UTF-16 offset、被覆、保存値)。確信が低い群はnull | 訳自体の品質ではない(表示の対応づけのみ) |
| 英訳生成(X/Y Advanced/Standard) | 構造Gate(Title/段落数、見出し混入)、数値保持(`numeric_retention`)、**Risk Flagger(非Blocking)**=完成英文×検証済みFact台帳(JA R2ではない)(CURRENT_SPEC.md:1185-1192、`er053_risk_flagger_production_01.py`) | JA R2とStandard英語の文・節単位の対応。旧Deviation Check(JA/Ledger照合、MAJOR→再生成)は2026-10-10撤去済み |
| KP gloss | 人称・指示対象整合 `er003_key_words_gloss_alignment.py`、T1訳の構造検査 `er003_kp_source_sentence_ja_01.py` | 文中の意味の逐語性は不問(A7) |
| Regression | `er135_enduser_translate_test_01.py`、`er135_enduser_page_test_01.py`(段落数不一致STOP等)、`er135_enduser_align_test_01.py` 等 | 「訳が英文の情報を過不足なく含む」の実データ回帰は、承認済み訳には無し |

## 4. 過去の同種不具合と対策
| 件 | 内容 | 対策 | 本件との関係 |
|---|---|---|---|
| OPEN-634 | 生成訳 Adv Comment 4 `things left out`=「省かれたもの」(語義不一致) | 該当partのみ再生成(文脈欄に直前part)。恒久策=OPEN-638 Trial | 生成訳経路。承認済み訳(今回)とは別経路 |
| OPEN-638 ERROR_CASES_01 | 生成訳310文(公開10記事)のAI全件裁定: 重大0(是正後)/中4文(1.3%)/軽27文(8.7%、主に訳語不整合) | 文脈Trial | 生成訳のみ。**承認済み訳573文は母集団外**(ERROR_CASES_01.md §1) |
| OPEN-243 | 翻訳段(JA→EN)由来の事実NGとEN Deviation Checkの見逃し | 旧Checker系は撤去、W-1+RF+HR方針へ | JA→EN方向の事実NG。日本語表示とは別 |
| OPEN-230 | 忠実英訳はFact精度を自動保証しない(Meta「元に戻した」意味反転) | must-fix retry | 同上 |
| OPEN-618/ENDUSER-JA-CAPTION・TRANSLATION-CONTEXT | 英日の文単位対応データは存在しない(訳は段落単位)。順序対応が成立するのはStd約15%/Adv約75%のみ | ja_align(DP+埋め込み)で表示上の対応づけ | **本件の構造原因と同一事実**(DECISION_LOG.md:22943付近) |

## 5. 「採用済みで未配線」の有無
- 逐語訳/意訳禁止に関する承認済み・未配線の仕様: **確認できず(該当仕様自体が無い)**。
- 承認済みだが未完のもの: A4/A5=`PRODUCTION_WIRED_PENDING_FABLE`(Fable受入待ち、OPEN-618)。配線漏れではなく受入待ち。
- 注意: 「Familyにより訳の出自が異なる」(X/Y story=日本語原稿、Z=英語原作の生成訳、X Adv Preview/Comment=生成訳)ため、共通の訳品質仕様が無い状態は**配線漏れではなく仕様自体の未定義**。

## 6. 未確認
- 過去のユーザー口頭/チャット指示でSSOT・delegation_log未記録のものは確認不能。
- delegation_log全ファイルのGrepは「逐語訳|意訳」で実施。「対訳」「要約」は該当が多く、関連(上記)のみ精査。
