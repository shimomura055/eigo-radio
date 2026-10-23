# OPUS_REVIEW_REQUEST_01: Family Y(Voices型)基本設計案 独立技術レビュー依頼

管理ID: FAMILY-Y-VOICES-DESIGN-01 / 2026-10-23 / 条件A(新しい構造・処理フローの設計)に該当(PM_GOVERNANCE 11-3)
レビュー対象: `docs/research/FAMILY-Y-VOICES-DESIGN-01/DESIGN_PROPOSAL_01.md`(入力: `INVENTORY_X_Z_SPEC_01.md`、`INVENTORY_OLD_B_VOICES_01.md`、ユーザー原文`docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER.md`)
性質: DESIGN/RESEARCH ONLY。Trial・API費用・Production変更なし。本レビューはユーザー承認Gateではない(Fableが照合し、11-3のSTOP条件に該当しなければ次工程へ進む)。

## 設計の要点サマリ

1. 基盤=Xの承認済みProduction経路。Yは「5パート(リード/Voice1〜3/Tension+Closing)・3 Voices・Voice編集思想」だけを追加。旧BのProductionコード・registry・入口・命名は転用しない。
2. マトリクス: 確定(ユーザー決定)8 / A継承29 / B旧B承認済み継承17 / C不継承13 / D判断4。
3. 処理フロー: Research→Ledger→**Y版B3(3視点候補+Voice別背景fact割当)**→**Voice Card生成(AI 1回、9項目、数値欄なし、`not_my_point`欄)**→**Y Writer R0のみ(日本語、5段落契約)**→**Leakage Check(日本語原稿1回)→局所書き換え(計3回上限)→Acceptance Gate**→忠実英訳→RF→A2簡易化→RF→In One Line/Preview/Comment1〜3/KP→TTS/ASR/検査/Assembly。
4. 実装方針: X runnerは触らず、Y用の薄い入口を新設し共有部品を再利用。segment_idは`full_story_part1〜5`(`--only-segments`正規表現は既に通る、`resolve_narrative_role`のpart4/5追加のみ)。
5. ユーザー判断(推奨付き): D1 最終パート(再定義なし+末尾1文の余韻、Comment 4廃止) / D2 Voice Card半自動生成 / D3 人物別TTS Voice(Z正式表の決定論関数再利用) / D4 R0のみ(R1/R2不使用)。
6. 費用(推定): X実測±約6円/セット(定常平均約70〜81円)。D4で-9〜-11円、Card/Leakage/局所書き換えで+5〜12円。Pro TTSが必要な場合のみ+12〜18円。

## レビュー論点(観点別。各論点に対し「問題なし/要修正+理由」を判定してください)

### 1. 旧Bの品質NG再発
- 1-1. **日本語先行チェーン(日本語→忠実英訳→A2簡易化)で一人称の人物性が平板化しないか**(旧Bは英語直接生成だった。Xの三段をYにそのまま使う設計が妥当か。人物性が日本語段階で決まる前提でよいか。簡易化指示に口調保持の文言がないが追加すべきか)。
- 1-2. **Leakage Checkを日本語原稿に対して1回だけ実行する設計**: 旧Bの項目(特に`leak_discovery_syntax`は英語構文依存)の日本語移植は妥当か。英訳後(Adv英語)で検査する案と比べた是非(是正時に再翻訳が要る代わりに、実際に聞く英語を検査できる)。
- 1-3. **F4(whack-a-mole)対策としての局所書き換え**: 該当パートだけ書き換え→全体再検査で、別Voiceに再発する問題を避けられるか。パート間の依存(最終パートが書き換え前のVoiceを参照している場合)の扱い。上限3の維持は妥当か。
- 1-4. **意味レベルの立場重複(§6(2))の抑え**: Voice Card相互排他設計+`not_my_point`+Trial人手評価だけで十分か。承認済みgateがない(C07/C08)ため、設計で足りない場合の最小の追加案があれば示してほしい(追加は採用判断=D扱いになる)。
- 1-5. **事実創作(§6(5))**: Writer規則+Card制約+RF(事後・非停止)のみで開始し、発生率をTrialで実測する方針は妥当か。X思想(内容理由のretry撤去)と、旧B承認済みAcceptance Gate(内容理由のSTOP)の併存に矛盾はないか。

### 2. 継承漏れ
- 2-1. X側で承認済みだがYに必要な仕様の見落とし(特に: segment_id固定を前提にした検査・Local Rewrite・disfluency/repetition QAの範囲、`key_phrase_source_gate`、`style_profile_gate`、U-1来歴、HRページ、routing/pricing)。
- 2-2. 旧B承認済みで継承すべきなのにC(不継承)にした項目の有無(C04 保守版Fact Safety、C05 A'、C06 外部制約統合、C10 Evidence Compression Editor)。
- 2-3. 「承認原文がXのみ」項目(丸め判断、RF)をA継承(開示)とした扱いの妥当性。
- 2-4. er109/PNAPのscope("Y")追加を技術対応として扱う運用が28-1運用7に照らして妥当か。

### 3. 不要な複雑化
- 3-1. Voice Card 9項目は多すぎないか(さらに削れるか)。Card生成を独立callにせずY版B3へ統合できないか(-2〜4円、ただしB3契約V1〜V10への影響)。
- 3-2. Leakage Checkの7+最終パート項目は日本語・3V・Y構造に対して過剰ではないか。
- 3-3. Y用の新runnerを作る方針(X runnerを触らない)と、`full_story_part1〜5`で共有関数を再利用する方針が、将来のX/Z/Y共通化(OPEN-354/355/415)と衝突しないか。
- 3-4. D1の「Comment 4廃止」「再定義なし」が、リスナー体験(締まり)に対して過剰に削っていないか。

### 4. QCD
- 4-1. §⑤の費用推定の前提(R1/R2 call単価、Leakage/Cardの単価、局所書き換え確率)に無理がないか。
- 4-2. R0のみ(D4)の品質リスク。「面白さ」をVoice Cardだけで担保できるか。OPEN-217の根拠(n=1 Trial)の強さに対して決定が早すぎないか。
- 4-3. 人物別TTS Voice(D3)について、flash-lite TTSで非Aoede Voiceの品質が保てる見込み(Z Dialogueのみ別モデル=Pro系を使っている理由が品質面だとすると、費用+12〜18円の前提が現実的か)。
- 4-4. 最小Trial(段階1テキスト→段階2音声、上限150円、1テーマ)は、§6(1)〜(6)を判別するのに十分か。

## 付: 既知の未確認事項(設計の前提)
- 01B §12の未確認(Trial-06基準の恒久規則化有無、一人称pov_checkの常設Gate有無、3V保守版ゲートのruntime evidence)、01A §12(`TTS_EXECUTION_MODE`実運用、er109最終Status、Std 6%減速のsegment範囲)。
- ユーザー希望のY総尺は原文に記載なし(X実測帯を基準に配分)。
