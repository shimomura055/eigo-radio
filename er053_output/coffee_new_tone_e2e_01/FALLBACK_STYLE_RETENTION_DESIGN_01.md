# FALLBACK_STYLE_RETENTION_DESIGN_01(調査・設計のみ、API課金0、コード/SSOT/Prompt変更なし)

管理ID: FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_03 / 日付: 2026-10-11 / worktree: eigo-radio-tone(HEAD 24acf9f4)
状態: 設計案(未承認)。Opus独立レビュー(Fable手配)→実装(別委任)の前段。commitしない。

## 0. 要約
- 現行fallbackは「承認済みtone文を捨て、短い汎用style `"natural, clear, conversational"`(EN)/旧JA minimal文(JA)へ差し替える」実装。Standard(A2)のEN Full Story・JA title/preview/comment/KP意味では「標準2回失敗→fallback1回」、Advanced(B1B)のpreview/comment/Full Storyでは「TTS例外・発話区間検出失敗の技術的fallbackのみ」で発火する。
- Style省略の理由は2段階。(a)minimal instruction自体の導入理由(長い演技指示でモデルがテキストを読まず応答する400 INVALID_ARGUMENT、短文のhallucination)は記録あり。(b)「fallbackでJ3/E2を載せない」判断はFAMILY-X-02 D-1「既存踏襲」「Phase 1時点の技術判断、実測に基づかない」と明記されたのみで、**tone維持を検討して却下した議論記録はない(記録なし)**。
- 救済実績: Flash-Lite時代(2026-09-27以降)のfallback発火実績はほぼ無く(根拠付きで2件)、定量評価できない。legacy時代(旧backend)のみ集計可能(§1-4)。
- 推奨: **案1(Style保持型minimal、承認済みtone逐語+発音hintのみ保持、試行枠・費用不変)**。最小指示(中立/旧Style)への降格は**黙って採用しない**。必要なら「Human Review候補(要明示承認)」としてのみ残す(案2-lite、後続判断)。
- STOP該当: **確定的なSTOP条件(救済能力の実測低下・品質悪化・費用/遅延の大幅増・仕様競合)は無し**。ただし「案1でstyle起因失敗の救済が弱まる可能性は未定量」。実装前に少額の強制fallback実測probe(別委任)を条件付きGateとして推奨。ユーザー判断論点は§8・§9。

## 1. 調査結果

