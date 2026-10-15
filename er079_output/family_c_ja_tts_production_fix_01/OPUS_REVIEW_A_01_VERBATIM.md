<!-- Opus独立技術レビュー条件A 原文(逐語)。抽出元: セッションjsonl(a66c19e8...jsonl)行2667のtask-notification本文(subagent jsonl agent-a6309c381506f53d1.jsonlには最終text blockが無く、委任文指定の.outputは0byteだったため代替抽出)。
     加工は(1)通知枠の『The report follows:』以降のみ切出し (2)ハーネスが付けた各行先頭2文字のインデントを除去 (3)末尾の</agent-message>タグ除去 のみ。
     sha256(本文)=38ad5dafea55d033e074680c9dfa7854e75fca1371f6e224b6dbd3c326cc23a0 chars=7563 -->

# FAMILY-C-JA-TTS-PRODUCTION-FIX-01 Opus独立技術レビュー(条件A、read-only、JPY 0)

## 総評
**条件付き同意**です。言語経路(候補A)と言語引数の追加方式は妥当で、仕様の範囲内の不具合修正と判断します。

一方、reuse_from由来照合(Q3)は設計の中心部分に穴が2つあり、このままだと「旧音声が新原稿に紐づく」問題を完全には塞げません(FCJ-01/02)。また、正当な再利用を誤って再生成に回すリスク(偽陰性)を、実データで測る計画がありません(FCJ-04)。この3点を実装委任の必須条件に加えれば、次工程(実装委任)へ進めてよいと考えます。新たな`USER_DECISION_REQUIRED`は生じていません(Q8)。

## Q1 候補Aの採用: 同意
- `verified_strict`は言語に関わらず`p9a.VOICE_NAME`を使います(`er003_v1_repro01_main_generate.py:322`、`er003_b1_p9a_audio.py:258`)。英語narratorと同じAoedeで、Trial-11も同じ呼出をしています(`er013_family_c_episode_trial_11_memory_run.py:568-569`)。runner冒頭コメント(`er013...:36-38`)が明記する「VALIDATED済み呼出の踏襲」にそのまま該当するため、新Voiceの採用には当たりません。
- Family C節(`CURRENT_SPEC.md:1047-1124`)にJA Voiceの規定がない点は、「Trial実績を根拠とした既存値の明文化」としてSSOT追記に含めれば十分です。
- 候補Bを不採用とする判断にも同意します。tts_safe_ja、placeholder Gate、resolverを持ち込むと、Legacy Familyへの新規実装になります。

## Q2 言語引数の追加方式: 同意(補足あり)
- 既定値`"en"`により、Story(L729)とtopic_intro_en(L807)は引数が同一のまま挙動不変です。後方互換は成立しています。
- 他の経路の見落とし確認:
  - 長さ見積は`detect_duration_anomaly(..., language)`(p9a L273)で、正しい言語を渡せば自動的に直ります。
  - モデル選択(`batch_model_name`、repro01 L314)、ASR言語(L291)、Validatorの分岐(L353/L377)も、すべて`language`の値で決まります。
  - 言語を落としている経路は、Sonnetが挙げた3箇所(L389/L500/L641)と費用記録L390以外に見当たりません。
  - `get_or_run_asr`のComment呼出はja固定で正しいです。japanese_title/preview_jaはASR診断の対象外で、これは既存挙動です。
- 非narrator voiceで言語がen以外の場合のRuntimeErrorは、`budget.check_before`より前、関数の先頭に置くことを推奨します(FCJ-09)。

## Q3 reuse_from由来照合: 条件付き同意(要修正)
- **照合キー**: 「text sha256一致+wav sha256一致」の組合せ自体は妥当です。言語・voice・modelがキーに含まれない点は既存仕様どおりで、今回は対象外とします(OPEN候補)。
- **偽陽性(旧音声が残る)**: 由来照合が自己参照になっています(FCJ-01)。
  - `upgraded_from_legacy_ok:true`のmetaは、L349-353が「その時点の原稿」のshaで捏造した記録です。
  - `to_audit_entry`(L410-414)の再利用entryも、`canonical_text`に現行原稿を書きます。
  - そのため、バグ期に誤って紐づいた出力(06d `cja_attempt1/2`の出力dir等)を`reuse_from`に指定すると、metaとauditの両方が「一致」と答えてしまいます。
- **コピー手順**: `_copy_with_ok`はコピー先(dst)に既存のwavがあると上書きしません(L305)。そこへsrcのmetaだけ足す、またはmetaなしでレガシー分岐に入ると、コピー先に残っていた古いwavに新しいmetaが付きます(FCJ-02)。
- **偽陰性(正当な再利用を再生成に回す)**: 実データでの規模が未測定です(FCJ-04)。
- **AUW `er078_reuse_value_guard_01`との関係**: 責務の重複はありません。値ガードは、metaに`asr_judgement`があり、かつwav shaが一致するときだけ発火し(L340-348)、textの変化は見ません。今回のsha照合は値ガードの前段条件として補完関係にあり、ガード本体を変えない方針は正しいです。
- **レガシー分岐の維持**: ローカルresumeに限定すれば許容できます。ただしFCJ-03の手当てが前提です。

