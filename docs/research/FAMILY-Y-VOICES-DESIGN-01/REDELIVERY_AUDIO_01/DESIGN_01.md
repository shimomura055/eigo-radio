# DESIGN_01 (委任_27 Phase 0: 『宅配の再配達は有料にすべきか?』音声化Trial 処理フロー設計。API 0)

作成: 2026-10-25。DEV/Trial専用。Production正式採用・配線なし(`production_reachable=False`)。新しい処理フロー・Validator・組立方式・Voice選定方式・Style変更は**作らない**(EXISTING_SPEC_CHECK_01 §2)。実装=`er110_family_y_redelivery_audio_01.py`(薄いglue)+`er110_family_y_redelivery_page_01.py`(ページ)+test 14件PASS(API 0)。

## 1. 処理フロー(全体像と並列化)
```
[無料] R0読込・sha一致確認(gate最終本文=article_ja.md、Gate PASS)
[有料 1] リード生成(1 call) と Tension+Closing生成(1 call、Voice本文を読取り専用で入力) は独立
         → Tension Leakage Gate(6項目、既存、判定上限3) → 日本語5パート原稿(article_final.md、タイトル+5段落)
[有料 2] 英訳: Adv忠実英訳+In One Line → Std A2簡易化(Advから) → 5段落契約・一人称契約(既存) → 監視Leakage(記録のみ) → 5パート対応確認(決定論)
[有料 3] scaffold: Comment1〜3/Preview/日本語タイトル/Key Phrase(Adv英語解説・Std日本語意味)
[無料]  権利確認(出典との連続一致) ← 英訳完了後
[有料 4] 音声: TTS(Adv・Std)→ ASR検査 → KP音声 → 局所Rewrite/retry/fallback(既存上限) → Y style gate → 組立(Std・Adv・Std voice_noslow参考)
[無料]  QA集計・Voice聞き分け実測(F0・重心・話速) → 試聴ページ(限定共有) → HTTP 200確認 → COMPARISON/QA/TRIAL_RESULT/ISOLATION
```
- 並列化: リード/Tension+Closingは独立だが各約1〜2円・待ち時間短縮は約1分のため、cmd_ja内の逐次(resume対応)とし、API 0の権利照合・ページ・QA集計の準備を有料run待ちの間に先行して進める。音声はAdv・Std各レベルのTTSをX共有関数が直列処理する(直列化規則・同一Master Audio Storeの競合回避・並行agentのTTS稼働確認を尊重するため、レベル間の並列起動はしない)。
- 直列の理由: 英訳はJA原稿に依存、scaffoldは英語原稿に依存、音声はscaffold(KP・Comment)に依存(前工程出力依存)。

## 2. 日本語5パート原稿(R0は再生成しない)
| パート | 内容 | 出所 | 検査 |
|---|---|---|---|
| 1 リード(Aoede) | 具体的な場面か問いから始め、3人の声を並べると予告(約70〜100字)+R0の開示文(逐語) | 生成1 call。仕様は`y0.Y_R0_HEAD`のリード行を逐語抽出(複製しない)。開示文はR0 article_ja.mdの文を逐語後置 | 決定論(一人称なし・取材系表現なし・数字なし・です/ます調なし・字数)。リードにLeakage項目はない(既存仕様)。失敗は1回再生成→STOP |
| 2 Voice1 現役ドライバー(Algieba) | R0 voice_1 **無変更** | gate最終本文とarticle_ja.mdの一致を実行時に確認 | R0で通過済みLeakage Gate(PASS) |
| 3 Voice2 共働きの受取人(Zephyr) | R0 voice_2 無変更 | 同上 | 同上 |
| 4 Voice3 受取方法を工夫する受取人(Schedar) | R0 voice_3 無変更 | 同上 | 同上 |
| 5 Tension+Closing(Aoede) | 共通前提→3人の違い(具体物で対比)→食い違い/重なり→締め1つ(聞き手が自分の生活から答えられる具体的な問い) | persona版`generate_tension`(Opus確認済みの規則)。共通前提と規則内の例文だけprocess内で差替え(ファイル無変更)。入力=Voice本文(読取り専用)+PERSONAS_05由来のラベル・主張の要点・R0本文に出た具体物 | persona版Leakage Gate(6項目、luna high、局所書き換え、判定上限3、`LEAKAGE_RESIDUAL_STOP`あり) |
- 人物像・立場・主張・口調は変更しない(Voice本文は無変更。Tensionの入力ラベルもPERSONAS_05 §1の記載のみ)。新しい事実・数字・出来事を作らない(Tension規則・リード規則に明記)。
- 5パートの契約検査: `y0.check_contract`(段落数5・Voiceの一人称・ナレーター段落が一人称で始まらない)。

