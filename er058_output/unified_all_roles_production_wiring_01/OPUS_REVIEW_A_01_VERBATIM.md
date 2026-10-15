# Opus独立技術レビュー原文(11-3 条件A、2026-10-15、opus-consultant=claude-opus-5-5、逐語保存・改変禁止)
対象: DESIGN_01.md(commit 3953de4ff)。本文は採点者セッションログからスクリプト抽出(委任_02a)。

## Opus独立技術レビュー結果: ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 DESIGN_01(11-3 条件A)

コードは読むだけで、実行・編集はしていません。API呼出 0、費用 JPY0。行番号は現在のworking treeで確認した値です。Production採用の可否は判断していません。

**総括**: 設計の骨格は承認仕様に沿っており、妥当です。骨格とは、2関数のadapter化、保護差ではSecondaryを呼ばないこと、最終ANDゲート、Secondaryを1回にしてキャッシュすることを指します。ただし次の2点が未定義または計画上の欠陥で、「誤PASS防止」と引き換えに「誤NG→再生成3回→HR滞留」(日本語はLRがないため直撃)を新たに生みます。
- 値ガードの判定意味論(どういう場合にDIFF/AMBIGUOUSとするか)
- 配線順序(ロールアウト)

このため、BLOCKER 2件を設計に追記・修正してから委任_02に入ることを推奨します。

---

### 1. 所見

#### BLOCKER

**OF-AUW-01 値ガード `compare_values` の意味論が過剰に厳しく、誤NGで完成物が出ない経路がある(観点11)**

根拠:
- DESIGN_01.md:354(欠落・追加はDIFF)、:359(確定できなければAMBIGUOUS)、:282(AMBIGUOUSは保護差でSecondaryを呼ばない)、:292(最終ANDゲートをPrimary PASSにも適用)
- `er066_..._trial.py:45-51,96-98`: `has_ambiguous`は文単位の判定
- `er066:76-82`: 〇を含む表記は値化しない
- `er007_ja_asr_validator_01.py:256-283`: 現行は「数字なし⇔かな」を`_reading_equal`で許容している
- `er006_preprod_hardening_01_validation.py:1063-1069`: `HOMOPHONE_MATCH_NUMBER_EXCEPTION`(承認済み)
- `er021_...:61`: Tier1は"one"を数値atomとして扱う

誤NGになる具体的な入力パターン:
- **JA かな数詞**: 原稿「一人で」とASR「ひとりで」、「一つ」と「ひとつ」、「二十歳」と「はたち」。原稿だけに値があるので「欠落=DIFF」となり、NG_PROTECTED→Secondaryを呼ばない→3NG→HR。現行は読み一致でPASSしているため退行です。
- **JA 曖昧語が無関係に混ざる文**: 「十分な」「一時的に」「3分の1」を含む文で、別の箇所に差分があるだけでも、文単位のAMBIGUOUSにより保護差になり、Secondaryが呼ばれません。「十分」と「充分」のような表記差も同様です。
- **JA 漢数字の位取り表記**: 「二〇二六年」とASR「2026年」。原稿側が値化されず「追加=DIFF」になります。「1万2000人」と「一万二千人」、「数十人」「十数人」も未検証です。
- **EN**: "one"の脱落・挿入がDIFFになります。"for"→"4"のような承認済みの`HOMOPHONE_MATCH_NUMBER_EXCEPTION`は、最終ANDゲートで「追加=DIFF」となり取り消されます。Tier1が片側だけ構文解析に失敗した場合もDIFFになります。Tier1はもともと受理専用の早期判定で、非等価のときはNoneを返して既存の分類へ戻す設計であり、拒否側に流用する前提になっていません。
- **内部矛盾**: :282と:361、:381、:395(5a)で、AMBIGUOUSのときに「Secondaryを呼ばない」と「Secondary EXACTならWARNING」が両立していません。

修正案:
- 判定を `{NO_VALUES, EQUAL, DIFF, AMBIGUOUS, UNKNOWN}` の5値にする。
- **DIFFは積極的な証拠がある場合だけにする**: 対応する位置の両側atomが値化でき、値または単位が異なる場合。または片側の値に対応する相手側spanに数字・数詞・かな数詞のいずれも無い場合。
- 構文解析できない・片側だけ値化できない場合はUNKNOWNとし、既存のprotected_check判定と読み一致判定に委ねる。
- AMBIGUOUSは**位置単位**で、両側の表層が異なる場合だけにする。同一表層ならEQUALとする。
- AMBIGUOUSのときはP3としてSecondaryを呼び、Secondary転写が原稿と同一表層の場合だけWARNING(`NUMERIC_AMBIGUOUS_SURFACE`)とする。
- 最終ANDゲートは「承認済みラベルが根拠としたequivalenceを再否定しない」ようにする。`HOMOPHONE_MATCH_NUMBER_EXCEPTION`、Tier1 diff-anchored、読み一致が対象。
- 上記の全パターンを§5-7のテストに追加する。

