# RUNTIME_EVIDENCE_01(JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A。**実走の出力を機械的に貼付**。生成: `tools/make_runtime_evidence_md_01.py`)

## 0. 実験構成(何が本物で、何が代替か)
- **本物**: Production判定の実コード(`n3_tts.generate_a2_japanese_with_reading_safety` -> `generate_narration_snippet_verified_strict` -> `er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail` -> 新module `er078_ja_v2beta_01`、`unified_judge`無改変)、実scope(`er109_xz_scope_01.run_scope`: Xは`generate_family_x_a2_segments`、Yは`generate_y_a2_segments`、Zは`run_tts_stage`が自ら設定)、実run単位Secondary hook(`with_secondary_run`)、実Family完了hook(`write_listening_list_safe(completion_label=...)`)、実ASR(OpenAI `gpt-4o-mini-transcribe` + Azure Speech `azure-speech-stt`、Production routing `er006_asr_provider_routing_01`)。
- **代替(唯一)**: TTS。`er003_b1_p9a_audio.generate_narration_snippet`だけを、保存済みの実wav(月タイトル6本=`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_{ms_03,reselect_01}/a2/narration/attempts/japanese_title_attempt{1,2,3}_*.wav`)を`out_path`へコピーする関数に差し替え(Gemini TTS 0円・声/モデル不変の既存wav再利用)。
- **書込先**: すべて一時dir(`%TEMP%/ja_v2beta_rt_*`)。Production results・Master Audio Store・承認記録・Production監査ログ/HR queueへは書かない(`test_state_isolation_01`でattempt_history/HR queueをtmpへ退避。Y fixtureは既存Y run `er121_output/family_y_production_01/redelivery_fee/run_style_fix_01`のjson 5本のみを一時dirへコピー)。
- 全有料phase前に`tools/stop_scope_check_01.py`をrc=0で確認(`stop_check_*_paid.json`)。費用はCOST_01.md。
- **制約(正直に)**: Y/Z familyは記事全体のfixture無しで`japanese_title`1 Sectionのみを選択して実走(`_ONLY_SEGMENTS`/`only_clips`)。Familyの組立・試聴ページ全体の生成は未実走(節のrender関数は実際の呼出し=同じ`render_html_section(load_listening_list(...))`/`_y_pww_aux_html`を実行)。

## 1. E0(API 0): 保存済み転写を実Production経路(X scope)に注入 -> 月6本 = 4 PASS_W / 2 HR
Primary=各attempt jsonの`asr_text`、Secondary(Azure)=EVAL_UNIFIED_03 §1aの記録。OpenAI/Azure呼出はstub、ネットワークはsocket guardで遮断。

| draw | verdict | reason_code | rescue_basis | warnings | judge_rule_version | 期待(委任文) |
|---|---|---|---|---|---|---|
| e0_ms_03_a1 | HR | p1_value_diff | None |  | ja_v2beta_r1off_01 | HR |
| e0_ms_03_a2 | PASS_W | primary_pass | v2 | JA_NEWLAYER_PRON_EQUIVALENT | ja_v2beta_r1off_01 | PASS_W |
| e0_ms_03_a3 | PASS_W | ja_beta_composite | beta | JA_COMPOSITE_VALUE_FROM_SECONDARY,JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED,JA_PRON_EQUIVALENT,JA_COMPOSITE_SECONDARY_READING_CONFLICT,JA_COMPOSITE_LISTEN_ADVISED,JA_NEWLAYER_BETA_COMPOSITE | ja_v2beta_r1off_01 | PASS_W |
| e0_reselect_a1 | PASS_W | primary_pass | v2 | JA_NEWLAYER_PRON_EQUIVALENT | ja_v2beta_r1off_01 | PASS_W |
| e0_reselect_a2 | PASS_W | primary_pass | v2 | JA_NEWLAYER_PRON_EQUIVALENT | ja_v2beta_r1off_01 | PASS_W |
| e0_reselect_a3 | HR | secondary_not_accepted | None |  | ja_v2beta_r1off_01 | HR |

scope外(None=A/B/C相当)で同じ6転写を判定: 新キー(`ja_v2beta`/`verdict`/`rescue_basis`/`judge_rule_version`)は**全行で無し**、判定は従来(L0)のまま。

