# OPUS_REVIEW_01 — Opus独立技術レビュー結果(逐語。委任_01設計 commit b633a612b 対象)

## 1. 結論: GO with changes（修正付きで進めてよい）

- 方式（X方式の`resolve_run_profile`をYに配線し、新run dirを使う）、33 take（Adv 15 / Std 18）、5 clip再生成の案R、V1（Voice本文にもPD06）は、どれも承認記録・コードと整合しています。
- ただし fail-closed Gate の「role網羅」検査は、設計どおりに実装すると Y 本文で空振りします（M-1）。legacy waiver が default 音声の新規生成経路になり得ます（M-2）。
- PD06 の文面は人物の語りを平板化させる懸念が文言上も具体的にあります。さらに A19 の承認は「S9評価で確認する」条件付きで、その評価は未実施です。V1 は「配線是正」で完了扱いにせず、S9 をユーザーの判断事項として明示して提出する必要があります（M-3）。

## 2. 判定表

| 論点 | 判定 | 根拠（ファイル:行） | 必須(M) / 推奨(R) |
|---|---|---|---|
| P-1 Voice本文にPD06 | 妥当（条件付き） | PD06の実文 `er019_family_x_style_profile_01.py:108-111` は「a smile in your voice」「reassuring」「like a favorite morning radio host」「keeping the news clear and credible」。どれも司会者役への指示で、全話者に一様な明るい感情の色を付けます。批判的・不満を述べる人物と食い違う可能性が文言から読めます（default 側の「calm, steady news narration…not dramatic」も語り手型ですが、感情の方向を指定していません）。A19/T10（`DESIGN_PROPOSAL_02.md:109,242`）は「適用」ですが、同:347 は「S9をTrialで評価し、PD06除外等が要れば再判断」とする条件付きの承認で、その評価結果は記録がありません（STYLE_MATRIX §6-2）。前例も無く、Z の人物 Dialogue は PD06 非適用です（`DESIGN_PROPOSAL_02.md:317`）。一方 V2 は Y 固有承認の Style ではなく、新しい例外です。V1 を既定とする判断自体は正しいです。 | **M-3**: 再提出では、Voice 1〜3（Std/Adv 6 segment）を「S9未評価のユーザー判断項目」と明記します。旧`_02`（default）と新版を segment 単位で並べ、追加費用は0円です。差戻し時の V2 の費用・時間（約8円）も添え、S9 確認前に「完成」「PRODUCTION_WIRED」と呼びません。**R-1**: Std 本文は PD06 逐語のため、旧 default にあった減速指示の連結が消え、話速が変わり得ます（後処理の6%減速は継続）。前後比較表に話速（WPM）を入れます。**R-2**: V2 実装例の `_base` は、Std では `_base_slower` にします（DESIGN 2-2-4）。 |
| P-2 fail-closed Gate | 要修正 | (1) `m3_assembly_gate` は FULL_STORY の対象を `full_story_part1..3` に固定しています（`er019…:201-202,675-681`）。Y ではこれらが entry=None のまま `checked` に入り、その後 `_X_ONLY_SEGMENTS` で除外されます（`er121_family_y_audio_01.py:765,799`）。このため設計(iv)「`x_gate.checked` が当該roleで≥1件」は、Y 本文が1件も検査されなくても満たされます。(2) SUPPORT_JA と KP_JA_MEANING は base sha だけで判定しています（`er019…:564-569`）。しかも `_generate_or_reuse` で再利用した entry は「untouched」扱いにならず、`attach_segment_profile_record` で現行 profile の sha が上書きされます（`er121…audio:699-700`、`er019_family_x_audio_production_runner_01.py:1114-1117`、`validation_inheritance:186-189`）。そのため日本語 role の照合は構造上「一致」になり、実際の送信値の測定にはなっていません。今回は新 run dir（M2）なので実害はありませんが、`style_actual_vs_approved.json` を「実測照合表」と呼ぶ根拠になりません。(3) 英語 role の偽陽性は確認範囲では見当たりません。発音 hint ありは head200 の前方一致で判定（`er019…:584-588`）、Std は逐語で sha 一致、LR は `<default:` → RECORD_MISSING とあわせて BLOCK → HR で、設計どおりです。resume は同一 profile なので問題なく、chunk は全 chunk を検査しています。(4) 並行中の TTS 統一（er127）は未コミットのため未確認です（ファイル0件）。 | **M-1**: 網羅検査は `x_gate.checked` ではなく、Y 側の期待集合（`Y_ROLE_COVERAGE` の role×level×segment）との**完全一致**で判定します。entry が存在し、`evaluate_segment_evidence` を実行した件数で数え、≥1件ではなく全件を要求します。**M-4**: 照合表の日本語行は送信 instruction の実測値（attempt または raw_usage_log の instruction）から取ります。取れない場合は「意図sha（実測なし）」と明示ラベルを付け、一致扱いにしません。**R-3**: er127 が Adv ③（短文Style）を承認済みの通常成功経路にする場合、現 Gate は `ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED` で BLOCK します。そこで「採用 attempt 番号＋承認済み Style 変種の一覧」を Gate が参照する形を er127 側の設計で定義します。順序は er127 確定 → Y Gate 実装です。**R-4**: profile 有効化で Adv の `ADV_MINIMAL_FALLBACK`、Std の `STD_FALLBACK_USED` が Y にも効き始めます。人間確認（HR）待ちの発生率が上がり得ることを QDC 見込みに入れます。 |
| P-2 補足 legacy waiver | 要修正 | `resolve_run_profile` は CLI で `default` が指定されると、run state の有無を見ずに default を返します（`er019…:481-482`）。waiver はファイルの path を渡すだけなので、AI 側で作成できます。 | **M-2**: waiver は (a) 既存 run state あり・固定記録なしの dir に限定し、(b) `tts_*` stage との併用を禁止して課金前に STOP し、(c) ref は `docs/pm/delegation_log/*_USER.md` 配下で対象 run の path を含むことを検査します。旧 run の再 pages が不要なら、waiver 自体を作らないのが最善です。 |
| P-3 再生成範囲 | 妥当 | 5 clip が Style 不変という判定はコードで確認しました。Adv topic_intro=`TOPIC_INTRO`、comment=`COMMENT` はいずれも override なし（`er121…audio:571,581`）。Std topic_intro=`TOPIC_INTRO`、japanese_title=`_role_style_ja()` で profile を通りません（同:678,688）。音声の再利用機構は同一 out_dir の cache だけで（`er019…runner:1076-1118`）、新 dir では M2 により結果ファイルを持ち込めません（`er019…:290-295,483-493`）。案R が正しいです。Voice 2/3 の再生成が必須という理解も正しいです。ただし本質的な理由は sha ではなく、音声自体が誤った Style で生成されていることです。 | **R-5**: ユーザー原文は「無関係な音声は再利用」なので、5 clip（約2.5円）を再生成する理由（新しい引継ぎ機構を作らない）を報告に1行明記します。**R-6**: KP 英語（K2）が Std と Adv で同じ Master Store key を共有する場合、2つ目の level は Store hit になり、3 take 少なくなる可能性があります（未確認。見積の過大側）。 |
| P-4 再発防止 | 一部不足 | (a)(c)(d) と M-1 で、Y の配線漏れは機械的に検出できます。ただし (c) の test は Y 専用（`er121_*`）です。新 Family では、その test を作らない限り何も検出できず、チェックリスト（人手の手順）頼みになります。X の `checked=[]` で PASS する経路は profile=default の分岐だけです（`er019…:695-696`）。default 以外の profile では `_gate_targets` が必ず名前を生成するため、`checked` は空になりません。共通 helper で塞ぐと、X の legacy default resume（公開済み旧 run）を壊します。 | **R-7**: 横断の登録表（Family→runner→`ROLE_COVERAGE`）と、Production runner を glob で列挙し、未登録なら FAIL する test を1本作ります。これで新 Family の未配線を機械検出できます。**R-8**: `m3_assembly_gate` の default 分岐は変更しません（X に影響するため）。各 Family の runner 入口で「新規 run は承認 profile 必須」を assert する方式が影響最小です（X は既に `DEFAULT_NEW_RUN_PROFILE` で同等）。Z の実測照合は未確認のままで、別途 read-only 確認でよいです。 |