## 3. 英訳(Family X承認方式)
- Advanced: `adv_gen.generate_family_x_faithful_translation`(忠実英訳) + `efam._advanced_in_one_line`。**話者保持**はOF-Y3-01(b)のmust_fix欄(persona版の5パート版、段落番号のみ差替え、A2 Prompt本体は無変更)。新事実追加禁止の1文を同欄に付記(新規Prompt追加ではなくmust_fix欄の内容)。
- Standard: `std_gen.generate_family_x_standard_a2_no_heading`(Advanced英文からA2簡易化)。同じmust_fix欄を渡し、人物の個性・意見を不必要に削らない。
- 5段落契約(`y0.check_en_contract`)違反=段落数のみ1回再生成(既存方式)、それ以外は停止。
- 英語Ledger: 意見ベースのため検証済み事実台帳がない。`LEDGER_PLACEHOLDER`(「事実台帳なし。数値・統計・制度の事実主張を新たに述べてはいけない」)を渡す。IOLが事実を足さない保険。
- **5パート対応確認(`mapping_check`、決定論・記録用・Gateにしない)**: 日本語/Adv/Stdの3言語で、段落数5、段落2〜4の一人称(私/わたし/僕、英語はI/my系)、段落2〜4に各人物固有のアンカー語(V1=不在票・送料・料金全体 / V2=午前・夫・指定 / V3=営業所・ロッカー)が出ること、段落1・5が一人称で始まらないこと。V2とV3の取り違えをtestで検知できることを確認済み。英語アンカーの取りこぼし(誤検知)は目視で最終判断し、COMPARISON_01に原文を無編集で置く。
- 3人の人物像・主観性の保持(ユーザー§9-2): COMPARISON_01で日本語R0とStd/Adv全文を対応表で示す。機械指標(一人称語数・疑問符・文長の差)を`en_monitors.json`に記録(記録のみ)。