### 1-1 fallbackの実体とstyleが落ちる箇所(ファイル:行、worktree)
| # | 経路(新tone対象) | 組み立て箇所 | styleが落ちる点 |
|---|---|---|---|
| E-A2 | Standard英語Full Story(F1.5+6%減速)/topic_intro/in_one_line | `er003_v1_crosslevel_audio_02_common.py` `generate_english_segment_with_fallback`(L80-)。標準: L142-146で`style_prefix_override`を渡す。fallback: L181 `_run_a2_minimal_fallback_attempt`(L292-)→L321 `repro01.generate_english_component_minimal_instruction(text,out_path,tts_backend,enable_pronunciation_resolver=True)`。docstring L106-109「fallbackにはstyle_prefix_overrideを渡さない(速度指示で平板化の恐れ)」 | `er003_v1_repro01_main_generate.py` L535-540: `tts_backend=="speech_metadata_flash_lite"`なら`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`、それ以外は`MINIMAL_INSTRUCTION_PREFIX`(L490-493、"warm podcast announcer"長文)。この関数自体が`style_prefix_override`引数を持たない |
| J-A2 | Standard日本語 title/preview/comment_1-4/KP日本語意味(J2) | `er003_v1_n3_01_tts_generate.py` `generate_a2_japanese_with_fallback`(L480-)。標準: L510-516で`style_prefix_override`転送。fallback: L532 `_generate_a2_japanese_minimal_instruction`(L400-) | L394-396 `_A2_JA_MINIMAL_INSTRUCTION_PREFIX`(「次の文章だけを、翻訳・言い換え・追加をせず、自然で温かいpodcastのナレーターの声で…」)を**backendに関係なく**使用(L406-413コメント「JA側は意図的に無変更、短い代替styleは考案しない」)。JA fallbackは短縮ですらなく旧文流用。J2は載らない |
| E-B1B | Advanced preview/comment_1-4(E2-upbeat、Charon) | `er003_v1_sing01_voice01_generate.py` `generate_charon_english`: 標準=L157 `style_prefix_override`。技術的fallback=L173-210 | trimmed is None(TTS例外/発話区間検出失敗)のときのみ、同一attempt内でL183-190 `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`へ差し替え(+発音hint) |
| F-B1B | Advanced Full Story(F1.5、Aoede) | `er003_v1_sing01_news_tail_fix.py` `generate_news_narration_wide_margin`: 標準=L128/L153、技術的fallback=L169-178 `repro01.generate_english_component_minimal_instruction`(style_prefix_override非転送) | 同上(repro01経由で`FALLBACK[0]`) |
| LR | Local Rewrite回復(Luna) | B1B: `_local_rewrite_recovery_for_charon_english`(voice01 L326-)は`generate_charon_english.__wrapped__(...,style_prefix_override=...)`で**tone維持**。A2英語: crosslevel L381-383の`_retts_fn`は`_run_a2_minimal_fallback_attempt`を呼ぶ=**toneが落ちる** | A2英語のLocal Rewrite再TTSもfallback扱い |
| 付随 | runtime evidence | repro01戻り値は`"instruction": "minimal (not ENGLISH_STYLE_PREFIX)"`のみ。`style_prefix`/`tts_model_id`を持たない(標準側voice01 L270-272は持つ) | fallbackではactual styleをevidenceで確認できない(是正対象) |

FALLBACK style逐語: `FAMILY_X_ROLE_STYLE_EN_FALLBACK = ["natural, clear, conversational", "clear"]`(`er033_tts_flash_lite_family_x_styles_01.py` L80、[0]のみ使用、[1]は未使用)。
承認済み新tone逐語(同ファイルL43-49): J2=「明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。」/E2-upbeat="warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation."/F1.5="warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, while maintaining clear and credible news narration."
Flash-Lite backendではstyleは`speech_metadata.style`で本文と別フィールド(`er033_tts_flash_lite_backend_wiring_01.py` L389-: prompt=(text,style_prefix))。旧backendの「指示と本文の混在(instruction leakage)」は構造上起きにくい。

### 1-2 fallbackの発火条件
- 総試行上限: 同一segment総試行`PRODUCTION_MAX_TTS_ATTEMPTS=3`(標準2+fallback1、`er011_human_review_lock_01.py` L80/102/103)。累積guard `MAX_CUMULATIVE_TTS_ATTEMPTS=15`(L68)。標準経路がHUMAN_REVIEW_LOCKEDを返したらfallbackへ進まない(crosslevel L152-157、n3 L522-527)。
- A2(E-A2/J-A2): 標準`standard_attempts=2`回が不合格(ASR TRUE_CONTENT_MISMATCH・反復/言い直しQA・length_ok・disfluency・TTS例外・無音等、`verified=False`全般)で発火。fallback予算=`3-len(標準attempts_log)`(標準がstop_retryingで早期終了した場合は2回以上になり得る)。fallback内でも検証し、不合格または`stop_retrying`で終了。fallback合格音声は`force_secondary=True`でSecondary ASR必須(CURRENT_SPEC L1909)。
- B1B(E-B1B/F-B1B): ASR/QA不合格ではfallbackは発火しない(同一styleで最大3回retry→Local Rewrite→HRL)。fallbackは同一attempt内の**技術的失敗**(TTS例外[400 INVALID_ARGUMENT/500/timeout/empty response]・発話区間検出失敗)のみ。
- 全段不合格→Local Rewrite回復(connected-speech有効時)→HRL。fallbackは「attempt3(最終)」にあたる。