## Q4 長さ見積と、JA化後に予見される失敗: 長さは問題なし、別のリスクあり
- **長さ見積**: `estimate_max_reasonable_duration_seconds`(`er003_audio_tts_asr_safety.py:177-186`)の計算で説明がつきます。
  - en扱いだと、空白のない日本語文は1語と数えられ、1×1.5+4.0=**5.50秒**になります(06dの値と完全に一致)。
  - jaなら`文字数×1.2+3.0`で、80〜110字では99〜135秒です。16.9秒の音声は十分に収まります。見積の妥当性は問題ありません。
- **予見リスク1(記号Gate)**: Layer-4の記号Gate(repro01 L283、`safety.py:987-995,1026`)は言語を問わず、括弧`()（）[]`、`/`、`〜`、`…`、`:;：；`があるとSTOPします。候補Aはtts_safe_jaの正規化を通しません。japanese_title_textとpreview.txtは未検証のため、有料実行の前に0円で事前検査すべきです(FCJ-06)。
- **予見リスク2(ASR長さ)**: `length_ok`の上限は`len(text)+15`文字です(repro01 L292)。ASRが漢字を仮名で返すと超過しうるため、監視項目とします。Trial-11/12では成立していました。

## Q5 retry/fallback/regeneration/HR Lock/試聴リストとの整合: 概ね同意、訂正1点
- 投委案の5-4節は「通算3回目cool-down」が適用されると書いていますが、誤りです。cool-downは`cooldown_total_budget`が渡された場合だけ動き(repro01 L329)、Family Cは渡していません。記述を訂正するだけにとどめ、追加はしないでください(追加は新規実装になります。FCJ-05)。
- HR Lock: Family Cは`total_slots`を渡さないため、この呼出の最終attemptでNGならHR投入になります(L385-386)。外側にfallbackがないので、これで整合しています。
- `--only-segments comment_N`の扱い: 原稿再生成の判定(L592)が真になるとComment 3本すべてのLLM文面が再生成されるため、TTSも3本とも再生成になります(sha照合で正しく処理されます)。「1 clipだけ再生成」という期待は、文面を手で編集した場合にしか成立しません(FCJ-07)。

## Q6 test計画・evidence計画: 条件付き同意(追加2件、修正1件)
- **追加1**: 0円の「reuse plan dry-run」。全`article_config.json`の`reuse_from`先について、clipごとに「meta正規/legacy-upgraded/metaなし、audit上の`reused`有無、新ルールでの判定(再利用か再生成か)」を一覧化します。これで偽陰性の規模を実データで測ります。
- **追加2**: Run C'。Memory A2を`reuse_from`に指定し、空の出力dirで実行します。TTS関数を「呼ばれたら例外を出す」形に差し替えて走らせれば、偽陰性があれば0円のまま検出できます。Run Cはローカルresumeしか通らないため、新しいガードの回帰を検証できません。
- **追加3**: β項目にFCJ-01/02/03用を3件追加します(legacy-upgraded metaと`reused` auditからは再利用しない/既存dstを確実に置き換える/TTS失敗後に`.ok`が残らない)。
- **修正**: Run Bは、文面を編集する場所(reuse_src側か出力dir側か)を明記し、成果物を「test fixture(Comment Contract未経由)」と表示して、納品物扱いにしないでください。
- 省けるもの: β10(既存静的test)は既存suiteの実行に含まれるため、独立項目は不要です。

## Q7 Legacy Family Cへの例外記録: 同意(条件付き)
DECISION_LOGに、次の3点を併記してください。
- ユーザー指示B(`docs/pm/delegation_log/2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md:19-57`)の位置。
- 範囲限定: tts_safe_ja、cool-down、N1の再生成対象拡張を持ち込まないこと。
- `CURRENT_SPEC.md:1556-1558`の条件1・3は引き続き有効であること。

Statusは、今回の是正単位に限定してください(Family C全体のStatusを格上げしない。FCJ-10)。

## Q8 新たなUSER_DECISION_REQUIRED: なし
条件付きで発生しうるものが2つあります。
- (a) FCJ-06の事前検査でJA文面に禁止記号が見つかった場合: 文面の修正はComment内容仕様に触れるため、STOP対象です。
- (b) FCJ-04のdry-runで、ユーザーが試聴承認したepisodeの音声が新ルールで再生成される場合: 承認済み音声を差し替えることになるため、Fableを経由して判断を仰ぐ対象です。

