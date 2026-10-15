# INVESTIGATION_01 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_01A、2026-10-15)

性質: 調査のみ(コード変更なし、有料API呼出なし、費用JPY0)。根拠は`ファイル:行番号`。**読解で確認した事項**と**実行で確認した事項**を区別する(実行確認は各節に明記。無印は読解)。

## 1. 承認済みgloss規則の正本
- 正本: `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(ファイル全体sha256 `69d0e6ff…e8f6`)。再整合段は実行時に該当段落を抽出して使う(`er003_key_words_gloss_alignment.py:119-134` `load_approved_gloss_rules`)。**抽出結果**のsha256は実行で再計算し `447e07cb8b9a30850a8dc75b6c3cce48c53d99b5f1fafa88d19b778d9155949b` と一致を確認(指示の「447e07cb…」はファイル全体ではなく抽出後規則文字列のsha256)。
- 該当文言(`gloss_alignment_01/prompt_example_01.txt`に全文転記済み): 「日本語グロスは、辞書的な表記として自然な範囲であれば「～」「〜」を使ってもかまいません(例: 「～を示す」)。ただし「…」のようなプレースホルダー記号は使わないでください。数字は漢数字」「括弧で補足を書き添えない」「選ぶ表現は必ず本文中の実表現(source_span)に対応させ、短く自然な日本語グロスを付けて」。
- 帰結: 承認済み規則は「～」の有無を合否条件にしていない。「～」は許可、禁止は「…」・括弧・算用数字のみ。

## 2. 正式経路と再整合段の通過
順序(実コード): 選定(`run_key_phrase_selection`)→ `run_key_phrase_canonicalization`(`er003_v1_n3_01_scaffold_generate.py:683`)内で canonicalization(LLM) → `merge_canonicalization_result` → **`gloss_align.align_glosses`(同:724-725)** → `keywords_canonicalized.json`書込(同:730-731)→ 戻って `_run_key_phrases_impl`(同:812-)が Redundancy QA(同:~875)と記号QA(同:~885、NGなら選定からやり直し、上限`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)→ 呼出元runnerがTTS(KPは`keywords_canonicalized.json`の`japanese_gloss`を直接読む。Family X: `er019_family_x_audio_production_runner_01.py:753,1117,1344` / 出力利用:898,994,1269)→ Audio Validation Gate(`er003_v1_n3_01_assemble.py:~480-515`)→ assemble。
- ユーザー指示の工程順「1 候補選定・初期gloss → 2 英語KP最終確定 → 3 再整合 → 4 必要な品質判定 → 5 TTS」に対し、現行も順序は概ね一致する(再整合は`run_key_phrase_canonicalization`内、Redundancy/記号QAはその後)。**欠けているのは順序ではなく「3の失敗が4以降・5を止める結合」**(Redundancy QAも再整合失敗を入力として見ない)。
- Family X(M2P0/N01): `er019…:404` `sc.run_key_phrases(..., kp_backend=kp_backend)` → 再整合段を**通る**(flag ON時)。
- Family Z(Strategy L, `process=None`): `er026_family_z_fiction_production_runner_01.py:796`(legacy `kp`) および E2E `stage_kp` → `w62.run_kp_stage`(同:1161-1180)→ 最終的に同じ`run_key_phrases`を通る(読解。`w62`内部は未精読)。再整合段を**通る**。
- 既定ONの影響範囲: `run_key_phrases`の呼出元は `rg` で 40 前後のスクリプト(er003〜er035、Family A/B/C/News/Z/X・各種Trial)。**全員**が再整合段の影響下(flagで一括)。