### 1-3 Style省略の理由(DECISION_LOG/CURRENT_SPEC/OPEN_ITEMS grep結果)
- minimal instruction導入理由(記録あり): crosslevel L40-56コメント(2026-08-09、標準経路が6回とも400 INVALID_ARGUMENT "Model tried to generate text, but it should only be used for TTS"=「モデルがテキストを読み上げず応答しようとする現象」→確立済みminimalを一般化)、repro02 L148-153(「opt outのhallucinationを解決した仕組み」)、CURRENT_SPEC L1607/L1909(ER-003-N3-ROOT-FIX-01等)。OPEN-38(OPEN_ITEMS L205): 「標準経路(短いフレーズへ長いstyle instructionをそのまま使う設計)自体の見直し余地」=長styleが失敗を誘発し得るという認識は記録あり。
- FAMILY-X-02 D-1: repro01 L527-537コメント・CURRENT_SPEC L1654-1666: 「長い"warm podcast announcer"指示文を使っていたため短いfallback style(Trial attempt2相当)を配線」。er033 styles L70-80コメント: 「実測に基づくものではなくPhase 1時点の技術判断、Phase 2実TTS/ASR結果を見てOpus L2/Fableが妥当性を再確認すること」。
- J3/E2配線時(TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01、DECISION_LOG L12318-、2026-09-28 PRODUCTION_WIRED): 「fallback[minimal instruction]経路は既存どおり無変更、FAMILY-X-02 D-1踏襲」(L12332-)。確認用再生成でもfallback未発火(`instruction_type="english_style_prefix"`、L12376-)。
- **結論**: 「fallbackに承認toneを載せない」ことの設計根拠としての議論・実測記録は**なし**(省略は「既存踏襲」の副作用)。安全上の根拠はminimal導入時の「指示が本文を乱す」仮説のみで、speech_metadata方式(別フィールド)でその仮説が成立するかは未検証。INVESTIGATION_01 §2の注意と一致。

### 1-4 救済実績(集計: scratchpad `fb_scan.py`/`fb_scan2.py`、`python -I`、read-only、主repoのjson/jsonl 30,385ファイル)
注意: fallback markerを持つ記録の多くはlegacy時代(旧backend・旧style)。dedupeはpath+attempt内容による近似で、数字は目安。
- A2系関数(`fallback_used`付き結果)1,520件中、fallback発火53件(3.5%)。うち救済(status OK+asr_verified)41件(77%)、非救済12件(ASR_VALIDATION_UNCERTAIN 6、STOPPED 5、他1)。発火前の標準attempt失敗類型: TRUE_CONTENT_MISMATCH 40、ASR_VALIDATION_UNCERTAIN 13、TTS_FAILURE 5、TTS例外系(400 INVALID_ARGUMENT・timeout・empty response)多数。fallback内の合格classification: NORMALIZED_MATCH 10、EXACT 4、PHONETIC 1、Secondary系 2。
- B1B/voice01系(`attempts_log`に`minimal_fallback`)47件: 最終OK 29/STOPPED 18、fallback合格21件。**発火直前のトリガ**: TTS 400 INVALID_ARGUMENT 27(救済10/非救済17)、TTS empty response 6(救済5/非救済1)、TTS timeout 2(救済2)、TTS 500 2(救済0)、発話区間検出なし1(0)、その他検証不合格9(救済4)。=技術的fallbackは主に400/empty/timeoutの救済。
- **Flash-Lite時代(2026-09-27以降、review_lock_state 511セグメント)**: 2 attempt以上を要したのは127件(約25%、試験run含む)、HUMAN_REVIEW 45件。fallback markerが残る記録は2件のみ: (i)small_bag b1b `full_story_part2_heading` attempt1=TTS_FAILURE分類→attempt2=minimal_fallback(`FALLBACK[0]`)で合格(RESOLVED、見出しroleで新tone対象外)、(ii)er022 Trial b `point_three` attempt2 minimal_fallbackもTRUE_CONTENT_MISMATCHで不合格(HRL)。`flash-lite`を含む729ファイル内に`fallback_used:true`/`minimal_fallback`記録は0件。= **新tone対象role(J2/E2/F1.5)でfallbackが救済した/しなかった実績はほぼ無い**。補足: OPEN-222(極短単語"Two."/"Three."の言語ドリフト)は標準styleでもFALLBACK styleでも再現し、style差では救済できなかった(OPEN_ITEMS L405)。
- 限界: `last_attempts_log`は最終部分のみ保持。attempt別audioは主repoでgit管理されない(`save_tts_attempt_audio` er011_human_review_lock_01.py L489-)。Flash-Lite時代のfallback救済率は定量不能(データ不足)。