## 指摘一覧
- **FCJ-01 MAJOR**: 由来照合が自己参照で、偽陽性が残ります。
  - 根拠: L349-353がmetaを捏造し、`to_audit_entry` L411-414が現行原稿を記録するため。
  - 代替案: `reuse_from`では、`upgraded_from_legacy_ok`のmetaを由来の証拠として扱わない。audit経由は`reused`が偽(新規生成の記録)のentryだけ受け入れる。それ以外は再生成する。06d `cja_attempt*`の出力dirは汚染資産として隔離・記録する。
- **FCJ-02 MAJOR**: 受理した経路でのコピー方法。
  - 代替案: 照合を通ったら、コピー先のwav/.ok/metaを削除してからsrcのwavをコピーし、`{tts_text_sha256, wav_sha256(=src実測), reuse_from_source, provenance_basis}`を照合関数自身が書き込む。`_copy_with_ok`の「上書きしない」挙動やレガシー分岐には乗せない。
- **FCJ-03 MINOR**: TTS失敗時に、古い`.ok`(metaなし)と最後の失敗attemptのwavが同居すると、次のresumeで無条件に再利用されます(L349。p9aはattemptごとにout_pathへ書き込む、L277)。
  - 代替案: 新規TTSを呼ぶ前に、out_pathの`.ok`と`.ok.meta.json`を削除する。
- **FCJ-04 MAJOR**: 偽陰性の規模を実データで測っていません。Q6の追加1・2で対応してください。
- **FCJ-05 MINOR**: 投委案5-4節のcool-down適用の記述は誤りです(repro01 L329)。記述の訂正のみとします。
- **FCJ-06 MINOR**: 記号Gateの0円事前検査を、Run Aの前に必須化してください。
- **FCJ-07 MINOR**: Run Bの条件明記と、`--only-segments`では3本とも再生成になる点の明記。
- **FCJ-08 MINOR**: 新規コード(コメント・関数名を含む)に`asr_verified`、`evaluate_attempt*`、`classify_*asr_match`、`unified_judge`を書かないこと(`er078_asr_unified_wiring_static_audit_01.py:479,482`)。
- **FCJ-09 MINOR**: 非en言語ガードを関数の先頭に置き、`run_simple_narrator_asset`が`language`を渡すことのtestを追加。
- **FCJ-10 MINOR**: Family Cの記載(`CURRENT_SPEC.md:1119`「APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE」)は格上げしないこと。古くなる記述(`RUNTIME_EVIDENCE_06.md:370`の「C runnerから統一ASR判定に到達しない」)は、Dangling Reference Checkで更新対象にすること。
- **FCJ-11 MINOR**: runner内部の予算見積はclipあたり1回分(0.9円)しか数えず、実際は1 clipで最大3 attemptです。実費の上限を守るのはharness側のmeterで、超過は最大でも1 clip分(約1.4円)です。hard_stopの余裕として記録してください。metaに言語・voice・modelを持たない点はOPEN候補とします。

## 確認した証拠(file:line)
- `C:\Users\tensh\eigo-radio\er013_family_c_production_runner_01.py`: 28-39, 303-312, 325-357, 360-371, 374-407, 410-426, 484-504, 592-648, 672-695, 702-736, 768-773, 807-832
- `C:\Users\tensh\eigo-radio\er003_v1_repro01_main_generate.py`: 197-266, 283-292, 314-335, 346-390, 423, 459-478
- `C:\Users\tensh\eigo-radio\er003_b1_p9a_audio.py`: 227-277
- `C:\Users\tensh\eigo-radio\er003_audio_tts_asr_safety.py`: 171-203, 987-995, 1026-1083
- `C:\Users\tensh\eigo-radio\er013_family_c_episode_trial_11_memory_run.py`: 561-572
- `C:\Users\tensh\eigo-radio\er078_reuse_value_guard_01.py`: 1-71
- `C:\Users\tensh\eigo-radio\er078_asr_unified_wiring_static_audit_01.py`: 473-482
- `C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\RUNTIME_EVIDENCE_06.md`: 320, 339, 370, 372
- `C:\Users\tensh\eigo-radio\CURRENT_SPEC.md`: 1047-1137, 1553-1560
- `C:\Users\tensh\eigo-radio\OPEN_ITEMS.md`: 881(OPEN-372)
- `C:\Users\tensh\eigo-radio\er079_output\family_c_ja_tts_production_fix_01\INVESTIGATION_01.md`(全文)
- `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md`: 19-57

**入力範囲の補足**: 指定されたパス`docs/pm/delegation_log/2026-10-16_AUW-FAMILY-C-DQI-USER-INSTRUCTION.md`は存在しませんでした。B節は`2026-10-16_FAMILY-C-JA-TTS-PRODUCTION-FIX-01_01.md`の19-57行から読みました。