## 3. 見落としリスク

- **再利用 entry の上書きで照合が自己一致になる**: 再利用した entry には現行 profile の sha が上書きされます（P-2(2)）。英語 role は最終 style の記録で実測検査されますが、日本語 role は自己一致になります。将来「同一 dir で profile を移行する」経路（`migrate_record`、`er019…:767-`）を Y で使うと、古い Style の日本語音声が PASS します。Y では使用禁止とするか、M-4 の適用が前提です。
- **長い PD06 と Puck の安定性**: Puck は default Style では1 attempt で通っていましたが、177字の PD06 との組合せは未経験です。retry 率は未知です（Cap 60円の範囲内）。
- **ゲート判定を固定記録からも取る**: `y_style_gate` は profile を引数で受け取ります。DESIGN 2-1-7 の再検証に加え、Gate 内でも `read_record` を正として、引数と食い違えば STOP するのが安全です。
- **並行作業の順序**: OPEN-527 の test が `r.STYLE_PROFILE` を参照しているため、名称撤去の前に並行委任を完了させる必要があります（設計どおり）。er127 が未コミットなので、照合キー（top-level `style_prefix` の正規化）の最終形は未確認です。
- **未読範囲**: ROOT_CAUSE_01 §Q2 と `assemble_level` の内部（Gate の再呼出しの有無）は読んでいません。

## 4. 5行要約

1. 方式・再生成範囲（33 take、案R）・V1 は承認記録とコードに整合しており、GO with changes です。
2. M-1: Y 本文の網羅検査は `x_gate.checked` だと X 専用の名前で空振りするため、Y 期待集合との完全一致で判定します。
3. M-2: legacy waiver は tts stage との併用を禁止し、ユーザー記録の ref 検査を必須にします。M-4: 日本語 role の照合表は実測値を使うか、「実測なし」と明示します。
4. M-3: PD06 の文面（smile / reassuring / radio host）は人物の語りを平板化し得ます。A19 は S9 評価が条件でしたが未実施なので、Voice 1〜3 は旧版と並べた試聴でユーザー判断項目として提出します。
5. X の `checked=[]` の穴は default 分岐だけで、共通化は X に影響するため見送ります。新 Family の配線漏れの機械検出には、横断の登録表 test（R-7）を推奨します。