### 1-5 J3/E2(2026-09-28 PRODUCTION_WIRED)配線時の扱い
当時もfallbackはStyle省略(D-1踏襲)。DECISION_LOG L12318-12385に「fallback経路は既存どおり無変更」と記録されるのみで、tone維持を比較検討・却下した議論記録なし(記録なし)。

## 2. 設計制約
1. 初回・標準retry・fallback・regeneration・resumeで承認Styleに整合(旧仕様への黙示的復帰禁止)。2. 既存fallbackの救済能力維持。3. 総試行3回上限・HRL・累積guard・Secondary ASR必須化・OPEN-122/186 Equivalence Layer・Validator/記号正規化は不変(独自に回避しない)。4. 既定backend(structured_separation)はbyte-identical(他Family無影響)。5. 新styleの文言を考案しない(承認逐語のみ)。承認toneの「短縮/抜粋」派生文は未承認の新styleになるため不可。

## 3. 設計案比較
| 項目 | 案1 Style保持型minimal | 案2 2段fallback(保持→最小) | 案3 fallback廃止(HRL直行) |
|---|---|---|---|
| 内容 | fallbackの`speech_metadata.style`を、roleの承認Style(J2/E2/F1.5)逐語へ。除外するのは旧minimal文言・"warm podcast announcer"等の補助指示のみ。発音hint(Ledger由来)は従来どおり付与。A2 EN Full Storyは既承認A2_SLOWER_PACE_INSTRUCTIONを標準経路と同条件で連結(推奨。要Opus確認) | 標準2→保持fallback。さらに中立minimalを使う場合は**自動採用せず**Human Review候補扱い(音声保存・Lockへ)。総試行3回上限内では最小指示段を置く枠が無く、上限例外(KP英語のような4回)か、HRL後の明示承認時のみ生成のどちらかが必要 | 標準3回後HRL |
| 救済能力 | (a)TTS 400/empty/timeout: Flash-Liteはstyleが別フィールドで旧機序は弱い。E2/F1.5は現行FALLBACK styleより長いが1文、救済は維持見込み(未実測)。(b)TRUE_CONTENT_MISMATCH(数詞/固有名詞等): 救済要因は主に再試行・Secondary ASR・Local Rewriteでstyle差の寄与は小さい(OPEN-222)→維持見込み。(c)style起因失敗(tone文が発話ゆらぎ誘発): 救済が弱まる可能性(未定量) | (a)(b)は案1と同じ。(c)は最小指示で救済し得るがStyle違反のため採用せずHRL=自動救済は案1以下(ただし原則厳守) | 大幅低下。legacy集計で失われるのはA2系41件+B1B系21件相当。B1B技術的fallback(400/empty/timeout救済)が全消失(Flash-Lite時代は不明) |
| 品質 | 新toneが全経路で一貫。fallback後のASR/QA/Secondary ASR必須化は不変 | 同左+最小指示音声は人間確認 | tone一貫だがHRL増=人手増 |
| 費用・遅延 | 追加なし(試行枠・回数不変) | 追加なし(最小候補生成は明示承認時のみ)。HRL増の人手コスト | API費は減るがHRL増で待ち・再生成コスト増 |
| 仕様競合 | Validator・記号正規化・length_ok・Master Store(key=(language,voice,tts_model,text,style_instruction_id,version))・version guard v4と整合。留意1・2参照 | 最小指示音声はStoreへ保存しない(style_id違いの黙reuse禁止) | 競合なしだがCURRENT_SPEC「標準2+fallback1=TOTAL3」「Secondary ASR必須」等の改訂が必要(ユーザー承認要) |
| 開発規模 | M: `repro01.generate_english_component_minimal_instruction`・`_generate_a2_japanese_minimal_instruction`に`style_prefix_override`引数追加(既定None=現行挙動)、crosslevel `_run_a2_minimal_fallback_attempt`/Local Rewrite `_retts_fn`/voice01/news_tail_fixの技術的fallbackからoverride転送、er019 runnerでrole別style(`_role_style`/`_role_style_ja`/`_role_style_slower`)をfallbackにも渡す。SCG(merge済)が同じ3ファイルを変更しているためworktree baseのconflict確認要 | L: 案1+Human Review候補フロー(Lock/approve_regenerate連携、state追加) | S: 分岐削除+SSOT/test大幅改訂 |

