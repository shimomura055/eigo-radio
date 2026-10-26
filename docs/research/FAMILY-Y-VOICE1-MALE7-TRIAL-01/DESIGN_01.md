# DESIGN_01 — FAMILY-Y-VOICE1-MALE7-TRIAL-01(生成前に固定。観測後に基準を変えない)

作成: 2026-10-26(生成開始前、API 0)。Trial専用。Production(Voice割当・公開音声・Voice Registry・Style/Prompt・Gate)は変更しない。`run_01/`配下は読取のみ。
目的(ユーザー再Trial指示原文=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-VOICE1-MALE7-TRIAL-01_USER.md`): Family Y Voice 1に適した**男性**Voiceを、長ポーズの自然さ・安定性・音声品質から選び最終推奨1名の材料を作る。女性Voiceは比較に含めない(前回Zephyrは除外)。Sonnetは「推奨候補」までで最終推奨はFable。

## 1. 比較対象(男性7名)と追加2名の選定
| # | Voice | 由来 | 性別の出典 |
|---|---|---|---|
| 1 | Algieba | 現行Y Voice 1(`er121_family_y_structure_01.py:53` FIXED_VOICE_SLOTS) | 同上+Google Cloud TTS Chirp 3 HD Voice表(Male) |
| 2 | Schedar | Y Voice 3 / Z男性2(`CURRENT_SPEC.md:1563`) | 同上(Male) |
| 3 | Fenrir | Z男性3(`CURRENT_SPEC.md:1563`) | 同上(Male) |
| 4 | Orus | Z男性4 | 同上(Male) |
| 5 | Puck | Z男性5 | 同上(Male) |
| 6 | **Iapetus**(追加) | Gemini TTS公式Voice表「Clear」。repo内に男性役(LEO)での採用実績あり=`tts_test.py:96`、`tts_style_test.py:192`、`tts_japanese_demo.py:76` | Google Cloud TTS公式 `https://cloud.google.com/text-to-speech/docs/chirp3-hd` のVoice表で `Iapetus Male`(2026-10-26 curlで確認) |
| 7 | **Sadaltager**(追加) | Gemini TTS公式Voice表「Knowledgeable」(説明・解説調=Family Yの一人称Voiceに適性) | 同上 `Sadaltager Male` |
- 声質差の考慮(Gemini TTS公式の声質ラベル、`https://ai.google.dev/gemini-api/docs/speech-generation`): Algieba=Smooth / Schedar=Even / Fenrir=Excitable / Orus=Firm / Puck=Upbeat。追加2名は既存5名と重ならない **Clear**(Iapetus)・**Knowledgeable**(Sadaltager)。
- 除外した男性: Charon(Advanced補助/ナレーター枠`CURRENT_SPEC.md:1563`、人物Voice用プールに含めない)、Alnilam(Firm=Orusと重複)、Algenib(Gravelly=聴きやすさ懸念)、Rasalgethi(Informative=Charonと近い)、Enceladus(Breathy=長ポーズ・息継ぎ多用の懸念が事前に高く本Trialの目的に不向き)、Umbriel・Achird・Zubenelgenubi・Sadachbia(予備)。
- **予備(事前固定)**: 追加2名のどちらかがTTS APIでVoice名エラーとなった場合のみ、Iapetus→Umbriel(Easy-going)、Sadaltager→Achird(Friendly)へ代替(いずれも同表で男性)。代替は理由を`BUDGET_LOG_01.md`に記録。声質が気に入らない等の結果依存の入替えは行わない。
- 人物像・聞き分け(Y Voice 2=Zephyr(女性)、Voice 3=Schedar(男性30代)、Voice 1=男性40代): 聴感評価は機械化できないため試聴ページで提示し、Fable/ユーザー判断に委ねる(Sonnetは主観結論を出さない)。

## 2. 条件同一性(全Voice共通)
- 本文: `run_01/{a2,b1b}/parts.json`のy_voice_1/2/3を一字も変えず使用(Std 120/157/156語、Adv 133/155/158語、Std/Advは別文)。句読点変更なし。3本文とも1段落(改行0を確認済み)。
- 生成関数: Production関数を前回Trialと同一呼出しでimport(Voice名のみ差)。Std=`n3_tts.generate_a2_segment_with_slowdown`(6%減速・減速後ASR再確認・repetition QA)、Adv=`news_tail_fix.generate_news_narration_wide_margin`。`TTS_EXECUTION_MODE=STANDARD`、モデル`gemini-3.8-flash-lite-tts`、backend `speech_metadata_flash_lite`、style_profile `default`。
- Style文sha(今回spec、全Voice同一): Std `9293e0c3b294…`、Adv `07d72dd67728…`。前回Trialの`settings_*.json`のsha(Std 9293e0c3b294…、Adv 07d72dd67728…)と**一致**=再利用可(`REUSE_CHECK_01.md`)。
- 生成script: `tools/ym7_generate_01.py`(前回`yvp_cross_generate_01.py`の派生。男性許可リストでVoice名を直接指定。起動ごとに使用moduleのsha16を`launch_*.json`へ記録)。offline testで「Voice以外の設定が全Voiceで同一」をassert。

## 3. 評価指標(定義固定)
unit=raw attempt wav 1本(=独立TTS draw。Stdは減速前の生attempt。前回Trial DESIGN §1と同じ。減速は全Voice共通の後処理)。適格=main route(minimal_fallback等は別条件で本体から除外)。
計測=既存tool(`yfb_silence_scan_01`: −40 dBFS・10msフレーム・≥150ms、`yfb_pause_stats_01.merge`: <120ms有音は前後停止を結合、`yfb_pause_align_01`: 停止位置を本文語境界へ対応付け、精度±2〜3語)。
- **主要指標(primary)=「文中の不自然な長停止」=文境界に対応しない≥1.0秒の停止の1 sampleあたり回数** (`mid_long1000`)。文境界=対応付けられた直前語が `. ? ! …`(閉じ引用符/括弧付き可)で終わる。**コンマ・節区切り直後の≥1.0秒もここに含める**(自然な文末の間と区別するため。≥1.0秒のコンマ停止は不自然とみなす)。位置推定は±2〜3語の誤差を持つため、位置に依存しない次の補助指標を併記し、両者の順位が乱れたら「位置対応付けの不確実性」として開示する。
- 補助: 全≥1.0秒停止回数(`long1000_n`、位置非依存)、停止占有率(内部停止合計/全体尺%)、最長停止、悪いtake率=P(`mid_long1000`≥1)(`bad_mid`)、全≥1秒版`bad_any`、ASR合格率(attemptの`verified`)、Repetition QA旗率、fresh takeの最終status OK率、発話速度。
- 自然な間(文末の0.5〜1.0秒)は評価の対象外(減点しない)。「短いほど良い」とはしない。

## 4. 推定(区間)
- Voiceごとの値=**6 cell(Std/Adv×本文1〜3)の等重み平均**(reuse側のcell sizeが不均衡=Algieba本文1が多い等の影響を避ける)。
- 95%区間=cell層別ブートストラップ(各cellを復元抽出、B=10000、seed=20261026+項目名のsha)と、件数指標はGamma-Poisson(事前0.5)、2値指標はBeta(0.5,0.5)事後(cell等重み平均)の**広い方(下限は小さい方、上限は大きい方)**。理由: 「文中≥1秒」は0件が多く、通常のブートストラップは0件のcellで区間幅が0になり過剰に断定しやすい(Fable既定のブートストラップに保守側の補正を追加、事前固定)。
- Algieba比=主要指標の差のブートストラップ95%区間と P(Voice<Algieba)。
- 感度分析(判定には使わない): (a)初回attempt(attempt==1)のみ (b)過去日の再利用(run_01/候補take)を除く。
- 切り分け: 主要指標の平方和を Voice / 本文 / レベル / Voice×本文×レベルcell / cell内(同条件の生成ばらつき)に分解(不均衡のため周辺SSの近似)。Voice×本文の交互作用はcell別表(本文ごとのVoice順位)で示す。

## 5. 生成計画(事前固定)
### 5-1 再利用
前回Trial(PAUSE-CAUSE-01、同日2026-10-26、同一Style/モデル/関数)の**Algieba(voice slot 1)とSchedar(voice slot 3)のmain sample**(Algieba 39 + Schedar 19 = 58)を再利用。Algieba本文1は再利用が過去日(run_01正式attempt/Voice1候補take)のみのため、**同一セッションの対照としてAlgieba本文1を新規2 take×Std/Adv(計4 take)追加**(ドリフト混入の監視。事後に有利な条件を作る目的ではなく、基準Voiceの条件整合のため)。cell n<2の再利用cellは無い(最小3)。
### 5-2 Phase 1(64 take)
新規5名(Fenrir/Orus/Puck/Iapetus/Sadaltager)×3本文×2レベル×2 take=60 + Algieba対照4 = **64 take**。
- 順序: `tools/ym7_plan_01.py`で決定論生成(`plan_phase1.json`)。ラウンド(take序数)→cell(本文×レベル)→Voiceの順で、Voice位置を(j+cell+round)で回転=特定Voiceが常に先頭/末尾にならず、Voiceが時間帯に偏らない。3 processへ貪欲割当(各processのVoice別件数を均す)、各process内もラウンドロビン順。
- 起動: 3 process(batch 1〜3)を**160秒以上の間隔**でずらして並列(0/160/330秒=同一run 5分以内の起動は2回以下)。各起動前に`tools/stop_scope_check_01.py`(rc=0)、`TTS_EXECUTION_MODE=STANDARD`、`--budget-jpy`は各process 80円(合計の暴走防止)。
### 5-3 Phase 2(上限36 take)と停止規則 — §6
### 5-4 費用見積(`docs/pm/RESULT_PACKET_YVP1.md`の実績 91.12円/39 take=2.34円/take [TTS+ASR/QA+retry込み])
Phase 1 64 take≒150円、Phase 2 最大36 take≒84円、合計最大約234円(Guardrail 250円以内、案件300円未満=承認区分A)。日次: 既使用約214円+本案件最大約234円+他案件の予定(Z約48〜75円、Chunk約100円)=約600〜620円で日次1,000円以内。

## 6. Phase 1後の停止/継続規則(事前固定)
`ym7_summarize_01.py --phase 1`が機械判定:
1. 7名のpooled主要指標の平均と95%区間を算出。最小平均のVoiceを`best`とする。
2. **drop**: `best`以外で、区間下限 > `best`の区間上限(区間が重ならない)のVoiceは追加生成しない(Algiebaは基準なのでdrop対象外だが、下記のとおり`best`が全員と区間分離すればPhase 2なし)。
3. `best`が**他の全Voice(Algieba含む)と区間分離**している場合はPhase 2なし(差が明確)。
4. それ以外: 生存Voiceのうち平均の小さい上位3名(Algiebaが入らなければ上位2名+Algieba)に、各cell(本文×レベル6)+2 take=Voiceあたり12 take、**最大36 take**を追加。順序はラウンドロビン、`plan_phase2.json`を決定論生成。
5. Phase 2後は追加生成しない。上位2名の区間が重なる場合は「**明確な優位なし**」として数値で報告(さらなる追加はFable判断事項として報告に残す)。
- 暴走防止: Phase 1の途中で、想定外の大量retry・無意味なloop・原因不明のrc≠0が2回続く場合は再起動せずSTOPして報告。

## 7. 推奨候補の条件(事前固定。Sonnetは条件の機械判定までで、最終推奨はFable)
候補Vが**全て**満たす場合のみ「推奨候補」:
1. 主要指標のpooled平均がAlgieba未満、かつ (区間がAlgiebaと重ならない または 悪いtake率`bad_mid`がAlgieba比で半減以上)。
2. Std・Advの**両レベルで**主要指標の平均がAlgieba以下(両方での安定性)。
3. ASR合格率(attempt)がAlgieba以上、Repetition旗率がAlgieba以下。
4. 声質の決定論的問題がない: Vのfresh takeが10以上あり、最終status OK率≥0.9(ASR不一致・欠落でtake失敗が多いVoiceは不可)。
複数該当時は主要指標の平均が最小のVoiceを候補1位とし、他は並記。該当なしなら「推奨候補なし(現行維持)」とし数値を示す。Production採用判断・聴感(声質の自然さ・人物像適合・V2/V3との聞き分け)は含まない。

## 8. 禁止・開示
- 結果を見た後に§3〜§7の基準・閾値・追加条件を変更しない。変更が必要なら「観測後改訂」として履歴付きで開示(`DESIGN_01.md` §9に追記し、sha固定時のshaと改訂後shaを併記)。
- 少数takeの偶然の好結果で推奨しない(§7の条件・区間で保護)。男女混合の結果を根拠にしない(前回Zephyr除外)。
## 9. 実施記録・改訂
このファイルは固定後に編集しない(sha固定)。実施記録は`BUDGET_LOG_01.md`・`RESULT_01.md`、観測後改訂が必要な場合は`DESIGN_01_REVISIONS.md`に履歴付きで別記する。