影響範囲: 全JA Section(LRなしなのでHRへ直行)、EN最終ゲート、§8-3の受入条件。

**OF-AUW-02 ロールアウト順序: flagなしで段階commitすると、中間状態がProductionで有効になる**

根拠:
- DESIGN_01.md:539: 委任_02で`_is_number`(#4)とJA数字分岐(#5)を変更しつつ「挙動不変(未配線)」と書いている。しかし両者はProductionの判定本体そのものなので、commitした時点で有効になります。
- :540-541: EN配線(_03)が試聴リスト・ページ連動(#18、_04)より先に入る。この間に本番runがあると、WARNING音声がリストに載らないまま自動採用され、原文§2の「自動登録」に違反します。V04 L159-164の前提条件にも反します。

修正案:
- 02〜05は作業branchで実施し、Integration・Regressionがすべて通った時点でmainへ**1回だけmerge**する。revert単位もこのmerge 1つにする。
- branch運用が難しい場合は、registryとページ節を_03に前倒しし、#4と#5は配線と同じcommitに移す。

影響範囲: 安全性(原文§2)、ロールバック、並行して動くE2E。

#### MAJOR

**OF-AUW-03 判定点11箇所の一覧から、引継ぎ・再利用の経路が漏れている**
- 根拠: `er019_family_x_validation_inheritance_01.py:180-192`(`try_inherit_from_cached`→`REUSED_VALIDATED`)、`:205-227`(`classify_asr_match`で直接再判定)。呼出元は`er019_family_x_audio_production_runner_01.py:620,661`。Master Storeの再利用は既に要確認とされています(DESIGN :321)。
- 問題: 旧判定で合格した音声(25%→26%の穴や旧JA `\d+`判定の時代のもの)が、値ガードを通らず、WARNINGも引き継がれずに採用されます。受入条件#1、#2、#7が成立しません。
- 修正案: 引継ぎ時に保存済みASR転写へ最終ANDゲートを適用する(API 0)。保存済みラベルからWARNINGを再導出する。判定点の表に「J11 引継ぎ・再利用」を追加する。

**OF-AUW-04 静的監査(AST)の対象範囲が「主要10ファイル」に依存している**
- 根拠: DESIGN :161、:181。
- 修正案: 各runnerのentrypoint(er019、er063、er026、er012_b、er013、er012_e、n3_tts)からimport graphをたどり、到達するmodule内の `transcribe` / `classify_asr_match` / `classify_ja_asr_match` / `val.evaluate_attempt` / `evaluate_attempt_*` の全呼出をallowlist方式で検査する。J7(`n3_tts.py:196`)のように`classify_*`を直接呼ぶ箇所や、OF-AUW-03の箇所はallowlistに理由付きで載せる。

**OF-AUW-05 Melos Regressionの再判定はAPI 0だけでは完結しない**
- 根拠: `clip_results.json` L1754-1860。segment_id=None側の1件は**primary_2**でM1受理されており(EVIDENCE_RUN_01.md:16)、Azure転写は保存されていません。
- 問題: Primary#2を廃止すると、この観測は保存データだけでは判定できません。「12/12」(原文§4の基準)を再現できない可能性があります。
- 修正案: Azure転写が保存されていない観測は、保存wavに実Azureを1回だけ当てて判定する(1件あたり約¥0.1)。§8-3の期待値を「統一フローでの12/12」として再定義する。12/12を割り込んだ場合は、原文STOP条件「既存品質の悪化」としてFableが判断する。

**OF-AUW-06 LR後v1へのforce_secondary適用は、既存保護の継続ではなく拡張になっている**
- 根拠: `force_secondary=True`の箇所はProduction内で`er003_v1_crosslevel_audio_02_common.py:351`(A2 minimal経由)だけです。voice01:359とnews_tail_fix:368のLR再TTSには適用されていません。設計 :326 は全LR v1へ適用します。
- 問題: 原文§6「Rewrite後は同じ統一ASR判定を適用」、§2「Primary PASSならSecondaryは不要」、§5「例外を勝手に増やさない」と競合します。V04 2-7の(A)/(B)/(C)はユーザー判断事項で、D-5は決定記録なしです(REDETERMINATION_CHECK_01.md:108)。
- 修正案: **U(ユーザー判断)へ格上げ**する。回答までの暫定はA2だけ現行維持、B1は統一判定と`LR_REWRITTEN`のWARNINGのみ。推奨は「LR v1はPrimary PASSでもSecondaryで確認(A)」です。対象が少なく、Coffee part2 #5の実例があるためです。

**OF-AUW-07 LR発火条件⑤(合意誤読)の定義が内部で矛盾している**
- 根拠: DESIGN :324。判定に「canonical側の差分spanの一致」を使うと、Mello/Mallowは同じspan(Melos)なので「合意」と判定されます。一方、同じ段落の例示では「LRしない」としています。
- 修正案: 判定式を明文化する。たとえば「両エンジンのASR側の語が一致する、またはARPAbet距離が閾値以下」とし、Melosの転写で単体testを置く。

**OF-AUW-08 JAのUNCERTAIN Cascadeの受理集合が黙って縮小される**
- 根拠: 現行は`er007_ja_secondary_asr_01.py:486,490-493`で、Secondaryの`should_pass`(PHONETIC_MATCHを含む、`er007_ja_asr_validator_01.py:502`)と`ORTHOGRAPHIC_VARIANT_CONFIRMED`(2エンジン)で受理しています。設計 :294 はJA SecondaryをEXACT/NORMALIZEDだけに限定し、`ORTHOGRAPHIC_VARIANT_CONFIRMED`には言及がありません。
- 修正案: 縮小すること自体は安全側です(V04 L126のPHONETIC誤PASS実例がある)。ただし承認済み経路(OPEN-145)の変更なので、**R+**としてDECISION_LOGに記録する。`ORTHOGRAPHIC_VARIANT_CONFIRMED`はPrimary#1とSecondary#1の2エンジンで維持し、test化する。

**OF-AUW-09 費用の計測とCOST_GUARDが実態と合っていない(QDC)**
- 根拠: `er006_secondary_asr_01.py:702,878,916` ではAzure 1回を$0.00001と仮置きしています。実単価は約¥0.0444/秒(`er007_ja_secondary_asr_01.py:89-91,311`)で、40秒なら約¥1.8です。
- 問題: COST_GUARD($0.05、L243)は実質的に発火しません。Secondaryの対象を「通常の内容語差」まで広げると、長いsegmentではAzureがTTSやPrimaryより高くつく可能性があります。§9の「量産費は低下見込み」には根拠がありません。
- 修正案: 共通judgeでは秒数ベースの`est_jpy`(SCGと同じ式)を使う。COST_GUARDの再校正、または「現状無効」と明記する。_06の前に、過去の`attempt_history`のNG分布から1記事あたりの増分を試算し、15-9(70円)と照合する。

**OF-AUW-10 HR_TECHが新しい状態になっており、Secondary障害時の処理が詰まりやすい**
- 根拠: DESIGN :285、:302。`er011_human_review_lock_01.py:106-107` の`VALID_STATES`にHR_TECHはありません。
- 問題: Azureが全体的に障害を起こすと、全segmentがHR Lockに入り、人間の承認待ちが大量に発生します。
- 修正案:
  - HR_TECHはLock状態に追加せず、「技術STOP(再実行で再開可能、承認不要)」として記録する。
  - run単位のcircuit breakerを置く(例: Azure取得不能がsegmentをまたいでN回続いたらrunを停止して報告し、TTSを無駄に消費しない)。
  - SecondaryCacheには失敗結果(None)を保存しない。

**OF-AUW-11 test入力と受入基準の不足**
- 根拠: DESIGN :388-403、:504。
- 修正案:
  - 原稿はProductionと同じ前処理(`tts_safe_news_en`、`tts_safe_number_words_en` で2〜12を数字化するもの、`n3_tts.py:843-894`)を通した形でtestする。
  - 新旧の再判定表について、受入条件を「誤PASS新規0」だけでなく「PASS→NGに変わった件を全件確認し、意図しない件は0」に拡張する。これは観点11の誤NG側の歯止めです。

**OF-AUW-12 KP英語解説がmax_attempts=2のままで、受入条件#4(最大3回)と合わない**
- 根拠: マトリクスX-B1-07(`er019:700`)。また X-B1-06 は「USER確認」、C-B は「R」と記述が食い違っています。
- 修正案: 2回がユーザー決定で定められているかをSSOTで確認する。決定がなければ、例外として維持せず3回に揃える(R)。文書内の不一致も直す。

**OF-AUW-13 ロールバック手順に検証がない**
- 根拠: DESIGN :454。_03、_04、_05は同じファイル(er011 lock、n3_tts、voice01)を触るため、単独revertでconflictが起きる可能性があります。
- 修正案: OF-AUW-02のbranch・単一merge方式を採る。Gate 4で `git revert --no-commit` の予行と旧testの再実行を行う。追加したデータ(attempt_historyの新キー、manifestの`asr_judgement`)を旧コードが読み飛ばせることもtestする。

#### MINOR

- **OF-AUW-14**: EN SecondaryのPhraseListについて、マトリクス(:189等)の「PhraseListなし」と§4-5の「維持」が矛盾しています。キャッシュを1本化するなら「維持」が整合的です。V04 L69(PhraseListなし)からの逸脱として、理由とともに記録してください。
- **OF-AUW-15**: legacy A/B/Cで「JSONのみ」とすると、ユーザーが事後に試聴できる状態になりません。registryの`render_html_section`で単独HTMLを出力するのが低コストで、U判断を回避できます。
- **OF-AUW-16**: slot3の保護差NGでは、HR資料用にSecondaryを1回だけ診断目的で呼ぶ案を検討してください。PASS根拠には使いません。
- **OF-AUW-17**: 新しいラベル(`NUMERIC_VALUE_EQUIVALENT_MATCH`、各`state`)を、下流のGate、ページ、集計のallowlistやcount処理が認識できるかをGrepで確認してください。
- **OF-AUW-18**: Primary ASRの障害(None)でTTS attemptを消費する現行挙動は、OpenAI障害時の無駄打ちになります(V04 S6)。今回の範囲外ならOPENに記録してください。

### 2. §11 論点への回答

1. **修正(骨格は同意)**: 保護差でSecondaryを呼ばない方針は、原文§3末尾の優先規定に合っています。「両エンジンの一致を条件にPASS」とする案Bは、「単純なSecondary一致だけで誤PASSさせない」に抵触するため**反対**です。ただしOF-AUW-01の意味論の修正が必須です。AMBIGUOUSはSecondaryを呼び、表層EXACTの場合だけWARNINGとする形に統一してください。最終ANDゲートを重ねる考え方は十分ですが、承認済みequivalenceを打ち消さないように範囲を限定してください。
2. **同意(条件付き)**: adapter方式に賛成です。条件は次の4点です。
   - `attempt_ctx`未指定時の旧呼出元の既定動作を明文化する(HRログ書込みの有無)。
   - M1の相互参照(`secondary_text`)を保持する。
   - `detail_out`のキー互換をgolden比較testで確認する。
   - Trial系の旧呼出元の挙動が変わることを記録する。
3. **修正**: 言語別の許容集合は同意です。ただしJAのUNCERTAIN経路はOF-AUW-08のとおり明示が必要です。PhraseListは維持し、その旨を記録します(OF-AUW-14)。Primary#2とS#2の廃止には同意しますが、OF-AUW-05の影響測定が条件です。「2連続でHR_TECH」はOF-AUW-10の形に修正してください。
4. **同意**: 原文§2が明示しており、ER-008の置換はR+で妥当です。ただし固有名詞型では「TTS 3回+cool-down 600秒+LR判定」の時間コストが増えます。D-14(cool-down)は未決のまま現行維持とし、`NG_BOTH(entity)`件数と所要時間をtelemetryで取得してください。
5. **修正**: OF-AUW-06(force_secondaryはU)とOF-AUW-07(判定式の矛盾)を直してください。標準Prompt化、再TTSの計数、JA・KP・見出し・DialogueをLR対象外とする点は同意です。
6. **同意**: B0で十分です。Dialogue(Std)とVoices A2に外側ループを足すのは、既存A2全体の整合の範囲内です。ただし外側ループと内側ループの合計が通算3回になることと、Review Lockの「RESOLVEDはブロックしない」特例との関係をtestで確認してください。OPEN-76/270の原文は未照合です。B′は不要です。
7. **修正**: 値ガードはStage 1だけを昇格させ、読み展開は含めない線引きに同意します。OPEN-334の同時解消も同意します。ただし前提として、OF-AUW-01(かな数詞・〇の位取り・位置単位の曖昧判定・UNKNOWN)が必要です。`_is_number`の拡張は、55件のテストと受入条件の拡張(OF-AUW-11)で回帰を確認してください。
8. **修正**: `tts_generation_results.json`から導出すること、非ブロッキングにすること(C-H R+)には同意です。追加で次の3点が必要です。
   - 引継ぎ・再利用の経路の警告を継承する(OF-AUW-03)。
   - legacyでも単独HTMLを出す(OF-AUW-15)。
   - run途中のSTOPでも、それまでに採用した音声のリストは出力する。

### 3. 競合一覧(§6)の評価と見落とし

- **C-A1〜A3はR、C-A4(C2)はR+、どちらも妥当です。**
- **C-A5/A6をUとすること**: 結論は妥当ですが、事実の整理が必要です。REDETERMINATION_CHECK_01.md:12は「除外条件も承認」としている一方、:35は「C1はFable採用・ユーザー個別承認の逐語なし(V04 C-10)」としており、記載が割れています。ユーザーへの質問文には、この両方の記載を事実として添えてください。暫定として現行の除外を維持することは、誤PASS側では安全です。ただし未回答のままでは受入条件#1(仕様一致)が成立しないため、**PRODUCTION_WIREDの前に回答が必須**です。
- **C-B(KP)はRで妥当です。** ただしOF-AUW-12の不一致を直してください。
- **C-C(i)(ii)のR+は妥当です。** 原文の「原則としてPromptを維持」が後から出た明示指示だからです。
- **C-H、C-J、C-KのR+は妥当です。**
- **見落としの可能性があるユーザー判断事項**:
  1. **U2: LR後v1にSecondary確認を必須とするか**(OF-AUW-06)。V04 9-4は未回答で、「同じ統一判定」と直接競合します。
  2. **U3(確認のみ)**: KP英語解説の2回が既存のユーザー決定か(OF-AUW-12)。決定がなければUにはせず、Rで3回に揃えます。
  3. **R+として記録が必要なもの**(Uではありません): JA UNCERTAIN経路の縮小(OF-AUW-08)、EN SecondaryのPASS集合(D-3は未回答。原文の「Secondary PASS」を既存の分類器の判定と解釈する)、HR_TECHの扱い。
  - U1(C1・類似度)とU2は1回にまとめて質問すれば、実装を止める必要はありません。

### 4. 実装を進めてよいか

**条件付きで可**です。条件は次の5点です。
1. OF-AUW-01とOF-AUW-02を設計に追記する。DESIGN_01の差分(DESIGN_02相当)としてFableが照合する。
2. U1(C-A5/A6)とU2(LR v1)をまとめてユーザーに提示する。暫定は現行維持とし、回答前にPRODUCTION_WIREDを報告しない。
3. 委任_02の範囲に以下を含める。
   - OF-AUW-04: import graph方式の静的監査
   - OF-AUW-09: 秒数ベースの費用計測
   - OF-AUW-11: test拡充
4. OF-AUW-03(引継ぎ経路)、OF-AUW-08(JA受理集合の明記)、OF-AUW-10(HR_TECH)を_03・_04の設計に含める。
5. OF-AUW-05のとおり、Melos regressionで不足するAzure転写を_06で補う(約¥数円)。

### 5. 確認できなかった事項

- OPEN-76/270、OPEN-288/289の原文(SSOT全文読込禁止のため未照合)。
- KP解説の2回、および10/11時点のC1承認の逐語原文(DECISION_LOGでGrepしたが該当句ヒットなし)。
- `verify_episode_audio_validation_gate`の判定条件、Master Storeのmanifestスキーマ。
- `normalize_numeric`が`25%`をどのtoken列に変換するかの実測。testは実行していません。
- legacy E(`er012_e_*`)の呼出経路の全数確認。
- 長いsegmentでPrimary NGになる率の実分布(OF-AUW-09の試算の入力値)。

主な参照ファイル:
- C:\Users\tensh\eigo-radio\er058_output\unified_all_roles_production_wiring_01\DESIGN_01.md
- C:\Users\tensh\eigo-radio\er006_secondary_asr_01.py
- C:\Users\tensh\eigo-radio\er007_ja_secondary_asr_01.py
- C:\Users\tensh\eigo-radio\er007_ja_asr_validator_01.py
- C:\Users\tensh\eigo-radio\er066_ja_asr_orthographic_equivalence_01_trial.py
- C:\Users\tensh\eigo-radio\er021_en_asr_semantic_equivalence_production_01.py
- C:\Users\tensh\eigo-radio\er006_preprod_hardening_01_validation.py
- C:\Users\tensh\eigo-radio\er019_family_x_validation_inheritance_01.py
- C:\Users\tensh\eigo-radio\er003_v1_crosslevel_audio_02_common.py
- C:\Users\tensh\eigo-radio\er011_human_review_lock_01.py
- C:\Users\tensh\eigo-radio\er077_output\m1_oov_multi_pronunciation_01\evidence_01\clip_results.json
- C:\Users\tensh\eigo-radio\er058_output\design\UNIFIED_FLOW_SPEC_V04.md
- C:\Users\tensh\eigo-radio\docs\research\ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01\REDETERMINATION_CHECK_01.md