留意1(Master Store/resume): fallback音声が標準と同一style_idでStore登録されると、後続reuseで「fallbackだが承認Style」として扱われる。承認Styleで生成された音声なら整合する(むしろ望ましい)。旧FALLBACK style音声が過去Storeにあっても、version guard v4(INVESTIGATION_01 §7)により今回の新runには引き継がれない。resume時は`style_prefix`/`style_source`をtelemetryで再検証すること。
留意2(JA): JA fallbackの現行minimal文が持つ「翻訳・言い換え・追加をしない」注意文は、J2逐語へ置換すると消える。文言追加は新style考案で禁止のため、既存の全文ASR Validatorで担保する。JA fallbackのtext忠実化効果が弱まる可能性は未定量。

## 4. 推奨案: 案1(Style保持型minimal)+強制fallback probe(条件付きGate)
- 理由1: ユーザー必須条件(新Style維持)と救済能力維持を、追加費用・試行回数・HRL/Validator/上限の変更なしで両立できる最小変更(規模M、既定backend byte-identical)。理由2: Flash-Liteではstyleが別フィールドで旧minimal導入理由(指示が本文を乱す)の機序は弱く、E2/F1.5は1文。J2は2文で旧JA minimalと同程度の長さ。
- 条件: 実装後、強制fallbackで「承認Style保持fallback」と「現行fallback style」を既知の難所(数詞・固有名詞・短文・400再現ケース)で比較する少額実測(別委任、数十円規模、現行Flash-Lite backend、最新モデル原則に従う)を実施し、救済率が大きく低下しないことを確認(低下時はSTOP→案2-lite等)。
- 最小指示(中立)への自動降格は却下。必要なら案2-lite(HRL到達後、人間が明示承認した場合のみ中立minimalで候補生成、Store保存せず`style_source="degraded_by_user_approval"`記録)を後続判断。
- B1Bでは影響はTTS例外時のみ。A2で影響が大きい。

## 5. Style適用の検証方法(runtime evidence)
- fallback戻り値/attempts_log/`save_tts_attempt_audio`のmetadataに、`style_prefix`(実際にTTSへ渡した最終文字列、発音hint込み)、`style_source`("approved_role_style"等)、`instruction_type`、`tts_model_id`、`voice`、`tts_backend`を必須記録(現在fallbackは`"instruction": "minimal ..."`のみ)。
- er019 runnerで、Flash-Lite backend時に新tone対象segment(Standard: title/preview/comment_1-4/KP意味[J2]・Full Story[F1.5+減速連結]。Advanced: preview/comment[E2]・Full Story[F1.5])について、採用attemptのstyle_prefixが承認定数(+許容付加物=減速指示・発音hint)と一致することをfail-closedで検査(不一致=STOP、旧styleで採用しない)。
- テスト: モック(`resolve_tts_call_and_prompt`)で最終promptのstyle要素を捕捉し、全attempt種別(標準/fallback/Local Rewrite/regeneration/resume reuse)で承認定数を含み、旧`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`や旧JA minimal文を含まないことを検査。既定backend経路は従来promptとbyte-identical。
- 実API(別委任、少額): 強制fallback(標準経路をモックで不合格化、またはfallback関数直接)で1〜数segment生成し、`speech_metadata.style`・model_id(Flash-Lite)・voice(Aoede/Charon)・`asr_verified`を記録。