| draw | state(従来) | reason_code | 新キーの有無 |
|---|---|---|---|
| e5_none_ms_03_a1 | NG_PROTECTED | p1_value_diff | {'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False} |
| e5_none_ms_03_a2 | NG_BOTH | secondary_not_accepted | {'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False} |
| e5_none_ms_03_a3 | NG_PROTECTED | p1_value_diff | {'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False} |
| e5_none_reselect_a1 | NG_BOTH | secondary_not_accepted | {'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False} |
| e5_none_reselect_a2 | NG_BOTH | secondary_not_accepted | {'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False} |
| e5_none_reselect_a3 | NG_BOTH | secondary_not_accepted | {'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False} |

## 2. E1(有料・実ASR): 同じ6本の実wavを実ASRで判定(X scope、1 attempt、3 draw)
**重要な観測**: OpenAI `gpt-4o-mini-transcribe`のPrimary転写は、**同一wavでも呼出しごとに変わる**(下表)。判定は転写に対して決定的(E0・単体testで固定)だが、wav -> verdictは転写の揺らぎで変わる。保存済み転写での4/6は『その転写がその形だった場合』の値であり、同じwavを新たに再ASRすると2〜3/6になった。これは新方式の欠陥ではなく、Primary ASRの非決定性(従来から存在)の露出。ASR再試行は承認済み仕様(UDR #204)で不採用のため、本IDでは是正しない(報告のみ)。

### draw 1 (e1)
| wav | verdict | reason_code | rescue_basis | Primary転写 | Secondary転写 | 費用(audit) |
|---|---|---|---|---|---|---|
| ms_03 a1 | HR | p1_value_diff | None | 月野詩は8000900本超え。その奥に潜む岩の上着の秘密。 | None | 0.0 |
| ms_03 a2 | PASS_W | secondary_confirmed | v2 | 月の芝は八千九百本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本超。その奥に潜む岩の上着の秘密。 | 0.2667 |
| ms_03 a3 | HR | secondary_not_accepted | None | 好きの氏は八千九百本超。その奥に潜む岩の上着の秘密。 | 杉野氏は8900本超。その奥に潜む岩の上着の秘密。 | 0.3111 |
| reselect a1 | PASS_W | ja_beta_composite | beta | 月野氏は8000900本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。 | 0.3111 |
| reselect a2 | PASS_W | primary_pass | v2 | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密。 | None | 0.0 |
| reselect a3 | HR | secondary_not_accepted | None | この市は、八千九百本超。その奥に潜む岩の上着の秘密。 | Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | 0.3556 |

### draw 2 (e1b)
| wav | verdict | reason_code | rescue_basis | Primary転写 | Secondary転写 | 費用(audit) |
|---|---|---|---|---|---|---|
| ms_03 a1 | HR | secondary_not_accepted | None | 月の詩は8,900本超え。その奥に潜む岩の上着の秘密。 | 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | 0.3111 |
| ms_03 a2 | HR | p1_value_diff | None | 月の島は千九百本超、その奥に潜む岩の上着の秘密。 | None | 0.0 |
| ms_03 a3 | HR | p2_exclusion:A4_C2_HOMOGRAPH | None | 月の詩は八千九百本調。その奥に潜む岩の上着の秘密。 | None | 0.0 |
| reselect a1 | PASS_W | primary_pass | v2 | 月野氏は八千九百本超。その奥に潜む岩の上着の秘密 | None | 0.0 |
| reselect a2 | PASS_W | primary_pass | v2 | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 | None | 0.0 |
| reselect a3 | HR | p1_value_diff | None | 月の死は、は1900本超。その奥に潜む岩の上着の秘密。 | None | 0.0 |

### draw 3 (e1c)
| wav | verdict | reason_code | rescue_basis | Primary転写 | Secondary転写 | 費用(audit) |
|---|---|---|---|---|---|---|
| ms_03 a1 | HR | secondary_not_accepted | None | 月野詩は八千九百本超え。その奥に潜む岩の上着の秘密。 | 月野市は8900本越え。その奥に潜む岩の上着の秘密。 | 0.3111 |
| ms_03 a2 | HR | p1_value_diff | None | 月の島は千九百本超。その奥に潜む岩の上着の秘密。 | None | 0.0 |
| ms_03 a3 | PASS_W | primary_pass | v2 | 月の氏は八千九百本超。その奥に潜む岩の上着の秘密。 | None | 0.0 |
| reselect a1 | HR | p1_value_diff | None | スキノ氏は8000900本超。その奥に潜む岩の上着の秘密。 | None | 0.0 |
| reselect a2 | PASS_W | ja_beta_composite | beta | 月野氏は8000900本超。その奥に潜む岩の上着の秘密。 | 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。 | 0.3111 |
| reselect a3 | HR | secondary_not_accepted | None | スギノシは八千九百本超、その奥に潜む岩の上着の秘密 | Sukino氏は8900本超。その奥に潜む岩の上着の秘密。 | 0.3556 |

PASS_W件数(3 draw): [3, 2, 2] / 6。HRは従来どおりの根拠(`p1_value_diff`/`secondary_not_accepted`/`p2_exclusion`)で、新層による誤った救済は無い。

model_id / routing(1件分。全rowの`asr_judgement.r5.models`に同形で記録):
```json
{
 "primary": {
  "model": "gpt-4o-mini-transcribe",
  "provider": "openai_asr"
 },
 "secondary": {
  "model_id": "azure-speech-stt",
  "provider": "azure"
 }
}
```

## 3. E2(有料・実ASR): X / Y / Z それぞれ family関数で 1 Section(`japanese_title`)
音声=`reselect a2`(E1の3 drawすべてでPASS_Wになった音声。ただし実ASRの誤転写で落ちる draw もある=3-F)。Family関数がscopeを自ら設定し、生成+Secondary hook+完了hookまで実走。本表・§4は最終run(run4。fallback経路も偽TTS化後)。

| Family | 実走した関数 | status | verdict | reason_code | rescue_basis | judge_rule_version | model_id(primary / secondary) | 費用 audit vs RunState |
|---|---|---|---|---|---|---|---|---|
| X | x_family_generate_family_x_a2_segments | OK | PASS_W | ja_beta_composite | beta | ja_v2beta_r1off_01 | gpt-4o-mini-transcribe / azure-speech-stt | audit 0.3111 = RunState 0.3111 (Secondary呼出 1) |
| Y | y_family_generate_y_a2_segments | OK | PASS_W | ja_beta_composite | beta | ja_v2beta_r1off_01 | gpt-4o-mini-transcribe / azure-speech-stt | audit 0.3111 = RunState 0.3111 (Secondary呼出 1) |
| Z | z_family_run_tts_stage | OK | PASS_W | primary_pass | v2 | ja_v2beta_r1off_01 | gpt-4o-mini-transcribe / None | audit 0.0 = RunState 0.0 (Secondary呼出 0) |

**β追加Azure費用の整合(M-2)**: Zの実走ではβが発火(`rescue_basis=v2`)。監査record `cost`={"azure_calls": 0, "azure_seconds": null, "est_jpy": 0.0} は、run単位`RunState.est_jpy_total`(0.0)・`secondary_calls`(0)と一致。raw usage log(`raw_usage_log_runtime_evidence_e2_01.jsonl`)にもAzure 1件(`azure_stt_strict_scg`)。

### 3-X. Family X: 新方式の記録(抜粋)
```json
{
 "state": "PASS_WITH_WARNING",
 "verdict": "PASS_W",
 "reason_code": "ja_beta_composite",
 "rescue_basis": "beta",
 "rescue_reason_ja": "数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000九百(digit+kanji:8000+九百)。Primaryの読みは助詞は→わ等の発音形でのみ一致。",
 "judge_rule_version": "ja_v2beta_r1off_01",
 "warnings": [
  "JA_COMPOSITE_VALUE_FROM_SECONDARY",
  "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED",
  "JA_PRON_EQUIVALENT",
  "JA_COMPOSITE_LISTEN_ADVISED",
  "JA_NEWLAYER_BETA_COMPOSITE"
 ],
 "ja_v2beta.layers": [
  {
   "cause": "value=secondary/reading=primary",
   "effective": true,
   "layer": "beta",
   "side": "primary+secondary"
  }
 ],
 "ja_v2beta.error": null,
 "primary_text": "月の詩は8000九百本超。その奥に潜む岩の上着の秘密。",
 "secondary_text": "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。",
 "segment_statuses": {
  "comment_1": "SKIPPED_NOT_SELECTED",
  "comment_2": "SKIPPED_NOT_SELECTED",
  "comment_3": "SKIPPED_NOT_SELECTED",
  "comment_4": "SKIPPED_NOT_SELECTED",
  "full_story_part1": "SKIPPED_NOT_SELECTED",
  "full_story_part2": "SKIPPED_NOT_SELECTED",
  "full_story_part3": "SKIPPED_NOT_SELECTED",
  "in_one_line": "SKIPPED_NOT_SELECTED",
  "japanese_title": "OK",
  "preview": "SKIPPED_NOT_SELECTED",
  "topic_intro": "SKIPPED_NOT_SELECTED"
 }
}
```

### 3-Y. Family Y: 新方式の記録(抜粋)
```json
{
 "state": "PASS_WITH_WARNING",
 "verdict": "PASS_W",
 "reason_code": "ja_beta_composite",
 "rescue_basis": "beta",
 "rescue_reason_ja": "数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000900(digit_split:8000+900)。Primaryの読みは助詞は→わ等の発音形でのみ一致。",
 "judge_rule_version": "ja_v2beta_r1off_01",
 "warnings": [
  "JA_COMPOSITE_VALUE_FROM_SECONDARY",
  "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED",
  "JA_PRON_EQUIVALENT",
  "JA_COMPOSITE_LISTEN_ADVISED",
  "JA_NEWLAYER_BETA_COMPOSITE"
 ],
 "ja_v2beta.layers": [
  {
   "cause": "value=secondary/reading=primary",
   "effective": true,
   "layer": "beta",
   "side": "primary+secondary"
  }
 ],
 "ja_v2beta.error": null,
 "primary_text": "月の詩は8000900本超。その奥に潜む岩の上着の秘密",
 "secondary_text": "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。",
 "segment_statuses": {
  "comment_1": "SKIPPED_NOT_SELECTED",
  "comment_2": "SKIPPED_NOT_SELECTED",
  "comment_3": "SKIPPED_NOT_SELECTED",
  "japanese_title": "OK",
  "preview": "SKIPPED_NOT_SELECTED",
  "topic_intro": "SKIPPED_NOT_SELECTED",
  "y_closing": "SKIPPED_NOT_SELECTED",
  "y_intro_1": "SKIPPED_NOT_SELECTED",
  "y_intro_2": "SKIPPED_NOT_SELECTED",
  "y_intro_3": "SKIPPED_NOT_SELECTED",
  "y_lead": "SKIPPED_NOT_SELECTED",
  "y_voice_1": "SKIPPED_NOT_SELECTED",
  "y_voice_2": "SKIPPED_NOT_SELECTED",
  "y_voice_3": "SKIPPED_NOT_SELECTED"
 }
}
```

### 3-Z. Family Z: 新方式の記録(抜粋)
```json
{
 "state": "PASS_WITH_WARNING",
 "verdict": "PASS_W",
 "reason_code": "primary_pass",
 "rescue_basis": "v2",
 "rescue_reason_ja": "v2読み規則: 値の表記差(三十人=30人、桁区切りの有無等)と発音形の一致のみ(原因=A3_value+A2_particle)。読み・値は原稿と同等と判定。",
 "judge_rule_version": "ja_v2beta_r1off_01",
 "warnings": [
  "JA_NEWLAYER_PRON_EQUIVALENT"
 ],
 "ja_v2beta.layers": [
  {
   "cause": "A3_value+A2_particle",
   "effective": true,
   "layer": "v2_pron",
   "side": "primary"
  }
 ],
 "ja_v2beta.error": null,
 "primary_text": "月野氏は8,900本超。その奥に潜む岩の上着の秘密。",
 "secondary_text": null,
 "segment_statuses": {
  "japanese_title": "OK"
 }
}
```

### 3-F. 失敗経路の最終成果物(同じ音声・同じ実Production経路で、実ASRが3回とも誤転写した draw。`runtime_evidence_e2_stopped_run3_01.out.json`)
実ASR(OpenAI mini)は同一wav(`reselect a2`)を『発線900本超』『8000級本超』と誤転写し、標準2回が `NG_PROTECTED/p1_value_diff`(従来どおりの根拠・新層は救済せず)。この draw では minimal-instruction fallback の3回目が**ハーネスの不備**で実TTSへ出ようとして通信監視に止められた(= 3回目のASRまで到達せず STOPPED。実TTSは呼ばれていない・費用0)。run4でfallback経路も偽TTSにし、全familyでPASS_Wを得ている。失敗経路としての最終成果物は次のとおり: segment status=STOPPED・HR Lock登録1件・完了ブロックは新方式PASS_W『0件』と『要Human Review: japanese_title』を明示・組立/納品候補は従来どおりGateで止まる(PASS_Wではないため)。

- Family Y: segment status=`STOPPED`
```
【日本語ASR PASS_W(新方式)】Family Y a2(Standard)
  新方式(v2/β)のPASS_W: 0件 (β 0 / v2 0 / Secondary読み相違あり 0 / 断片説明(garble) 0) ※既存のPASS_WITH_WARNING全体: 0件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。
  0件(該当なし)
  新方式の稼働状況: JA判定record 2件 / 有効 2 / 定数OFF 0 / E3E4ブロック 0 / **無効化(エラーで従来判定へ戻った)件数 0**
  要Human Review(HR Lock登録 1件 / JA HR queue行 0件): japanese_title
```
- Family Z: segment status=`STOPPED`
```
【日本語ASR PASS_W(新方式)】Family Z a2
  新方式(v2/β)のPASS_W: 0件 (β 0 / v2 0 / Secondary読み相違あり 0 / 断片説明(garble) 0) ※既存のPASS_WITH_WARNING全体: 0件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。
  0件(該当なし)
  新方式の稼働状況: JA判定record 0件 / 有効 0 / 定数OFF 0 / E3E4ブロック 0 / **無効化(エラーで従来判定へ戻った)件数 0**
  要Human Review(HR Lock登録 1件 / JA HR queue行 0件): japanese_title
```
(注: Zの失敗entryは `asr_judgement`/`attempts_log` に判定recordを持たない形式のため、完了ブロックの『JA判定record 0件』はZ失敗segmentでは判定回数を反映しない[既存のZ失敗entry形式の制約。HR Lock登録とSTOPPEDは正しく報告される]。)

## 4. 最終制作報告の掲載例(実走から生成。完了ブロック=標準出力、JSON=`audit/pass_with_warning_listening_list.json`、試聴ページ節)
### 4-X-1. 完了ブロック(標準出力。Family X a2(Standard)。固有名詞アラーム報告は省略=同JSONに全文)
```
【日本語ASR PASS_W(新方式)】Family X a2(Standard)
  新方式(v2/β)のPASS_W: 1件 (β 1 / v2 0 / Secondary読み相違あり 0 / 断片説明(garble) 1) ※既存のPASS_WITH_WARNING全体: 1件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。
  1. [beta/断片説明(garble)] japanese_title | 音声=C:\Users\tensh\AppData\Local\Temp\ja_v2beta_rt_g8kmfzps\x_theme/a2/narration/japanese_title.wav sha=dd3dbc1e6304
       原稿: 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密
       Primary: 月の詩は8000九百本超。その奥に潜む岩の上着の秘密。  / Secondary: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。
       発生理由: 数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000九百(digit+kanji:8000+九百)。Primaryの読みは助詞は→わ等の発音形でのみ一致。
       警告: JA_COMPOSITE_VALUE_FROM_SECONDARY, JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED, JA_PRON_EQUIVALENT, JA_COMPOSITE_LISTEN_ADVISED, JA_NEWLAYER_BETA_COMPOSITE
  新方式の稼働状況: JA判定record 4件 / 有効 4 / 定数OFF 0 / E3E4ブロック 0 / **無効化(エラーで従来判定へ戻った)件数 0**
  要Human Review(HR Lock登録 0件 / JA HR queue行 0件): なし
```
### 4-X-2. JSON(`pass_with_warning_listening_list.json`の`entries[0]`と`ja_v2beta_summary`)
```json
{
 "count": 1,
 "entries[0]": {
  "adopted_sha256": "dd3dbc1e630450305b6613e6449395e4ae8ad3885e9c49d9dba8d0c3b3548e19",
  "audio_path": "<一時dir>/japanese_title.wav",
  "canonical_text": "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密",
  "entry_key": "segments/japanese_title",
  "inherited": false,
  "judge_rule_version": "ja_v2beta_r1off_01",
  "lang": "ja",
  "level": "",
  "listen_advised": true,
  "original_wav": "",
  "primary_text": "月の詩は8000九百本超。その奥に潜む岩の上着の秘密。",
  "reason": "ja_beta_composite",
  "rescue_basis": "beta",
  "rescue_reason_ja": "数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000九百(digit+kanji:8000+九百)。Primaryの読みは助詞は→わ等の発音形でのみ一致。",
  "role": "japanese_title",
  "script_version": "v0",
  "secondary_reading_conflict": false,
  "secondary_text": "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。",
  "segment_id": "japanese_title",
  "slot": 3,
  "value_guard_kind_primary": "DIFF",
  "value_guard_kind_secondary": "EQUAL",
  "verdict": "PASS_W",
  "warning_labels": [
   "JA_COMPOSITE_VALUE_FROM_SECONDARY",
   "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED",
   "JA_PRON_EQUIVALENT",
   "JA_COMPOSITE_LISTEN_ADVISED",
   "JA_NEWLAYER_BETA_COMPOSITE"
  ],
  "weak_rank": 1
 },
 "ja_v2beta_summary": {
  "count_by_rescue_basis": {
   "beta": 1
  },
  "garble_explained_count": 1,
  "health": {
   "active": 4,
   "attempt_records": 4,
   "blocked_by_e3_e4": 0,
   "disabled_by_constant": 0,
   "error_samples": [],
   "errors": 0
  },
  "new_method_total": 1,
  "pass_w_total": 1,
  "secondary_reading_conflict_count": 0
 }
}
```
### 4-X-3. 試聴ページ節HTML(`render_html_section`の出力)
```html
<section id="pass-with-warning-listening-list"><h2>事後試聴リスト(PASS_WITH_WARNING) WARNING音声 試聴リスト(自動採用・事後確認用)</h2>
<p>1件。公開をブロックしません。事後に試聴して確認してください。</p><p>『新方式』欄が入った行は日本語ASR v2読み規則/B-light βで救済した音声です(証拠の弱い順に先頭表示)。試聴は推奨(任意)であり、制作・組立・納品候補作成は止めません。</p><table border="1"><tr><th>segment</th><th>role</th><th>warning</th><th>原稿</th><th>Primary転写</th><th>Secondary転写</th><th>値ガードkind</th><th>理由</th><th>新方式</th><th>救済理由</th><th>音声</th></tr>
<tr><td>japanese_title</td><td>japanese_title</td><td>JA_COMPOSITE_VALUE_FROM_SECONDARY, JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED, JA_PRON_EQUIVALENT, JA_COMPOSITE_LISTEN_ADVISED, JA_NEWLAYER_BETA_COMPOSITE</td><td>月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密</td><td>月の詩は8000九百本超。その奥に潜む岩の上着の秘密。</td><td>月の詩は8900本ちょうその奥に潜む岩の上着の秘密。</td><td>DIFF/EQUAL</td><td>ja_beta_composite</td><td>beta</td><td>数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000九百(digit+kanji:8000+九百)。Primaryの読みは助詞は→わ等の発音形でのみ一致。</td><td><audio controls preload="none" src="<音声path>"></audio> <a href="C:\Users\tensh\AppData\Local\Temp\ja_v2beta_rt_g8kmfzps\x_theme/a2/narration/japanese_title.wav">mp3</a></td></tr>
</table></section>
```

### 4-Y-1. 完了ブロック(標準出力。Family Y a2(Standard)。固有名詞アラーム報告は省略=同JSONに全文)
```
【日本語ASR PASS_W(新方式)】Family Y a2(Standard)
  新方式(v2/β)のPASS_W: 1件 (β 1 / v2 0 / Secondary読み相違あり 0 / 断片説明(garble) 1) ※既存のPASS_WITH_WARNING全体: 1件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。
  1. [beta/断片説明(garble)] japanese_title | 音声=C:\Users\tensh\AppData\Local\Temp\ja_v2beta_rt_g8kmfzps\y_theme/a2/narration/japanese_title.wav sha=dd3dbc1e6304
       原稿: 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密
       Primary: 月の詩は8000900本超。その奥に潜む岩の上着の秘密  / Secondary: 月の詩は8900本ちょうその奥に潜む岩の上着の秘密。
       発生理由: 数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000900(digit_split:8000+900)。Primaryの読みは助詞は→わ等の発音形でのみ一致。
       警告: JA_COMPOSITE_VALUE_FROM_SECONDARY, JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED, JA_PRON_EQUIVALENT, JA_COMPOSITE_LISTEN_ADVISED, JA_NEWLAYER_BETA_COMPOSITE
  新方式の稼働状況: JA判定record 1件 / 有効 1 / 定数OFF 0 / E3E4ブロック 0 / **無効化(エラーで従来判定へ戻った)件数 0**
  要Human Review(HR Lock登録 0件 / JA HR queue行 0件): なし
```
### 4-Y-2. JSON(`pass_with_warning_listening_list.json`の`entries[0]`と`ja_v2beta_summary`)
```json
{
 "count": 1,
 "entries[0]": {
  "adopted_sha256": "dd3dbc1e630450305b6613e6449395e4ae8ad3885e9c49d9dba8d0c3b3548e19",
  "audio_path": "<一時dir>/japanese_title.wav",
  "canonical_text": "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密",
  "entry_key": "segments/japanese_title",
  "inherited": false,
  "judge_rule_version": "ja_v2beta_r1off_01",
  "lang": "ja",
  "level": "",
  "listen_advised": true,
  "original_wav": "",
  "primary_text": "月の詩は8000900本超。その奥に潜む岩の上着の秘密",
  "reason": "ja_beta_composite",
  "rescue_basis": "beta",
  "rescue_reason_ja": "数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000900(digit_split:8000+900)。Primaryの読みは助詞は→わ等の発音形でのみ一致。",
  "role": "japanese_title",
  "script_version": "v0",
  "secondary_reading_conflict": false,
  "secondary_text": "月の詩は8900本ちょうその奥に潜む岩の上着の秘密。",
  "segment_id": "japanese_title",
  "slot": 1,
  "value_guard_kind_primary": "DIFF",
  "value_guard_kind_secondary": "EQUAL",
  "verdict": "PASS_W",
  "warning_labels": [
   "JA_COMPOSITE_VALUE_FROM_SECONDARY",
   "JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED",
   "JA_PRON_EQUIVALENT",
   "JA_COMPOSITE_LISTEN_ADVISED",
   "JA_NEWLAYER_BETA_COMPOSITE"
  ],
  "weak_rank": 1
 },
 "ja_v2beta_summary": {
  "count_by_rescue_basis": {
   "beta": 1
  },
  "garble_explained_count": 1,
  "health": {
   "active": 1,
   "attempt_records": 1,
   "blocked_by_e3_e4": 0,
   "disabled_by_constant": 0,
   "error_samples": [],
   "errors": 0
  },
  "new_method_total": 1,
  "pass_w_total": 1,
  "secondary_reading_conflict_count": 0
 }
}
```
### 4-Y-3. 試聴ページ節HTML(`render_html_section`の出力)(dev試聴ページ。公開(public)ページには出ない=下記)
```html
<h3>Standard</h3><section id="pass-with-warning-listening-list"><h2>事後試聴リスト(PASS_WITH_WARNING) WARNING音声 試聴リスト(自動採用・事後確認用)</h2>
<p>1件。公開をブロックしません。事後に試聴して確認してください。</p><p>『新方式』欄が入った行は日本語ASR v2読み規則/B-light βで救済した音声です(証拠の弱い順に先頭表示)。試聴は推奨(任意)であり、制作・組立・納品候補作成は止めません。</p><table border="1"><tr><th>segment</th><th>role</th><th>warning</th><th>原稿</th><th>Primary転写</th><th>Secondary転写</th><th>値ガードkind</th><th>理由</th><th>新方式</th><th>救済理由</th><th>音声</th></tr>
<tr><td>japanese_title</td><td>japanese_title</td><td>JA_COMPOSITE_VALUE_FROM_SECONDARY, JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED, JA_PRON_EQUIVALENT, JA_COMPOSITE_LISTEN_ADVISED, JA_NEWLAYER_BETA_COMPOSITE</td><td>月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密</td><td>月の詩は8000900本超。その奥に潜む岩の上着の秘密</td><td>月の詩は8900本ちょうその奥に潜む岩の上着の秘密。</td><td>DIFF/EQUAL</td><td>ja_beta_composite</td><td>beta</td><td>数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000900(digit_split:8000+900)。Primaryの読みは助詞は→わ等の発音形でのみ一致。</td><td><audio controls preload="none" src="<音声path>"></audio> <a href="../a2/narration/japanese_title.wav">mp3</a></td></tr>
</table></section>
```
Y公開(public)ページの節出力: `''`(空=公開物に内部の判定情報を出さない設計どおり)。

### 4-Z-1. 完了ブロック(標準出力。Family Z a2。固有名詞アラーム報告は省略=同JSONに全文)
```
【日本語ASR PASS_W(新方式)】Family Z a2
  新方式(v2/β)のPASS_W: 1件 (β 0 / v2 1 / Secondary読み相違あり 0 / 断片説明(garble) 0) ※既存のPASS_WITH_WARNING全体: 1件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。
  1. [v2/発音同一] japanese_title | 音声=C:/Users/tensh/AppData/Local/Temp/ja_v2beta_rt_g8kmfzps/z_run_family/a2/narration/japanese_title.wav sha=dd3dbc1e6304
       原稿: 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密
       Primary: 月野氏は8,900本超。その奥に潜む岩の上着の秘密。  / Secondary: None
       発生理由: v2読み規則: 値の表記差(三十人=30人、桁区切りの有無等)と発音形の一致のみ(原因=A3_value+A2_particle)。読み・値は原稿と同等と判定。
       警告: JA_NEWLAYER_PRON_EQUIVALENT
  新方式の稼働状況: JA判定record 1件 / 有効 1 / 定数OFF 0 / E3E4ブロック 0 / **無効化(エラーで従来判定へ戻った)件数 0**
  要Human Review(HR Lock登録 0件 / JA HR queue行 0件): なし
```
### 4-Z-2. JSON(`pass_with_warning_listening_list.json`の`entries[0]`と`ja_v2beta_summary`)
```json
{
 "count": 1,
 "entries[0]": {
  "adopted_sha256": "dd3dbc1e630450305b6613e6449395e4ae8ad3885e9c49d9dba8d0c3b3548e19",
  "audio_path": "<一時dir>/japanese_title.wav",
  "canonical_text": "月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密",
  "entry_key": "segments/japanese_title",
  "inherited": false,
  "judge_rule_version": "ja_v2beta_r1off_01",
  "lang": "ja",
  "level": "",
  "listen_advised": false,
  "original_wav": "",
  "primary_text": "月野氏は8,900本超。その奥に潜む岩の上着の秘密。",
  "reason": "primary_pass",
  "rescue_basis": "v2",
  "rescue_reason_ja": "v2読み規則: 値の表記差(三十人=30人、桁区切りの有無等)と発音形の一致のみ(原因=A3_value+A2_particle)。読み・値は原稿と同等と判定。",
  "role": "japanese_title",
  "script_version": "v0",
  "secondary_reading_conflict": false,
  "secondary_text": null,
  "segment_id": "japanese_title",
  "slot": 1,
  "value_guard_kind_primary": "EQUAL",
  "value_guard_kind_secondary": null,
  "verdict": "PASS_W",
  "warning_labels": [
   "JA_NEWLAYER_PRON_EQUIVALENT"
  ],
  "weak_rank": 2
 },
 "ja_v2beta_summary": {
  "count_by_rescue_basis": {
   "v2": 1
  },
  "garble_explained_count": 0,
  "health": {
   "active": 1,
   "attempt_records": 1,
   "blocked_by_e3_e4": 0,
   "disabled_by_constant": 0,
   "error_samples": [],
   "errors": 0
  },
  "new_method_total": 1,
  "pass_w_total": 1,
  "secondary_reading_conflict_count": 0
 }
}
```
### 4-Z-3. 試聴ページ節HTML(`render_html_section`の出力)
```html
<section id="pass-with-warning-listening-list"><h2>事後試聴リスト(PASS_WITH_WARNING) WARNING音声 試聴リスト(自動採用・事後確認用)</h2>
<p>1件。公開をブロックしません。事後に試聴して確認してください。</p><p>『新方式』欄が入った行は日本語ASR v2読み規則/B-light βで救済した音声です(証拠の弱い順に先頭表示)。試聴は推奨(任意)であり、制作・組立・納品候補作成は止めません。</p><table border="1"><tr><th>segment</th><th>role</th><th>warning</th><th>原稿</th><th>Primary転写</th><th>Secondary転写</th><th>値ガードkind</th><th>理由</th><th>新方式</th><th>救済理由</th><th>音声</th></tr>
<tr><td>japanese_title</td><td>japanese_title</td><td>JA_NEWLAYER_PRON_EQUIVALENT</td><td>月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密</td><td>月野氏は8,900本超。その奥に潜む岩の上着の秘密。</td><td></td><td>EQUAL</td><td>primary_pass</td><td>v2</td><td>v2読み規則: 値の表記差(三十人=30人、桁区切りの有無等)と発音形の一致のみ(原因=A3_value+A2_particle)。読み・値は原稿と同等と判定。</td><td><audio controls preload="none" src="<音声path>"></audio> <a href="C:/Users/tensh/AppData/Local/Temp/ja_v2beta_rt_g8kmfzps/z_run_family/a2/narration/japanese_title.wav">mp3</a></td></tr>
</table></section>
```

### 4-Zβ. v2 + β混在の完了ブロック(Z a2のv2/β例 + E1の実β判定record=`e1:reselect a1`を同じ試聴リストに載せて生成)
```
【日本語ASR PASS_W(新方式)】Family Z a2(v2+β例)
  新方式(v2/β)のPASS_W: 2件 (β 1 / v2 1 / Secondary読み相違あり 1 / 断片説明(garble) 1) ※既存のPASS_WITH_WARNING全体: 2件。試聴は推奨(任意)・制作/組立/納品候補作成は止めません。
  1. [beta/読み相違あり(証拠が最も弱い)] beta_sample_from_e1_reselect_a1 | 音声=er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/japanese_title_attempt1_customb8f0ff16.wav sha=6801464baf94
       原稿: 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密
       Primary: 月野氏は8000900本超。その奥に潜む岩の上着の秘密。  / Secondary: 月の詩は8900本ちょ。その奥に潜む岩の上着の秘密。
       発生理由: 数値はSecondary(Azure)の転写で原稿と一致、読みはPrimary(OpenAI)の転写で原稿と同等と判定(B-light β)。Primaryの数値は崩れて書かれていたが断片の和が原稿値と一致: 8,900本←8000900(digit_split:8000+900)。Primaryの読みは助詞は→わ等の発音形でのみ一致。Secondaryの残りの読みが原稿と食い違う(Secondaryが別内容を聞いた可能性。Primaryの読みを正とした)。
       警告: JA_COMPOSITE_VALUE_FROM_SECONDARY, JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED, JA_PRON_EQUIVALENT, JA_COMPOSITE_SECONDARY_READING_CONFLICT, JA_COMPOSITE_LISTEN_ADVISED, JA_NEWLAYER_BETA_COMPOSITE
  2. [v2/発音同一] japanese_title | 音声=er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01/a2/narration/attempts/japanese_title_attempt2_customb8f0ff16.wav sha=dd3dbc1e6304
       原稿: 月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密
       Primary: 月野氏は8,900本超。その奥に潜む岩の上着の秘密。  / Secondary: None
       発生理由: v2読み規則: 値の表記差(三十人=30人、桁区切りの有無等)と発音形の一致のみ(原因=A3_value+A2_particle)。読み・値は原稿と同等と判定。
       警告: JA_NEWLAYER_PRON_EQUIVALENT
  新方式の稼働状況: JA判定record 2件 / 有効 2 / 定数OFF 0 / E3E4ブロック 0 / **無効化(エラーで従来判定へ戻った)件数 0**
  要Human Review(HR Lock登録 0件 / JA HR queue行 0件): なし
```

## 5. E3(有料・実ASR): 負例とscope外
同じ音声(`reselect a2`)に対し、**原稿の数値だけを誤り**にした負例を判定(期待=NG/HR、`rescue_basis=None`)。

| 条件 | scope | status | verdict | state | reason_code | rescue_basis | Primary転写 |
|---|---|---|---|---|---|---|---|
| e3_neg_value_8000 (月のしわ、8,000本超！その奥に潜む「岩の上着」の秘密) | X | STOPPED | HR | NG_PROTECTED | p1_value_diff | None | 月野氏は発線900本超。その奥に潜む岩の上着の秘密。 |
| e3_neg_value_9800 (月のしわ、9,800本超！その奥に潜む「岩の上着」の秘密) | X | STOPPED | HR | NG_PROTECTED | p1_value_diff | None | 月の詩は八千九百本超。その奥に潜む岩の上着の秘密 |
| e3_scope_none_positive (月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密) | None | STOPPED | None | NG_PROTECTED | p1_value_diff | None | 月野氏は発千九百本超、その奥に潜む岩の上着の秘密。 |

scope外の行の新キー有無: [{'ja_v2beta': False, 'judge_rule_version': False, 'rescue_basis': False, 'verdict': False}]
(この1本は、実ASRのPrimary転写がその回に崩れたため従来NGだった。scope外=従来出力の同一性は、保存済み転写での§1の表と、`gen_golden_scope_none_01`の396判定byte一致[TEST_RESULTS_01.md]で確認している。)

## 6. 月タイトル6音声の新判定(再掲。保存済み転写=EVAL_UNIFIED_03と同じ決定対、R-1 OFF、配線後のProduction判定)
| draw | 判定 | reason_code | rescue_basis | 警告 | 扱い |
|---|---|---|---|---|---|
| ms 03 a1 | HR | p1_value_diff | None |  | HR(従来どおり。既存HR Lock -> 個別採用[HUMAN_APPROVED]で扱う。UDR #203=未決。本IDでは判断しない) |
| ms 03 a2 | PASS_W | primary_pass | v2 | JA_NEWLAYER_PRON_EQUIVALENT | PASS_W(非ブロッキング。試聴は任意・推奨) |
| ms 03 a3 | PASS_W | ja_beta_composite | beta | JA_COMPOSITE_VALUE_FROM_SECONDARY,JA_COMPOSITE_PRIMARY_VALUE_GARBLE_EXPLAINED,JA_PRON_EQUIVALENT,JA_COMPOSITE_SECONDARY_READING_CONFLICT,JA_COMPOSITE_LISTEN_ADVISED,JA_NEWLAYER_BETA_COMPOSITE | PASS_W(非ブロッキング。試聴は任意・推奨)。**証拠が最も弱い**(Secondary読み相違あり。試聴推奨) |
| reselect a1 | PASS_W | primary_pass | v2 | JA_NEWLAYER_PRON_EQUIVALENT | PASS_W(非ブロッキング。試聴は任意・推奨) |
| reselect a2 | PASS_W | primary_pass | v2 | JA_NEWLAYER_PRON_EQUIVALENT | PASS_W(非ブロッキング。試聴は任意・推奨) |
| reselect a3 | HR | secondary_not_accepted | None |  | HR(従来どおり。既存HR Lock -> 個別採用[HUMAN_APPROVED]で扱う。UDR #203=未決。本IDでは判断しない) |

**ユーザーの既試聴判断との整合(1行)**: ユーザーは6音声を試聴して全てOKと判断済みで、新判定の4本(PASS_W)はその判断と矛盾せず(機械が通した音声にユーザーNGのものは無い)、残る2本(ms_03 a1・reselect a3)はユーザーがOKでも機械はHR扱いのまま=既存HR Lock -> 個別採用(HUMAN_APPROVED)で扱い、既存のHUMAN_APPROVED記録は変更していない。

**実wavの再ASR(§2)**: 同じ6本を新たにASRすると PASS_W は draw別に [3, 2, 2] / 6(OpenAI miniの転写が呼出しごとに変わるため。保存転写の4/6は上限に近い値)。6本すべてが機械PASSになることは合格条件にしない(ユーザー原文§5)。

