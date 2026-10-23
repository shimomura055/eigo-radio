# PHASE3_PLAN_01: 音声Trial計画(次委任。本委任では音声を生成しない)

## 1. 音声化する候補(Phase 2の確定)
- **主候補: R2g**(R2をLeakage Gate通過させた稿)のStd+Adv各1本。理由(所見): 導入(リード)の情景・最終パートの比喩の回収が3本中で最も良く、Leakage・RF・5段落契約・S3監視はR0g/R1gと同等以上で悪化なし(`WRITER_COMPARISON_01.md`・`EN_COMPARISON_01.md`)。
- **比較候補(任意・推奨): R0g**のStd+Adv各1本。理由: 「R1/R2の追加費用(+10.56円/セット)に見合う品質向上があるか」はユーザー試聴でしか決められず、R0gとR2gの差は読みの差(導入・比喩)で、音声では聞き取りやすさが逆転しうる。R1gは中間のため音声化しない(原稿比較で足りる)。
- 学習支援構造(日本語タイトル・Preview・Comment 1〜3・KP 3件・In One Line)は**R2g・R0gの両方でStd/Adv全4件生成済み**(`english_{r2,r0}/scaffold_{b1b,a2}/`、Comment 4なし、KP全件CANONICALIZATION_PASS)。
- 追加アーム(A0/A1)は音声化しない。

## 2. 固定Voice(ユーザー決定。自動割当関数は使わない)
| segment_id | 内容 | Std | Adv |
|---|---|---|---|
| full_story_part1 | リード(語り手) | Aoede | Aoede |
| full_story_part2 | Voice 1(男性・教員) | **Algieba** | **Algieba** |
| full_story_part3 | Voice 2(女性・予算査定職員) | **Zephyr** | **Zephyr** |
| full_story_part4 | Voice 3(男性・定時制の生徒) | **Schedar** | **Schedar** |
| full_story_part5 | 最終パート(語り手) | Aoede | Aoede |
| in_one_line | 末尾要約 | Aoede | Aoede |
| Preview / Comment 1〜3 / 日本語タイトル / KP日本語 | 補助 | Aoede(Stdは単一Narrator) | Adv: Charon(`_row_info_b1b`準拠: Welcome・Topic intro・Preview・Comment・KP日本語・Full story introはCharon、KP英語はAoede) |

X準拠(Std=Aoede単独、Adv=Aoede+Charon)にVoice 3人を加える。Pro系TTSは使わない(gemini-3.8-flash-lite-tts、X/Zと同じ)。見出し読み上げ(旧Narrator見出し)は使わない。

## 3. Phase 3で必要な実装(Y runner = X runner無変更の薄い入口)
1. Y用segment順序: Intro → Welcome → Topic intro →(Std: 日本語タイトル)→ Notification 1 → Preview intro → Preview → Notification 2 → Key phrases intro → KP(最大3) → Notification 3 → Full story intro → Comment 1 → part1 → Comment 2 → part2 → part3 → part4 → Comment 3 → part5 → In One Line → Outro(Voice 1〜3は連続、Voiceの間にCommentもSFXも入れない)。
2. 直書きタプルのY版: `_REQUIRED_FULL_STORY_SEGMENT_IDS`/`_BODY_SEGMENT_NAMES`/`FULL_STORY`(style profile)/`resolve_narrative_role`(加算)/`A2_SLOWDOWN_TARGET_SEGMENTS`の扱い(`INHERITANCE_STATUS_01.md` §2)。**parity test**: Y part1〜5がX本文segmentと同じ検査(disfluency/repetition QA、Std 6%減速の適用と未適用ガード、Local Rewrite/Connected Speechのrole、AUW、値ガード)を受けることをsegmentごとに検証。共有moduleを変更する場合はX/Z出力のbyte一致回帰。
3. M4: 同一run内再利用の照合keyにTTS Voice名を追加(Y側の薄いラッパー、X関数は無変更)。Master Audio Storeは`speaker_voice`をkeyに含むため影響なし。
4. scope限定リテラルへ"Y"追加(`er103_proper_noun_alarm_policy_01.py:42`・`er109_xz_scope_01.py`等、技術対応。実装時にer109の最終Statusを確認)。
5. Y用timeline builder・試聴ページ(標準フォーマット、`render_standard_page`)。Voice人物名は内容ラベル(「人物1: 中学校で国語を教える教員[男性の声]」等)として表に載せ、内部ID・Style内部情報は載せない。
6. AUW(統一ASR判定)・値ガード・HR Lock・3層ASR・Audio Validation Gate・Master Audio Store・resume/retryはXの共有部品をそのまま使い、上限回数・安全装置は回避しない。

## 4. 評価項目(ユーザー試聴で確認)
(a)3人の意見を自然に聞き分けられるか(声の差で聞き分けられるか、自己紹介文だけでも分かるか) (b)PD06(Full Story style)が人物Voiceを語り手化・平板化しないか(S9) (c)R0gとR2gのどちらが聞きたくなるか (d)Stdの尺(語数がXより+6〜24%)と6%減速の影響 (e)Audio Validation Gate全PASS・HR Lock 0。

Comment 4あり/なしのA/B比較は、Comment 4廃止がユーザー決定のため**行わない**(設計書の旧計画から除外)。

## 5. 費用見積(推定。本Trialの英語語数と設計書§⑦のX実測から)
- 1候補(Std+Adv): TTS 約14〜17円 + ASR(3層)約7〜14円 = 約21〜31円(X実測の11〜13円/6〜11円を、Y語数+25%で補正)。Voice別TTSは同モデルで追加0、試聴ページ等は約0。余裕を含め **約25〜38円**。
- 2候補(R2g+R0g): **約50〜76円**。
- 通算(本委任146.28円 + Phase 3): 1候補で約171〜184円、2候補で約196〜222円 → **上限250円以内**。Pro TTSが必要になる場合(+12〜18円/セット推定、設計書§⑥ D3)は追加費用を伴う仕様変更のため**実行前にFableへ報告して再判断**(無断で行わない)。上限250円超過見込みの場合も実行前に停止・報告。
- 実装(Y runner・parity test・scope追加)は音声API費用ゼロ。X/Z出力のbyte一致回帰+全回帰を伴う。並列化: Y runner実装(a)、parity test(b)、scope追加と試聴ページ(c)は独立に先行可能。生成は本文Std/Adv×候補の複数process並列が可能(条件同一性を保てる)。

## 6. STOP/判断候補(Phase 3開始前にFableが確認)
- Std Voice partの6%減速: Xは全FULL_STORY減速(part3は検知ガードの穴=OPEN-466)。Zは会話の減速撤去/Adv約6%高速化(OPEN-462、Zのみ)。Yは人物の語りだが「会話」ではなく独白のため、**X準拠(Std全5パート減速)で生成し、速度は試聴で判断する**を既定とする。Z v2の考え方をYのVoiceへ適用するかは新仕様候補(判断候補)。
- Voice 1/3が同じ男性的な声質(Algieba/Schedar)で聞き分けにくい場合は、固定割当(ユーザー決定)の変更になるため**勝手に変えず**結果を添えて報告する。