## 6. テスト計画
1. 単体: `style_prefix_override`追加後、(a)指定時=その文字列(+hint)がspeech_metadata.styleに入る (b)未指定=現行(既定backend byte-identical)。2. 経路別: E-A2/J-A2/E-B1B/F-B1B/Local Rewrite(A2英語・B1B)。3. 回帰: 既存test(er019 flash-lite wiring/er033/er011 retry/Human Review/ASR validator/SCG)全体、version guard v4不変、Master Storeキー互換。4. 強制fallback統合テスト(モックTTS): 標準2回不合格→fallbackでstyle保持、3回不合格→HRL(旧Styleで採用されない)。5. runtime evidence(少額実API): 難所ケースで保持fallback vs 現行fallbackの救済率比較(§4条件)。6. 「標準2+fallback1=3回」「Secondary ASR必須化」の不変確認。

## 7. Gate文案(PM_GOVERNANCE Wiring Checklist向け草案、SSOT未記入)
- 「Production初回経路だけでなく、retry・fallback・regeneration・resumeの各経路でも、人間承認済みの仕様(Style/Prompt/Validator等)が一貫して適用されるか。旧仕様が黙って採用される経路は無いか(runtime evidenceで各経路の実適用値を確認)。」
- 「新仕様の正式採用時は、既存fallback/retryの救済能力(発火条件・失敗類型・試行上限)を調査し、救済能力を損なわず承認仕様を維持する設計を必須とする。両立不能な場合はSTOPしユーザー判断。」
- 「旧仕様/中立仕様への降格採用は、人間の明示承認がある場合に限る。」

## 8. Opusレビュー論点
1. 案1で救済能力が実質維持されるという根拠(speech_metadata別フィールド、style差<<試行ゆらぎ)の妥当性と、強制fallback probeの設計(N・ケース・費用)。
2. JA fallbackの「翻訳・言い換え・追加をしない」文の喪失の扱い(style逐語維持とValidator担保の整合)。
3. A2 EN fallbackでA2_SLOWER_PACE_INSTRUCTION連結の有無。
4. Production共通原則の適用範囲: 新tone 3 Style以外のrole(TOPIC_INTRO/IN_ONE_LINE/HEADING_READOUT/shell/KP等)のfallback styleも承認Styleへ揃えるか(ユーザー判断)。
5. 案2-lite(HRL後・明示承認時のみ中立候補)を設けるか。
6. A2英語Local Rewrite `_retts_fn`のstyle保持と、Master Store保存・resume時の再検証。
7. SCG(同ファイル変更)とのconflict・worktree base確認。

## 9. STOP該当の有無
- 確定的STOP(救済能力の**実測**低下・品質悪化・費用/遅延の大幅増・仕様競合)は**無し**: 案1は試行枠/費用不変、Validator/Store/version guard/HRLと整合、既定backend不変。
- 潜在リスク(未定量): (1)style起因失敗の救済が弱まり得る(Flash-Lite時代のfallback実績がほぼ無く実測不能)。(2)JA minimal文の喪失。(3)他role拡張・案2-lite・減速連結は要ユーザー判断。ユーザー規定のSTOP報告項目(原因/救済能力への影響/案・代替/品質・コスト・期間/推奨)は§1-4・§3・§4に記載。実装前に強制fallback probe(別委任・少額)を推奨。

