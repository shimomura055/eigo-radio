# RESULT_PACKET FXBY4 (委任_04, 読み取りのみ・API0・音声は未試聴)
出典: b1b/audit/tts_generation_results.json, er011_output/attempt_history.jsonl(13:27:43 part1 / 13:40:12 part3), raw_usage_log.jsonl。差分はcanonical vs ASRの単語diff(大小・句読点無視、自作script)。

共通: 全6 attemptとも route=standard(fallback_attempts_log/cascade_steps無し、attempts_detail.route=standard)。instruction=english_style_prefix_wide_margin、TTS=gemini-3.8-flash-lite-tts / voice Aoede(STANDARD mode)。一次ASR=gpt-4o-mini-transcribe、二次=azure-speech-stt。
Style sha: 実使用=3a680861…(PD6, 177字相当の"Speak directly to one listener…")。N01 d1956c91…とは**不一致**。ただしstyle_profile fx_20261017のFULL_STORY期待shaと一致(expected=actual)、style_profile_gate=PASS。N01(d1956c91)は旧profile coffee_n01_r2_p3側。同runのa2(Std)も同じ3a68…。=> 承認profile通り(er019_family_x_style_profile_01.py:105-111,275-)。「N01」前提なら委任文側の認識違い。
cooldown(600s): 理由コードは記録なし(cooldown_events: requested600/actual600.007, attempt_before=2, after=3。er020_tts_retry_local_rewrite_01.py:55-80「3回budgetの最終attempt直前に固定10分」ルール)。console_audio_01.txtはrun dir・er019_output配下に存在せず確認不可(find実施)。

## part1 (canonical 165語, 採用=attempt3)
| att | 生成(JST)/dur(trim raw) | 一次ASR判定 | 二次(Azure) | judge | 
|1|13:16:0x / 50.72s|TRUE_CONTENT_MISMATCH|TRUE_CONTENT_MISMATCH(Buy Us)|NG_BOTH secondary_not_accepted(p3_primary_ng), se=content_word|
|2|13:16:4x / 49.36s|TRUE_CONTENT_MISMATCH|TRUE_CONTENT_MISMATCH|NG_BOTH secondary_not_accepted, se=content_word|
|3|13:27:15 / 51.64s|HOMOPHONE_EQUIVALENT|未呼出|PASS primary_pass(adapter cmu_alternate), se=homophone_only|
(生成時刻はraw_usage_log UTC 04:16:08/04:16:42/04:27:15)
差分(前後3語は上のdiff基準; canonical→ASR):
- att1一次: "launch of [byUs] an AI" → Bias; "stage of [story-making] if" → storymaking。二次: byUs→"Buy Us"、"onto [the] stage"脱落(転写が"onto.Stage")、同storymaking。
- att2一次: byUs→BIOS、"pronounced [bias]"→BIOS。二次: byUs→Bias、"reader's"→reader、"stage of [story-]making"脱落("of.Making")、"LINE Manga"→"Lion Manga"。
- att3一次(採用): "pronounced [bias]"→**Byus**のみ(byUsは一致)。他は一致(句読点位置のみ差)。
分類: byUs/bias→Bias/BIOS/Buy Us/Byus = (c)固有名詞・造語誤認識(中心); storymaking, reader's→reader = (a); "onto the stage"脱落・"Lion Manga" = (d)/(c); 疑問符・読点位置差(Azureの"blurted that out? When…")= (b)。
採用att3のASR: 「It is pronounced Byus.」と転写。判定はHOMOPHONE_EQUIVALENTだが、実音が"bias"か"バイアス/バイアス風"かは未試聴=未確定。

## part3 (canonical 158語, 採用=attempt3, PASS_WITH_WARNING)
| att | 生成(JST)/dur | 一次 | 二次 | judge |
|1|13:28:39 (UTC04:28:39) / 50.40s|TRUE_CONTENT_MISMATCH|TRUE_CONTENT_MISMATCH|NG_BOTH secondary_not_accepted, se=content_word|
|2|13:29:13 (UTC04:29:13) / 49.20s|TRUE_CONTENT_MISMATCH|未呼出|NG_PROTECTED p1_value_diff, se=protected_number|
|3|13:39:23 (UTC04:39:23) / 50.32s|TRUE_CONTENT_MISMATCH|HOMOPHONE_EQUIVALENT(accepted)|PASS_WITH_WARNING secondary_confirmed(SECONDARY_CONFIRMED), se=homophone_only|
差分:
- att1一次: "yourself with [byUs] those words" → **Baias**。二次: byUs→"by us"、"was"→"with"、"a way"→"away"、"as a fan"の前で文が割れ"story. As a fan."(b)。
- att2一次: **"two works"→"20 works"**(数値protected、NG_PROTECTED)、byUs→FAYAS。
- att3一次: byUs→**BAYAS**(canonical "what if"の引用符等のみ差)。二次(採用根拠): byUs→bias、"imagining. What if the service…"と文境界が崩れる(b)。
分類: byUs→Baias/FAYAS/BAYAS/by us/bias = (c)中心; two→20 = (e)数値(最重要NG、att3では解消); away/with = (a)/(d); 文境界・句読点 = (b)。
採用att3: 一次はBAYAS(不一致)、二次Azureのbiasで救済=SECONDARY_CONFIRMED。pass_with_warning_listening_list.jsonにfull_story_part3がentry登録済み(試聴対象)。

## cooldown箇所
part1: att2直後 13:17:07→13:27:07、part3: att2直後 13:29:15→13:39:15。いずれもattempt_before=2→after=3。

## ユーザーが聞きどころを把握するための要約
- 両partとも3回すべてAdvanced標準経路(fallbackなし)。styleは承認profile fx_20261017のPD6(委任文のN01 d1956c91ではないが仕様通り)。
- 最大の争点は造語"byUs"(読み"bias")。ASRは Bias/BIOS/Buy Us/Byus/Baias/BAYAS等に割れ、発音の曖昧さが再試行の主因。
- part1採用は一次ASRのみ(HOMOPHONE判定、Azure未確認)。"It is pronounced bias."の箇所を重点的に聞く。
- part3採用はAzure二次の救済(PASS_WITH_WARNING)。"With byUs, those words…"の直前後と、att2で出た"two works"が正しく"two"かを確認。
- 音声の良否は未試聴=未確定。上記はASR転写上の差分のみ。

判断候補: なし

## RESULT_PACKET 4行
(1)既存仕様整合: er019_family_x_style_profile_01.py:105-111,184-186,275-280(fx_20261017)、er020_tts_retry_local_rewrite_01.py:55-80 (2)未承認機能なし・読み取りのみ (3)成果物=本file+delegation_log T-0。目的(再試行内容の把握)に適合、ただしconsole_audio_01.txt未発見で理由コード不明 (4)撤去/残置なし
判定整合: 重大NG=なし