## 4. Voice割当・TTS(既存継承、新Trialなし)
- V1=Algieba(男)、V2=Zephyr(女)、V3=Schedar(男)、リード・Tension+Closing・In One Line=Aoede(ナレーター)。Z正式表の`assign_dialogue_voices(roster)`の結果とユーザー決定(#163 D3)の固定割当が一致することを実行時に機械確認(不一致なら停止=Voice方式を変えない)。V1/V3は男性別Voiceで、聞き分けはF0・スペクトル重心・話速の実測で記録(過去の同Voice組=F0差1.9〜2.6半音[OPEN-463 委任_05]を参考値)。
- 速度・Style・TTS設定: fx_20261017 profile(PD06)・speech_metadata_flash_lite・Std本文6%減速・語り手切替pause 0.8秒は既存moduleが適用。Pro系TTS・Style変更・新Voice選定はしない。過剰な演技・ニュースナレーター化の評価は耳で確認(Fable/ユーザー)、Style自体は変えない。
- 実装: `er110_family_y_audio_trial_01.py`をprocess内で`BASE/SRC/OUT_ROOT`だけ差替え(with内、finallyで復元)、`--cand r0`で呼ぶ。Master Audio StoreはProductionのsnapshot copy(Trial名前空間)、Local Rewrite recoveryは`er110_output/...`配下に付替え(既存実装、OPEN-493)。

## 5. 音声検査(新しい5パートでも漏れなく)
| 検査 | 適用箇所 | 備考 |
|---|---|---|
| TTS/ASR承認済み検査(統一ASR) | 全segment(topic_intro/日本語タイトル[Std]/Preview/Comment1〜3/本文5segment/In One Line/KP) | X共有関数が内部で実行 |
| Repetition QA(method D') | 本文5segment(`enable_repetition_qa`) | 偽陽性HR Lockは迂回しない(OPEN-469は別管理) |
| Connected Speech / Pronunciation Resolver | 本文5segmentはalias IDによりFULL_STORY扱い(既存testでresolve確認済み)、Adv Previewも | `connected_speech_enabled_for` |
| disfluency QA | In One Line・Previewほか | 既存 |
| KP音声検査(canonical・3条件) | KP英語・Adv解説・Std日本語意味 | `_generate_key_phrase_segments_b1/a2` |
| 発音Ledger | 固有名詞(今回ほぼ無し) | 共有ledgerを参照。書込みがあれば隔離証跡に記録 |
| 速度・ポーズ | Std本文`slowdown_applied`確認(5segment+In One Line、Y版Gate)、Adv Style prefix確認(minimal_fallback禁止)、pause値は既存timeline | `y_style_gate` |
| 不自然さ | 試聴(Fable/ユーザー)+機械指標(長さ比、話速、無音) | 新Gateは作らない |
| retry/fallback/局所Rewrite | 既存上限。局所Rewriteが発動したら書換え前後の本文を取り、**一人称・立場・口調の保持**を目視確認(QA_RESULT_01に記録) | 発動時はLOCAL_REWRITE_RECOVERY/ADV_MINIMAL_FALLBACKでY style gateがBLOCKする既存挙動に従い、人間確認が必要なら停止して報告(HR Lock迂回なし) |
| Audio Validation Gate(組立前) | 各level | 既存 |
| 安全上限・STOP | `stop_scope_check_01.py`(開始時・有料run前)、再起動規則(150秒・RESTART_STORM)、予算Cap | §7 |

## 6. Production隔離
- 出力先は全て`er110_output/family_y_redelivery_audio_01/`・`docs/research/.../REDELIVERY_AUDIO_01/`・`user_test/family_y_redelivery_audio_01/`。Production run dir・Master Audio Store・公開ページへ書込まない。
- 隔離証拠(ISOLATION_EVIDENCE_01): (a) Production store(`er006_output/master_audio_store_01/manifest.json`)のsha256を有料前後で比較(並行agentが書込む可能性があるため、変化した場合は私のTrial store/ログと照合し、私の起動に起因しないことを示す)、(b) `y_entry_point.json`の`production_reachable=False`、(c) 共有`pronunciation_ledger_01/ledger.json`のsha前後、(d) `git status`で既存tracked `.py`変更0、(e) sink付替え(Local Rewrite recovery出力先)確認、(f) test: `--paid`と承認ファイルが無いと全cmdが例外で止まり副作用0、env/flag経路なし、Production参照0=`er110_family_y_redelivery_audio_01_test_01.py` 14件PASS。
- Production到達経路に入る未承認機能: **なし**(本moduleはDEV専用で他からimportされない。flag/環境変数なし。X/Z Production .py・Prompt・閾値・辞書は一切変更しない)。

## 7. 有料run管理
- 開始時と有料run前に`tools/stop_scope_check_01.py --managed-id FAMILY-Y-VOICES-DESIGN-01 --run-dir <run>`(開始時 rc=0 取得済み: `er110_output/family_y_redelivery_audio_01/stop_check_fyt27_start.json`)。
- 起動は段ごとに1回(ja / english / scaffold / audio tts / audio assemble)。同一コマンドの再起動は150秒以上空け、原因不明のrc≠0が2回続いたら即STOP。監督ループ・自動再試行ラッパは作らない。
- TTS起動前に`other_tts_processes()`で他agentのZ/X TTS稼働を確認し、稼働中なら待機(他processは終了しない)。
- 磨き込みTrial禁止。既存基準を満たした時点で完成。