## 10. Opus条件Aレビュー(GO with required fixes)反映と実装結果(委任_06、2026-10-11、API課金0)
状態: 実装・test・¥0モックprobe完了(branch `feature/coffee-new-tone-fallback-01`、未merge・Production採用はユーザー承認事項)。証跡: `FALLBACK_MOCK_PROBE_01.md`、`er003_fallback_style_retention_test_01.py`、`er003_fallback_style_retention_probe_01.py`。

| Opus必須 | 反映 | 場所 |
|---|---|---|
| B1(A2英語=連結済み減速指示をそのまま) | runnerが標準経路へ渡す`_role_style_slower("FULL_STORY")`と同一値を`fallback_style_prefix`へ渡す(新文言を合成しない) | er019 audio runner(A2 Full Story)、crosslevel/repro01 |
| B2(JAはJ2逐語へ置換、旧注意文と連結しない) | `_generate_a2_japanese_minimal_instruction(fallback_style_prefix=...)`指定時は`_A2_JA_MINIMAL_INSTRUCTION_PREFIX`を置換(連結なし)。「翻訳・言い換え・追加なし」の担保は既存の全文ASR Validatorに委ねる | er003_v1_n3_01_tts_generate.py |
| B3(A2英語Local Rewrite再TTS) | crosslevel `_retts_fn`→`_run_a2_minimal_fallback_attempt`へ同一styleを転送。B1B側news_tail_fixのLocal Rewrite再TTSも、対象role(Full Story)のみ`style_prefix_override`/`fallback_style_prefix`を再TTSへ渡すよう是正(従来は標準styleが再TTSへ渡っていなかった=旧ENGLISH_STYLE_PREFIXへ黙って戻っていた) | crosslevel、news_tail_fix、voice01 |
| B4(i)(¥0モックprobe) | 全経路(初回・標準retry・fallback・regeneration・resume)×全role | `FALLBACK_MOCK_PROBE_01.md` |
| B4(ii)(¥0統計) | Tone Trial 12件+Flash-Lite era記録 | 同上 |
| B5(対象限定) | 既定None引数`fallback_style_prefix`を新設。runnerがJ2/E2_UPBEAT/F1.5対象segmentのみに渡す。TOPIC_INTRO/IN_ONE_LINE/HEADING/shell/KP英語/他Familyは引数を渡さず従来値 | 同上、テスト`RunnerRoleScopeTests` |
| B6(証跡) | fallbackの戻り値・attempts_log・`save_tts_attempt_audio` metadataに`style_prefix`(先頭200字)・`style_source`・`tts_model_id`・`tts_backend`を記録。crosslevelの`"model"`固定記録を`flw.resolve_actual_model_name`へ修正。`style_source`判定は`fl_styles.describe_style_source` | repro01/crosslevel/n3/voice01/news_tail_fix/styles |
| 追加(resume) | `FAMILY_X_VARIABLE_ROLE_STYLE_VERSION`を`v5_j2_e2upbeat_f15_tone_refresh_fallback_style_retention`へbump(旧v4 cacheは再利用されず再生成) | er019 audio runner |
| 未確認事項(Master Store) | fixed shell(`charon_english_fixed_shell`/`charon_japanese_fixed_shell`)とKP英語(`key_phrase_english_component`)のみがMaster Store経由で、これらは`fallback_style_prefix`を渡さず従来どおり。新tone対象のfallback音声(JA/Full Story/Advanced preview・comment)はMaster Storeへ登録されず、`tts_generation_results.json`+`style_version`(v5)で管理される。よってstyle_instruction_idの整合問題は発生しない |

設計からの逸脱・補足: (1) 設計§3案1の「Local Rewrite」はA2のみ言及だったが、news_tail_fixのLocal Rewrite再TTSが標準styleを渡していなかった既存ギャップを発見したため、対象role(Full Story)に限り是正(B5範囲内)。非対象role(B1B in_one_line)のLocal Rewrite再TTSは従来どおり(標準ENGLISH_STYLE_PREFIX)で、本件では変更していない(報告参照)。 (2) 強制fallback実測probe(実TTS)は本委任のスコープ外(別委任・少額)。