## 3. 「～」機械FAILを追加した理由(OF-230)と不適切な点
- 経緯(`docs/pm/OPUS_FINDINGS_LEDGER.md:258`): Opus所見OF-230「LLM自己申告(`qa_reflects_all_key_phrase_words`)のみに依存し、スロット『～』残存を機械的に検出できない」→ Fable採用 → 実装は「KPにスロット語(someone/something/one's等、`gloss_alignment.py:47`)が無いのに、glossに『～』が残ればFAIL」(同:223-226, 252-253)。
- 不適切な点(工程目的=最終KP全体の意味と日本語の整合):
  1. 検出したいのは「KPに追加された具体語の意味がglossに無い」ことなのに、**表層記号**(「～」)の有無に置換した。承認済み規則(辞書的に自然なら「～」可)と衝突(課題指示文自身が承認規則を引用しつつ「スロット語がある場合に限り許可」と矛盾する旨は`Q1_Q3_DRAFT_01.md`で既に注記)。
  2. 検出力が低い: オフライン監査(`OFFLINE_AUDIT_01.md`)で、目視で不整合と判定した6ユニークのうち「～」ルールが捕捉できるのは3(50%)。`raw-bean prices→焙煎前のコーヒー豆`、`bring in a human helper→人を呼んで加える`、`close around me→周りから迫ってくる`は「～」が無いので素通り(いずれも意味欠落)。
  3. 誤NGの危険: census 29件(KPにスロット語なしで「～」あり)のうち28件は承認規則上正当と推定(目視7+機械推定21、ユーザー未確認)。これらが再整合対象に入って正しい辞書表記「～」を返せばFAIL→retry→fallbackへ落ちる。実出力での誤NGは0/16だが、それは対象に入った8ユニークでは「～」を要しないKP伸長だったため(サンプル依存)。

## 4. FAILED通知のみで継続する設計になった経緯(OF-227/228)
- OF-227(`LEDGER:254`): 旧fallback「KPを候補へ戻す」は、候補が不完全(末尾機能語)でqa/reasoningと矛盾 → (ii)「最終KP維持」を既定へ。OF-228(同:255): 失敗がrun summaryに載らずサイレント → `gloss_alignment_status=FAILED`+events+NOTICE.md+stdoutで通知、**「Human Review送りなし」**(同:255「Human Review送りなし」、`FIX_01.md:10`「人間確認Queueへは送らない」、`gloss_alignment.py:322-324`コメント)。
- 解釈の根拠: 委任文01 §0「Human Reviewを常態化しない」(`delegation_log/…KP-GLOSS-ALIGNMENT-PRODUCTION-01_委任_01.md`)。これを「Human Reviewへ一切送らない」と読み、通知のみで下流を止めない設計にした。ユーザー2026-10-15の判定は「常態化しない=通常運用にしない」であり、**例外の最終対応としてのHuman Reviewは必要**。解釈が過剰に広かった。
- 通知の実体も弱い: `write_failed_notice(out_dir=kp_dir)`(`scaffold_generate.py:806-807`)はrun root直下ではなく `key_phrases/` 配下へ書く。M2 fallbackの通知(`er019…:427-429`でrun root)と異なり、runnerのsummary/最終stdoutに入らない(次節)。

## 5. FAILED後にTTS・assemble・完成Gateがどう振る舞うか(「停止しない」)
| 箇所 | 行 | FAILEDの扱い |
|---|---|---|
| gloss module | `gloss_alignment.py:365-382` | item `gloss_alignment_status="FAILED"`/`gloss_review_hint=True`、`merged["gloss_alignment_failed"]`を設定。戻り値`status`は変えない |
| canonicalization | `scaffold_generate.py:727-731` | `result["gloss_alignment_status"]=aligned["status"]`(= `ALIGN_FAILED`)を記録。`result["status"]`は`CANONICALIZATION_PASS`のまま→`merged`を書いて返す |
| run_key_phrases | `scaffold_generate.py:802-808` | `gloss_alignment_fallback_events`を追加、NOTICE書込、stdout印字。**例外・停止・status変更なし** |
| ループ判定 | `scaffold_generate.py:~870-905` | Redundancy QA/記号QAの`status`のみで分岐。gloss FAILEDは見ない(=選定やり直しも起きない) |
| Family X runner scaffold | `er019…:404-419` | `kp_status=canonicalization.status`(=PASS)。`gloss_alignment_fallback_events`を**読まない**。`scaffold_run_summary.json`にも載らない(載るのは`m2_fallback_events`のみ、:414-419) |
| Family X TTS | `er019…:753,898,994,1269` | `keywords_canonicalized.json`の`japanese_gloss(_tts)`をそのままTTS→`generate_charon_japanese…`。`gloss_alignment_status`/`gloss_review_hint`を**参照するコードは、定義側の2モジュール以外に存在しない**(`rg gloss_review_hint|gloss_alignment_status`の結果: canonicalization.py 2、scaffold 2、gloss_alignment、inline runtime 1のみ) |
| Family Z stage_kp | `er026…:1161-1180` | `NG_REVIEW_REQUIRED`/`OUTER_RETRY_EXHAUSTED`/canonicalization非PASSのみSTOP。gloss FAILEDは見ない→次のtts_b1b/tts_a2へ進む |
| Audio Validation Gate | `assemble.py:~480-515` | 判定対象は`tts_generation_results.json`のsegment/KP componentの`status`(VALIDATED/HUMAN_APPROVED以外はBLOCK)。ASRで「読み上げ=canonical_text」が一致すれば、意味不整合gloss(「なになにをもとにした」)でも**VALIDATED**になる。意味整合を見るGateではない |
| 完成/ページ | (未精読) | FAILEDを参照する経路は見つからず、正常完成扱いになる |
- 結論: 現行(ii)では**2回失敗しても、最終KP+古いglossのままTTSが生成され、Gate通過し、正常完成として扱われうる**。ユーザーが欠陥②と指摘した通り。(実行確認は未実施。unit testでfallback時の戻り値は確認済み[`FIX_01.md`]が、下流素通りの実走は行っていない。コード読解で「停止させる分岐が存在しない」ことを確認。)

## 6. 再利用できる既存機構と入口
1. **Human Review Lock**(`er011_human_review_lock_01.py`): `.../<theme>/<level>/narration/<segment>.wav`のパスからsegment keyを導出(:139-153)、`audit/review_lock_state.json`(:155)にstateを保持。`check_before_generation`(:297)が`HUMAN_REVIEW_REQUIRED`のsegmentではTTS/ASRを**0 API callで拒否**、`record_outcome`(:355)が非OK結果をHUMAN_REVIEW_REQUIREDへ遷移、`approve_regenerate`(:472)で人間が解除、canonical_text(=gloss)が変わると新version扱い(:326-330)。→ KP japanese_meaning segmentへ載せれば、**TTS停止と解除手順が既存機構だけで成立**。
2. **human_review_queue.jsonl**(`er006_secondary_asr_01.py:321-332` `_log_human_review`、重複抑止`is_duplicate_queue_entry`:531): 音声セグメント(wav_path+canonical_text)単位。KP gloss不整合は**音声が未生成の段階**なので`steps`(ASR転写)を持たない。載せるにはkind付きentryの追加フィールドが必要(HR試聴ページ生成側`er006_*_build_review.py`のschema許容性は**未確認**。実装前に確認要)。
3. **Audio Validation Gate**(`assemble.py:~75-100,480-515`): segment/KP componentの非VALIDATED/HUMAN_APPROVED statusでepisode assemblyを`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`で止める。`_only_segments_skip`の`SKIPPED_NOT_SELECTED`(`er019…:~590`)に前例あり: 「生成しないsegmentは非OK statusを記録してGateにassemblyを止めさせる」。→ gloss FAILED itemのKP componentに新status文字列(例`STOPPED_GLOSS_ALIGNMENT_FAILED`)を記録すれば**Gate側のコード変更なし**で完成を止められる(Gateが非許可statusをblockedに入れる実装[assemble.py:~480-495]による)。
4. **STOPセンチネル**(`STOP`/`STOP_ALL`)とNOTICE: 運用事故(2026-10-12)対策であり、品質判定の停止には使わない(センチネルは外部停止用。混用しない)。
5. **Family Zの`FamilyZE2EStop`**(`er026…:1175`): KP stageの非PASSで後続を止める既存ガード。gloss FAILEDを同じ条件に加えるだけで停止が成立。
6. 既存Validator: 記号系は`safety.detect_prohibited_symbols`/`detect_gloss_placeholder_notation`(`audio_tts_asr_safety.py:126`、TTS直前のSTOP)、Rule7は`kc.validate_canonicalization_item`。**意味整合を検証する既存Validatorは存在しない**(新規は判定LLMのみ。ここは新設が必要)。
7. 既存retry: 外側の選定やり直し(`KEY_PHRASE_REDUNDANCY_RETRY_MAX`、Redundancy/記号NG時)。gloss FAILEDを同ループに載せる選択肢あり(DESIGN_DRAFT_01の代替案B)。

## 7. 類似の抜け道(件数・代表例・分母)
分母: `rg`対象 `er003*.py er019*.py er026*.py er062*.py er063*.py`(テスト除く)。`status="FAILED"`リテラルでの記録は**gloss module 1ファイル(5行)のみ**。表記を変えた同型の抜け道を読解で3件確認:
| # | 箇所 | 事象 | 判定 |
|---|---|---|---|
| a | `_run_key_phrases_impl`の`NG_REVIEW_REQUIRED`(Redundancy/記号QA上限到達) | `status`に記録して戻るのみ。Family Z `stage_kp`は停止(`er026…:1175`)するが、**Family X runnerは`kp["status"]`を見ず**(`er019…:408-410`は`canonicalization.status`のみ。`rg NG_REVIEW_REQUIRED er019…`は0件)、TTSへ進む可能性(読解のみ・実走未確認) | 抜け道の疑い(要確認) |
| b | `gloss_review_hint`(A'でKPが候補外へ伸びたitem、`canonicalization.py:766-769`) | 設定されるが**参照する消費側が無い**(ヒントのみ) | ヒント止まり(設計意図どおりだが、通知だけで人が見る保証が無い) |
| c | gloss FAILED(本件) | 上記5節 | 抜け道(欠陥②) |
M2 fallback(`m2_fallback_events`)は代替経路(Strategy L)の結果がGateを通る仕様で、記録して進むことが設計上正当(別物)。新規OPEN候補: 「Family XでNG_REVIEW_REQUIREDが素通りしないか」(a)。本委任では修正しない。

## 8. 【安全】現行既定ON flagの運用隔離の実態
- `GLOSS_ALIGNMENT_ENABLED = os.environ.get("EIGO_KP_GLOSS_ALIGNMENT","1") not in ("0",…)`(`gloss_alignment.py:41`、**モジュールimport時に評価**)。既定ON。
- `rg EIGO_KP_GLOSS_ALIGNMENT|GLOSS_ALIGNMENT_ENABLED|GLOSS_ALIGNMENT_FALLBACK_MODE`(py/md/json/ps1/txt): 実装とtest以外のヒットは `docs/pm/ACTIVE_TASK_KGA.md:5`(「新規量産runは`EIGO_KP_GLOSS_ALIGNMENT=0`で起動」)、`OPUS_FINDINGS_LEDGER.md:262`、`gloss_alignment_01/FIX_01.md`/`Q1_Q3_DRAFT_01.md`、OPEN-356文面のみ。**runner(er019/er026)・scaffold・起動スクリプト・README・.ps1のいずれにも`=0`の強制・既定化・警告は無い。実行環境でも`EIGO_KP_GLOSS_ALIGNMENT`は未設定(`echo`で空を実行確認)。**
- 判定: **運用隔離は口頭(ドキュメント)運用のみで、コードによる強制は無い**。Family X/Zの委任文が`=0`を明記し忘れる、またはPowerShellで別セッションを起動すれば、未承認の再整合段が量産経路で作動する(再整合段は未承認Promptでの追加LLM呼出1回(対象itemのみ)+glossが書き換わる)。
- 承認境界に抵触しない最小措置(案、本委任では実施しない):
  - **S1 起動手順への明記**: Fableが出す全ての量産run委任文の固定ブロックに`EIGO_KP_GLOSS_ALIGNMENT=0`(PowerShell: `$env:EIGO_KP_GLOSS_ALIGNMENT="0"`)を追加(文書運用のみ。既存のT-0チェッカー`check_delegation_prompt.py`にKP生成を含む委任ではこの記載を要求する警告を足す案もあるが、チェッカー変更は別判断)。
  - **S2 起動時preflight警告**: `preflight()`が有効かつ未承認の場合に`[GLOSS-ALIGN][WARN] 未承認仕様が有効です`を1行印字(コード1行追加、挙動不変)。コード変更なので委任_02以降。
  - **S3 既定値OFF化**(1行: `"1"`→`"0"`): 最も確実な隔離。ただし既定flagの変更に当たり、現行再整合ON前提で動作確認済みの既存artifactには影響しないが、**既定値変更は承認境界に触れるためFable/ユーザー判断**。本委任は実施しない。
- 結論(判定): 量産が再開される前に **S3(既定OFF)が必要**と判断する(S1/S2は人為ミスを減らすが強制ではない)。理由: 未承認・欠陥2点が確認された仕様がopt-outのみで有効になっているため。Fableへ報告しユーザー承認後に実施すること。
