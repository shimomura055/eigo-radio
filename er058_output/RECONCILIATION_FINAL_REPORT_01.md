# RECONCILIATION_FINAL_REPORT_01: ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 統合報告書 v01(委任_05B、2026-10-12)

状態: **USER_DECISION_REQUIRED**(設計案+Trial結果の統合。Production採用は人間ユーザーのみ`APPROVED_FOR_PRODUCTION`)。本書作成でProduction code/Prompt/Validator/Routing/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/REPORT_LEDGERは変更していない(SSOT記録は後続委任_06)。有料API 0円(委任_05B)。
対象読者: PM(Fable)。判断材料を先に、根拠は後ろに置く。確定=コード・ログ・保存転写で確認、推測=その旨を明記。

主な根拠ファイル: 設計 `er058_output/design/UNIFIED_FLOW_SPEC_V04.md`(v03は残す)・`MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_V04.md`・`KP_K2_VS_EXISTING_COUNTERMEASURES_V04.md`・`JA_LOCAL_REWRITE_APPLICABILITY_01.md`、Trial `er058_output/trial_abc/{TRIAL_A_EXISTING_AUDIO_01,TRIAL_B_INTENTIONAL_MISREAD_01}.md`・`trial_c/TRIAL_C_EN_ASR_COMPARISON_01.md`・`kp_english_lock_trial_01/`、委任ログ `docs/pm/delegation_log/2026-10-12_ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01_04{A,B,C,D}.md`・`_05A.md`・`_05B.md`。
**試聴ページ(判断に必要、0円)**: https://shimomura055.github.io/eigo-radio/user_test/asr_misread_listen_01/index.html (40音声、Pages 200・40/40実再生OK、`er058_output/PLAY_EVIDENCE_05B.md`)。

---

## 0. 先に読む: 結論と、いま人間が決めること(要約)
| # | 問い | 結論(1行) | 条件・注意 |
|---|---|---|---|
| 1 | 共通フローは日英・各roleで成立するか | **成立する(設計上)**。状態遷移は言語非依存。日本語のLRだけ未成立 | 導入には3つの前提(試聴連動・S1の是正・計数改修)が必要(1章) |
| 2 | Secondary PASSの原則自動採用は安全か | **条件付きで可**(Trial A/B/Cで、合意誤読の誤PASSは0件。Secondary起因の誤採用は確認済み誤読30本中1件`ja_voi5`、GT未確定) | **試聴リスト連動が前提**(ASR PASSでも確定しない型が14/44本)。2ラベル/4ラベルでこの標本の数は不変(2章) |
| 3 | 語句の種類による例外は本当に必要か | **Secondary呼出の例外はほぼ不要(C1は廃止方向)。必要なのは「ASR PASSでも自動確定しない型」の試聴連動**と数値の安全条件 | C1廃止は誤PASS 0/4(Trial B)。固有名詞はPASS_WITH_WARNING(3章) |
| 4 | KPは4回構成を3回単一Promptにできるか | **構造上は可能**。ただし**Promptの中身が新規仕様判断**で、現行2段目(English Lock)は1.4%救済実績あり(ゼロではない) | 追加Trial(数円)で決める案を推奨(4章) |
| 5 | K2は既存対策を欠くか | **欠く**(冠詞弱形が完全欠落等、△3・×4)。K2単独置換は不可 | V3/V4の優劣は**区別不能**(n=1、差0.1〜0.2秒)(5章) |
| 6 | LRは最小変更で運用でき、日本語に適用できるか | **英語は最小変更で可**(minimal依存はA2経路の1関数のみ)。**日本語は不可**(本当のNG原因に触れた0/5) | 発火条件を「合意誤読のみ」に絞る案(R3)・F-5先行修正(6章) |
| 7 | QCD | Qは偽NG由来の再生成減、Cは**Secondaryは費用だけなら割に合わない**(Cascade廃止・同一Prompt継続が主効果)、Dはcool-down廃止の効果は**平均数十秒/segment** | D6(Azure二重呼出)計上、local medium案のリスク(7章) |

**ユーザー判断が必要な項目(8章、推奨付き)**: D-1(導入範囲と順序)、D-2(試聴連動を前提にするか)、D-3(Secondary PASS集合: 英語4/日本語2の非対称)、D-4(数値S1の是正)、D-5(見出し・LR後原稿の追加保護)、D-6(KP単一Prompt)、D-7〜D-14(UNCERTAIN→HR、minimal撤去範囲、LR位置づけ、C1、固有名詞、6%減速、Secondary選択、cool-down)、D-15〜(技術失敗、Trial実施可否、費用方針、OPEN候補)。**まず40音声の試聴(0円、約20〜30分)で代理ラベルの妥当性を確認することを推奨**(2章・8章D-16)。

---

## 1. 共通フローは日英・各roleで成立するか
**結論: 成立する(設計上、確定=コード読解)。**
- 骨格(`UNIFIED_FLOW_SPEC_V04.md` 2章): TTS→Safety QA→Primary→(NGなら)安全条件→Secondary(Azure、Phrase Listなし)→両NGなら**原稿・Prompt・モデル・Voice・速度を不変のまま**再生成→3回で終了(HRまたはLR)。5 role(Full Story/Preview/Comment/In One Line/Topic Intro)+Key Phrase(英語Phrase・日本語意味)で同じ状態遷移で書ける。言語依存は(i)Primary/Secondary検証関数、(ii)S1〜S7の判定実装、(iii)LR可否のみ。
- 日本語: 既存SCG(`er007_ja_secondary_asr_01.py`、日本語Secondary確認、2ラベル)が既に目標型に近い。LRは未成立(6章)なので、**日本語は「3回不合格→直接Human Review」で開始**。
- 英語: Secondary確認(Azure)が新規(現行はTier3/CS層のみ)。Tier3/CS層とのAzure二重呼出(D6)が費用面の課題(7章)。
**導入の前提(v04で明確化)**: (1)**PASS_WITH_WARNINGの最終試聴リスト連動の実装・runtime evidence**(M3、2-6章。連動前は有効化しない、暫定は警告=NG扱い)、(2)**S1(数値)の是正**(M2、日本語の漢数字見逃し・表記差での誤発火、英語`N%`の見逃し)、(3)**計数改修**(script版あたり3回+LR後3回=最大6回。`MAX_CUMULATIVE_TTS_ATTEMPTS=15`・ASR 60の再計算、**A2経路のLR再TTSが未計数**でCoffeeは記録4/実際5=C-6)。
**承認済み仕様の変更になる項目**: UNCERTAIN→HR直行の廃止(C-1)、標準2+minimal1→標準3(C-2)、KP 4回→3回(C-4)、script版あたり3回(C-6)、LR位置づけ(C-7)、force_secondary廃止(C-8)、Cascade 4段廃止(C-9)。いずれも**人間ユーザーの`APPROVED_FOR_PRODUCTION`が必要**。

---

## 2. Secondary PASSを原則自動採用して安全か
### 2-1. Trial A/B/Cの突合(代理ラベルであり、人間試聴のground truthではない)
| Trial | 標本・費用 | 主な結果 | 出所 |
|---|---|---|---|
| A(既存音声、¥0) | 日本語Phase 0 25音声、英語Coffee part2 5 attempt、英語他NG 20本(local proxy) | 日本語: 真の誤読の代理5本は**全て再生成(誤採用0)**、正解音声は**10/15採用**(現行SCG 8/15、差はg8・g7)。Coffee: 真の誤読と確定できたNG 0件、#5(LR後最終)がPrimary PASSで採用されるが4系統中2系統が`raw bean→robbing`(**未確定**)。g8は**Primary側のASR誤認**(Azure+whisperが原稿と一致) | `TRIAL_A_EXISTING_AUDIO_01.md` |
| B(日英意図的誤読73clip、実費¥12.52) | 誤読44+対照29 | **確認済み誤読30本中、Azure(Secondary)が原稿へ丸めて誤PASSは2件、うちPrimary NG→Secondary PASSの誤採用は1件(`ja_voi5`、GT未確定)**、もう1件は同形異音`ja_hom2`(Primaryも同時にPASS)。**対照29本の統一フロー不採用は0**。数値・否定・語形・長音・最小対・濁点(ガス/カス等)は3系統とも逐語転写でValidatorがNG(誤PASS 0)。Phrase List 10本で転写は同一(改善なし) | `TRIAL_B_INTENTIONAL_MISREAD_01.md` |
| C(英語ASR比較、実費約¥35.05) | Primary NG 18+HR 6+対照8=32本(評価28本) | Primary NG系22件中**救済4件(18%、Wilson約7〜39%)**、**合意誤読11件の誤PASS 0**(Azure noPLは11件とも原稿へ補正せず)。単純OR(安全条件なし)は繰返しQA NG音声(S13)を通した。Phrase Listなしの方が厳格PASSが多い(3対0、n=5) | `TRIAL_C_EN_ASR_COMPARISON_01.md` |
| C合成(最悪ケース、¥0) | 合成誤読188件(Secondaryが原稿へ補正すると仮定) | 単純ORは144/144通す。安全条件案は**否定26/26ブロック、数値11/15ブロック(残り4件=`N%`型は警告止まり、2-2b章)**、警告24、**残存83件(内容語置換24・脱落24・固有名詞27・複数形8)は安全条件では防げない**=Secondaryが補正しないことに依存(実測では補正0/11) | 同上4章、v04訂正 |
**訂正(M2)**: v03・04C報告の「数値・否定37/37ブロック」は不正確。**正しくは否定26/26、数値11/15**(37=26+11)。

### 2-2. 2ラベル版と4ラベル版の併記(M1、¥0オフライン再判定、`two_label_rejudge_05B/`)
Secondary PASS集合: v03本文・日本語SCG=2ラベル(EXACT/NORMALIZED)、英語Trial B/C=4ラベル(+TRANSCRIPT_STYLE_NORMALIZED、NUMERIC_EQUIVALENCE)。保存済み転写を両方で再判定した結果:
| 指標 | 4ラベル版 | 2ラベル版 | 備考 |
|---|---|---|---|
| Trial C 英語救済(Primary NG 22件) | 4/22 | **4/22** | 救済4件はいずれもEXACT/NORMALIZED |
| Trial C 合意誤読11件の誤PASS | 0 | 0 | |
| Trial C 対照(Primary PASS)6件をSecondary単独判定した偽NG | 0/6 | **2/6**(S25・S30: `20%`と`20 percent`=NUMERIC_EQUIVALENCE) | 統一フローはPrimary PASSならSecondaryを呼ばないため採用結果は不変。ただしSecondary単独判定・Primary NGの救済では表記差で通らなくなる |
| Trial B 対照29件の不採用 | 0/29 | 0/29 | Azure転写に該当ラベルが出た例なし |
| Trial B 確認済み誤読30件の誤採用(Secondary起因) | 3/30(1) | 3/30(1) | 同じ |
| Trial A 日本語(25音声) | 10/15採用 | 10/15 | 元から2ラベル |
| Trial A 英語(他NG 20本) | local whisper合否のみ | 再判定不能 | ラベル未保存 |
→ **この標本では2ラベル化で救済・誤PASS数は変わらない**が、長文の英語では`20%/20 percent`のような表記差の吸収が2ラベルでは失われる。**英語4/日本語2の非対称**をどうするかはユーザー判断(D-3、推奨: 日英2ラベルに揃え、表記差は個別の正規化ルールでNORMALIZED相当に引き上げる。PHONETIC一括許容は不可)。

### 2-3. 言語差
- 日本語: Secondary(Azure)はPHONETIC_MATCHを自動PASSに含めない(厳格)。Trial BではPHONETIC許容で`ゆうき→雪`・`いった→言った`が誤PASSになる。C1(entity_like除外)は誤PASS防止実績0(3章)。日本語S1は`\d+`のみ(漢数字を見ない、2-4章)。
- 英語: 現行は(Primary NG→)Phrase List付きAzureのCascade 4段。Phrase Listは効果が見えない(Trial B/C)。表記差(`%`/`percent`、`U.S.`/`US`)でのNGがValidator側に残る(F-5)。
### 2-4. 試聴依存(重要、安全の主たる担保)
**自動採用が安全と言えるのは、「ASRが検出できる型」に限る。** 誤読44本中**14本は全ASR(Primary/Azure/local medium)が原稿形で転写**した=TTSが正しく読んだのかASRが丸めたのか区別不能(英語10: -ed/-s脱落4/4、固有名詞綴り3/3、read/red・lead/led、parked/barked。日本語4: ゴミ/コミ、スターバクス、コヒー、同音の紹介/照会)。`ja_voi5`(てんき/電気)、needs_listen 5音声、Coffee #2(`showed`)・#5(`raw bean`)、Trial C合意誤読11・曖昧7も同様に**試聴が必要**。→ **試聴リスト連動(PASS_WITH_WARNING)が前提**(2-6章)。試聴ページ: 上記URL(40音声、Blindではなく原稿・意図した誤読・ASR判定併記)。

---

## 3. 語句の種類による例外が本当に必要か
### 3-1. 結論
**「Secondaryを呼ぶ/呼ばない」の語句種別による例外は、最小限(数値・否定・length/QA・言語ドリフト・ASR障害=安全条件S1〜S6)に絞れる。C1(entity_likeの粗い除外)は廃止方向を支持する。**代わりに必要なのは「ASR PASSでも自動確定しない型」(S7とPASS_WITH_WARNING→試聴リスト連動)。
### 3-2. C1廃止の根拠(Trial)
- Trial B日本語: Primary NG+entity_like=Trueの4本は**全て真の誤読でAzureもNG(誤PASS 0/4)**。Azureは濁点差(ガス/カス、バス/パス、ビル/ヒル)を**3/3で逐語転写**し、原稿へ丸めなかった。
- Trial A g8(熟すと出るガス): Primaryは`熟す→じくす`+`ガス→カス`と誤認、Azure・whisper small/mediumは原稿どおり=**Primary側のASR誤認(ほぼ確定)**。C1が救済機会を奪った。
- C1は「カタカナ比率≧0.5」等の粗いヒューリスティックで一般カタカナ語まで巻き込み、**誤PASS防止の実績が0件**(OPEN-272)。**ただし**固有名詞のPASS扱い自体は別(OPEN-257 Muse事例: 3系統が同じ誤聴)→ S7(Secondary一致でもPASS_WITH_WARNING+試聴、辞書/Ledger/CMU確定語のみ自動PASS)。**C2(同形異音語)と推奨4(否定マーカー)はユーザー採用済みのため維持**(D-10)。
### 3-3. 「ASR PASSでも確定しない型」の整理(Trial B)
| 型 | 事例(原稿→話した形→全ASR転写) | 共通ルールで防げない理由 |
|---|---|---|
| 英語 -ed/-s 脱落(4/4本) | showed→show、asked→ask、beans→bean、costs→cost | 3系統とも原稿形で転写(LM priorの補正 or TTSが正しく読んだ)。Secondaryを足しても独立した証拠にならない |
| 英語 固有名詞綴り(3/3) | Starbucks→Starbacks、Colombia→Columbia、Ethiopia→Ethopia | 固有名詞は正しい綴りへ寄る(Phrase Listなしでも) |
| 英語 同形異音(2/2)・parked/barked | read→red、lead→led | 発音差が綴りに現れない |
| 日本語 同形異音 | 会議を行った/いった(PrimaryがPHONETICで通過)、人気(にんき/ひとけ) | ASR出力は漢字表記で読みが落ちる |
| 日本語 濁点・カタカナ(一部) | ゴミ→コミ、スターバックス→スターバクス、コーヒー→コヒー | 一般語・既知語へLM補正(未確定)。ガス/カス等は検出できたため型内の差が大 |
| 同音語 | 紹介→照会 | 音声上区別不能(誤読ですらない) |
### 3-4. 原稿側の静的特徴でマークする案(新規仕様候補・**未承認・未実装**)
ASR結果に依存せず、**原稿側の静的特徴**で「最終試聴の対象」にマークする案: 英語=辞書/Ledger外の固有名詞(大文字語)、同形異音語リスト(read/lead/live/wind等)、-ed/-s語末が最小対になりうる高頻度語、日本語=カタカナ長語・同形異音漢字(C2辞書の読み候補あり)・数詞/助数詞。長所: ASRのLM priorに依存しない(Trial Bの14本型に効く)。短所: **件数が増えると試聴負荷が過大**(件数は未測定。Trial C 28本中の該当数を数える0円の集計が次の一歩)、辞書メンテ、推定ヒューリスティックの粗さ(OPEN-272と同型の課題)。**採否は未判断**(D-11と一体、最小対Trial後に確定する案)。
### 3-5. 表記差の正規化(2-2b章、M2)
日本語S1は`\d+`のみ(L67)で、**表記差(二人↔2人、三十人↔30人、十分↔10分、100円↔百円)では発火して正しい音声でもSecondary不呼出→3回NG→HR**、逆に**漢数字の値変更(三人→四人、三十人→四十人)を見逃す**。`20％↔20パーセント`はSecondaryもPASS集合外でNG。英語は`N%`の値変更4/15を見逃す。**方針案**: S1を「値の不一致」で判定し、数値・単位・記号を同一値へ正規化してからNORMALIZED相当へ引き上げる。**PHONETIC_MATCH一括許容は不可**(`ゆうき→雪`・`いった→言った`が誤PASS)。

---

## 4. KPは4回構成を3回単一Promptに変更できるか
### 4-1. 結論
**構造としては変更できる**(`generate_key_phrase_component_verified`の2段呼出を1段(max_attempts=3)へ畳むだけ。KP専用Minimal Promptは撤去対象と独立)。ただし(i)**単一Promptの中身が新規仕様判断**、(ii)現行4回=ユーザー正式決定(2026-09-01)の変更、(iii)**2段目(English Lock)の救済実績はゼロではない**。
### 4-2. 選択肢(`UNIFIED_FLOW_SPEC_V04.md` 3-2)
| 案 | P | 長所 | 短所・未検証 |
|---|---|---|---|
| P-a | 現行Minimal(初回段のPrompt) | 変更最小、Master Store再利用維持(キー無変更) | English Lock(翻訳的書起こし対策のTTS側予防)が無くなる。**旧2段目が救った約1.4%がMinimal 3回目で通るか未検証** |
| P-b | 現行English Lock常用(Minimal+Lock) | 既存承認文言の逐語使用のみ | 初回から常用の効果は未測定。Master Store version更新(既存241件再利用不可) |
| P-c | K2統合(簡潔V3/完全V4) | 一体感(K2)+対策②③を含められる | 新規Prompt=Trial・ユーザー採否必須。K2単独は不可(5章)。Master Store version更新 |
### 4-3. 2段目(English Lock)による救済実績(¥0集計、`zero_yen_checks_05B.json`)
- attempt_history(2026-09-01以降、`kp[1-5]_en`、重複除外294 call): **1回目合格272(92.5%)、2回目12(4.1%)、English Lock段(3〜4回目)で合格4(1.4%)**、English Lock段に入って不合格(HR)3、ロック済みHR 3。
- 保存attempt音声で確認できた事例3件(2026-09-17 b1_2v kp5、09-25 meta kp4、09-28 hormuz run_06 kp5=**Flash-Lite、Production現行**)はいずれも**Minimal 2回NG→English Lock段でNORMALIZED合格**。
- 解釈: **ゼロではない**。ただしEnglish Lockの効果と「単に3回目の再試行が確率的に通った」は**区別できない**。P-aの根拠(ゼロなら現行Minimal維持が自然)は**成立しない**=追加Trialが妥当。
### 4-4. Master Storeへの影響(確定、¥0確認)
- KP英語340件・固定殻35件・日本語3件。全378件が`instruction_path=primary`で**minimal/English Lock由来を示す印はキーに無い**。Promptを変える案(P-b/P-c)は`KEY_PHRASE_TRIM_POLICY_VERSION`更新が必要=**既存241件(`v2_margin030`)が再利用不可で再生成コスト**。P-aは影響なし。minimal由来が標準キーに混入していないかは**manifestだけでは判定不能**(混入経路はKPの2段目[救済率約1.4%]とB1/Charon固定殻の技術的fallback[頻度不明])。
### 4-5. 追加Trial最小設計(**未実施**、承認が前提)
V1(現行Minimal)・V3(簡潔統合)を**8〜10語×各3回**生成(Flash-Lite、Aoede、Standard同期)。評価: 自動(Primary PASS率・非ラテン・反復)+**Blind試聴**(版名を隠し順序ランダム、ユーザーが1語ずつ自然さ・語尾・冠詞を採点)。**費用目安: 数円(約3〜5円)**、所要約30分。English Lock救済実績(1.4%)の再現性は少数事象で、このTrialでは測れない点に注意(測れるのは初回合格率と聴感)。

---

## 5. K2の既存対策欠落
- 逐語比較(`KP_K2_VS_EXISTING_COUNTERMEASURES_V04.md` 2章): K2(332文字)は現行(1076文字)の「naturally and clearly」「warm announcer」「explanations列挙禁止」「not trailed off」「過剰強調禁止」「English Lock」を**欠落/弱体化(△3・×4)**、**冠詞・機能語の弱形(対策②、a catch問題の対策)が完全欠落**。一体感・音程の小さな連続はK2が強い。
- ①ASR対策(逐語ASR指示・非ラテン時の再確認)と③生成後QA(部分反復検知)はPrompt非依存で**維持**。②TTS Prompt対策はK2単独では満たさない→**K2単独置換は不可(統合が必要)**。
- Trial D(8語×4版、各1回、32 call、実費約¥1.6): **32件全てPrimary PASS・非ラテン0・反復0**(自動評価の識別力は低い)。長さ: V1 1.29s / V2(K2) 1.39s / V3 1.49s / V4 1.28s。**v04訂正(M5c)**: 「V4でK2の効果が薄れた」は撤回し、**V3とV4の差は区別不能(n=1、差0.1〜0.2秒)**。聴感評価・複数回再現は未実施(試聴ページ `user_test/kp_english_lock_trial_01/index.html`)。

---

## 6. LRは最小変更で運用できるか・日本語適用可否
### 6-1. 英語
- **最小変更で運用可能**(現行実装)。ただし位置づけ変更に伴う改修: (1)**minimal依存のLR再TTSはA2経路(`crosslevel` L383)の1関数のみ**(確認済み、¥0): B1/Charon(`voice01` L359)とNews(`news_tail_fix` L368)の再TTSは標準Promptの1 attempt(`__wrapped__(max_attempts=1)`)でminimal不使用。(2)**A2経路だけLR再TTS分を`attempts_log`へ追記しない**=Coffee記録4/実際5(C-6、必須是正)。(3)NG span選択をNGを出したASR転写基準へ(OPEN-274)。(4)LR後の再生成上限は現状1回→共通フロー案は3回。
- LR自体の品質Gate(全文性・局所性・span整合・数値保持・Luna 5 Gate QA)は維持。報告項目(発火理由・書換え箇所・前後文面・最小限の根拠・v1の再生成結果)をHR報告へ必須化。
### 6-2. 発火条件を「合意誤読のみ」に絞る案(R3、新規仕様候補・未承認)
Trial C/Aで、v0 3回全NG(Primary NGかつSecondary NG)でも**正しい音声のASR誤認・表記差**が多い(Coffeeの5NGで真の誤読確定は0件、日本語LR実例5件中3件はTTSが正しい)。LRが発火すると**正しい原稿を書き換える**(g21・g36)。案: **LRを発火させるのは「独立3系統のうち2系統以上が同じ差分でNG=合意誤読」の場合のみ**とし、ASR間で割れた・表記差のみ・Validator起因(F-5)はHR(または再生成)。合意誤読は実測で**Secondaryに補正されず(0/11)**、LRの対象として妥当。採否はD-9。
### 6-3. F-5の先行修正
F-5(US↔U.S.+cost↔costs同時でUNCERTAIN、Validatorの偽NG。根は固有名詞ヒューリスティックの粗さ=OPEN-272)が残る限り、偽NGがLR発火の入口になる。**LR位置づけを変える前にF-5相当のValidator偽NGを先に直す**ことを推奨(新規仕様候補・未承認)。
### 6-4. 日本語
**機械流用不可**(`JA_LOCAL_REWRITE_APPLICABILITY_01.md`): `identify_ng_span`は純日本語で`found=False`、Gate 7(`compute_unchanged_ratio`)は15候補全てで0.0=常に不合格、全文性判定は不安定。5実例でgpt-6-lunaは最小書換え候補を作れたが**本当のNG原因に触れたのは0/5、3/5はTTSが正しい**(ASR誤認・表記差)。→ **日本語LRはREJECTED寄り(現状案では)**。当面LRなし(3回不合格→HR)。Secondary側の表記差・PHONETIC扱いの設計が先(3-5章)。

---

## 7. QCD(是正済み項目を含む)
### 7-1. 是正済み(委任_05A、merge `d7ae4b9b`、SSOT反映済み)
- OPEN-270(6%減速の外側ループが上限3回を破る)CLOSED: 通算3回共有・cool-downを**通算3回目直前のみ**発火。runtime evidence(04A): TTS生成 旧6回→新3回(cap)。
- OPEN-271/275(Azure費用が集計外)CLOSED: Azure STT費用を計上(日本語SCG含む)。Coffee Phase 2累計は約¥31.03/50に補正。
- 残: LR再TTS未計数(A2、上記6-1)、OPEN-282〜285候補(R3〜R5、未承認)。
### 7-2. 品質Q / コストC / 時間D(見込み、標本が小さい項目は推測)
| 項目 | 変化 | 根拠・注意 |
|---|---|---|
| Q | 偽NGによる不要な再生成・本文書換え(LR)が減る(英語)。誤PASSは厳格集合+安全条件S1〜S7で抑える | 合意誤読の誤PASS 0/11。**内容語・固有名詞の最悪ケースは安全条件で防げず(残存83)**、Secondaryが補正しない前提に依存 |
| C | **Secondaryは費用だけでは割に合わない**(Azure約1.8円/40秒音声は1回のTTS再生成約0.135円の約13倍)。**主効果はCascade 4段廃止・force_secondary廃止・同一Prompt継続**。英語Azure追加は+約0.2〜0.3円/call(Trial C射影)。**D6(v04加算)**: Tier3/CS層が同じ音声に別にAzureを呼ぶため、Secondaryを足すと二重呼出=Primary NG音声(割合は標本により異なる。旧フローで標準2回内に完了しなかったcallは約7%)で**+約2円/件**(Secondary転写を共有する改修で0に) | 完了率95.3〜97.4%(現行93.1%)だが**主因は旧フローが打切った所を3回目まで継続した外挿**で、Secondary救済実測は5.6% |
| D | **cool-down(600秒)の廃止は「最大約10分/segment短縮」ではなく、平均で約30〜48秒/segment**(600秒待ちは通算3回目に到達した5〜8%のsegmentのみ)。**cool-down導入理由(一時的なAPI不調・レート制限の回避)を外した場合の悪影響は対照データが無く不明** | v03の「最大約10分」は最大値で平均ではない(M5a) |
### 7-3. local medium案のリスクと「言語ごとにSecondaryを変える」案(D-13)
- S-A: 日英Azure(Phrase Listなし)。S-B: **英語=ローカルwhisper medium(0円)、日本語=Azure(現行SCG維持)**。S-C: 英語Azure+medium併用。
- mediumのリスク: 局所脱落(`People`脱落等)、**Primary PASS音声の32.5%をNGにする**(FREE_VERIFICATION 4-8、偽NG源)、本番側のローカル実行環境が未確認、日英で挙動が二重化、**日英の独立性が等しいか未検証**。Trial CではPrimary NGの救済用途のみ測定(NG系22件でmedium 5件≒Azure 4件)。**Primary PASS検査用途は別問題で未測定**。

---

## 8. 残るユーザー判断事項(統合・重複排除)
注: Opus総合レビュー本文は本委任に渡されていない。04D「残る判断事項」8項目と必須修正M1〜M5から派生する判断を「Opus由来」として整理し、前回U-0〜U-19の未決と重複排除した(解消済みはD-18に明記)。各項目: 選択肢/推奨/理由。**いずれもProduction採用は別途`APPROVED_FOR_PRODUCTION`が必要**。
| ID | 判断事項(出所) | 選択肢 | 推奨 | 理由 |
|---|---|---|---|---|
| D-1 | 共通フローの承認範囲・導入順(U-0、04D#1) | (a)日英同時 (b)日本語先行 (c)英語先行 (d)Full Storyのみ先行 (e)見送り | **(d)Full Story(英語)先行、前提D-2〜D-4充足後**。日本語はLRなしで追随 | 影響最大のsegmentで実測、段階導入でロールバック容易 |
| D-2 | PASS_WITH_WARNINGの試聴リスト連動を導入の前提とするか(M3) | (a)連動実装・evidenceが先 (b)連動前は警告=NG扱いで暫定有効化 (c)連動なしで有効化 | **(a)。間に合わなければ(b)** | 連動なしだと自動確定しない型(14/44本)が誤PASSのまま公開される |
| D-3 | Secondary PASS集合の非対称(M1、U-3、04D#4) | (a)英語4/日本語2のまま (b)日英2+表記差の個別正規化 (c)日英4(日本語に同等実装) | **(b)**。PHONETIC一括許容は不可 | この標本で救済・誤PASS数は不変、`20%/20 percent`は正規化で吸収。PHONETIC許容は誤PASS(`ゆうき→雪`) |
| D-4 | S1(数値)の是正(M2、U-12) | (a)「値の不一致」で判定+正規化(漢数字/数詞語/`N%`/助数詞) (b)現状(`\d+`のみ) (c)数値を含む音声は全てHR | **(a)** | 日本語は漢数字の値変更を見逃し、表記差で正しい音声を3回NG→HR。英語は`N%`変更4/15を見逃す |
| D-5 | 見出し・LR後原稿の追加保護(M4) | (A)Primary PASSでもSecondary確認(見出し・LR後のみ) (B)最低限PASS_WITH_WARNINGで試聴リスト入り (C)対策なし | **(B)+見出し・LR後のみ(A)** | 見出しは元からforce_secondary無し(L126-128、v04確認)、標準1+minimal2の内訳。LR後は`raw bean→robbing`型(Coffee #5)。対象が少なく費用影響小 |
| D-6 | KP単一Prompt(04D#2、U-9) | P-a / P-b / P-c(4章) | **追加Trial(数円)実施→結果で決定**。暫定P-a | 2段目救済1.4%(ゼロでない)、K2は欠落あり、V3/V4は区別不能 |
| D-7 | UNCERTAIN→HR直行の廃止・例外案C(U-2、C-1) | (a)現行維持 (b)Secondary→再生成 (c)両ASRが同じ誤りで一致なら即HR (d)表記差・濁点・entityのみHR | **(c)**(最小対Trial後確定) | HR 8件が同一転写で再実行の効果薄 |
| D-8 | minimal撤去の範囲(U-4、04D#6) | (a)A2英語・日本語の内容NG再試行から撤去(同一Prompt 3回)、見出しの標準1+minimal2も同時整理 (b)現行維持 (c)技術失敗専用の隔離経路を残す | **(a)、(c)は不採用寄り** | 日本語leakageはFlash-Lite+speech_metadataで**0/87**(旧方式のみ発生)、400エラーは**確率的で同一Prompt再試行56%成功**=隔離不要寄り |
| D-9 | LRの位置づけ・発火条件・日本語(U-5、04D#5、R3) | (a)v0 3回全NGで自動発火 (b)**合意誤読のみ自動発火**(R3)、他はHR (c)HR後の人間手動オプションへ隔離 (d)日本語LR追加 | **(c)または(b)。日本語は当面LRなし**。F-5先行修正 | 日本語LRは本当のNG原因に触れた0/5。偽NGでの発火が正しい原稿を書換える |
| D-10 | C1廃止・C2維持(U-1、04D#7) | (a)C1廃止、固有名詞はS7+辞書/Ledger (b)C1維持 (c)最小対Trialで測ってから | **(a)に傾くが(c)を挟む**。C2・推奨4は維持 | C1誤PASS防止実績0(Trial B 0/4)、g8はASR誤認。推定自体の廃止はOPEN-272 |
| D-11 | 固有名詞のSecondary一致・最小対の扱い・原稿側マーク案(U-17、U-18、3-4章) | (a)再生成/HR、辞書・Ledgerのみ自動PASS (b)PASS_WITH_WARNING+試聴 (c)現行 / 原稿側静的特徴のマーク案の採否 | **(b)**、マーク案は件数集計(0円)後に判断 | 全ASRが同じ誤りを返す型(Muse等) |
| D-12 | 6%減速後の検証(U-7) | (a)案B (b)案C (c)**案B'**(最終音声のみ検証) | **(c)** | OPEN-76の承認仕様に忠実。外側ループの根はOPEN-270で上限共有済み |
| D-13 | Secondary選択・費用(U-8、7-3章) | S-A / S-B / S-C | **判断前にlocal medium追加検証(0円)**。暫定S-A(PLなし) | Secondaryは費用だけで割に合わない。medium偽NG(32.5%)は未測定用途 |
| D-14 | cool-down(U-6) | (a)廃止 (b)再生成前のみ (c)現行(通算3回目直前のみ、05A後) | **(c)現行維持** | 廃止効果は平均数十秒。導入理由を外した影響は不明 |
| D-15 | 技術失敗・ASR障害(U-10、2-5章) | (a)attempt外・上限付き(同一slot最大2回)、無音・異常長は消費 (b)全て消費 (c)全て外 | **(a)**、400は同一Prompt再試行 | 400は確率的(再試行成功56%) |
| D-16 | Trial実施可否(U-14、04D#8) | 試聴(0円)/ KP最小Trial(数円)/ 最小対Trial(8-3-A、約15〜20円)/ local medium追加(0円) | **試聴→KP最小Trial→最小対Trial** | 代理ラベルの妥当性確認が先 |
| D-17 | C-6計数改修(LR再TTS未計数、累積ガード再計算) | 導入の必須条件にする/しない | **必須条件に** | 上限6回で累積15・ASR 60の意味が変わる。Coffee記録4/実際5 |
| D-18 | 解消済み・別扱い | U-15(Azure費用計上)・U-19(OPEN-270/271是正)は**05AでCLOSED**。残: OPEN-285(単価未登録の扱い統一)、OPEN-282/283/284(候補) | 個別に採用/保留 | 本件の設計判断とは独立 |
| D-19 | 保留事項(U-13、U-16) | 新規仕様候補(否定活用ギャップ、辞書補強、異音同綴)は保留。wavはgit管理しない運用 | **保留 / (a)+(b)** | 根拠が合成のみ |

---

## 9. 対象ごとのStatus案(提案。最終判断はFable・ユーザー)
Status値: VALIDATED(Trial範囲で妥当、Production未承認)/ REJECTED / USER_DECISION_REQUIRED。**いずれもProduction採用は未承認**。
| 対象 | Status案 | 根拠 |
|---|---|---|
| 日英共通フロー(状態遷移・S1〜S7・PASS集合) | **USER_DECISION_REQUIRED**(Trial: 骨格はVALIDATED寄り) | 誤PASS 0/11だが、前提D-2〜D-4・D-17が未充足 |
| KP 4→3回単一Prompt | **USER_DECISION_REQUIRED**(追加Trial推奨) | Promptの中身が新規。2段目救済1.4% |
| minimal撤去(A2英語・日本語の内容NG再試行) | **VALIDATED(設計・影響範囲)/ Production: USER_DECISION_REQUIRED** | 日本語leakage 0/87、400確率的、A2のLR再TTSだけが依存 |
| minimal撤去(技術的fallback・見出しの標準1+minimal2) | **USER_DECISION_REQUIRED** | 見出しの内訳整理、B1/Charon技術的fallback |
| LR拡張(日本語) | **REJECTED(現状案)** | 本当のNG原因0/5、Gate 7常に不合格 |
| LR位置づけ変更(英語、発火=合意誤読のみ等) | **USER_DECISION_REQUIRED** | D-9 |
| C1廃止 | **VALIDATED(Trial限定、誤PASS 0/4)/ Production: USER_DECISION_REQUIRED** | D-10 |
| PHONETIC一括許容 | **REJECTED(Trial B)** | `ゆうき→雪`等が誤PASS |
| K2単独置換 | **REJECTED** | 冠詞弱形欠落 |
| K2+既存対策の統合(V3/V4) | **USER_DECISION_REQUIRED** | 聴感未評価、区別不能 |

---

## 10. Closeout用一覧
- **承認済み未配線(approved-but-unwired)**: `docs/pm/PM_BRIEF.md`直近記載は「なし」。日本語SCG(OPEN-258)はPRODUCTION_WIRED。**本タスクで新規の未配線は作っていない**(設計案・Trialのみ)。
- **未解決USER_DECISION_REQUIRED**: 8章 D-1〜D-17、D-19(D-18は解消済み/別扱い)。
- **未報告Trial**: なし(A=04B、B=04B、C=04C、D=04D、JA LR=04D、2ラベル再判定・0円確認・試聴ページ=05Bで報告)。**未実施(提案のみ)**: KP追加Trial(4-5)、最小対Trial(8-3-A)、local medium追加検証(0円)、**人間試聴(試聴ページ、結果待ち)**。
- **新規仕様候補(未承認・未実装、報告のみ)**: 3-4章(原稿側静的特徴マーク)、6-2(LR発火=合意誤読のみ)、6-3(F-5先行修正)、2-2b(S1正規化)、見出し標準Prompt化、Flash-Liteで`speech_metadata.style`がprompt_tokens非計上(Prompt長が費用に影響しない可能性、請求画面未確認)。
- **関連OPEN(既存、SSOT未編集)**: OPEN-257(固有名詞Muse)、272(固有名詞ヒューリスティック)、273(技術失敗)、274(LR再TTS・span)、276/277(一部)/279/281、282〜285(05A新規候補)。OPEN-270/271/275はCLOSED。
- **Dangling Reference Check**: 本委任でminimal fallback等の撤去は**行っていない**ため撤去後の実測検査は対象外。`er053_dangling_reference_check_01.py`は**旧Fact Checker撤去用の検査script(走査対象・シンボルが別)で、minimal撤去には適用できない**(実装時は新規対応が必要)。撤去した場合の想定結果(grepベース、要対応=`_run_a2_minimal_fallback_attempt`・`PRODUCTION_STANDARD/MINIMAL_FALLBACK_TTS_ATTEMPTS`+assert・静的監査/回帰テスト、残す=`FAMILY_X_ROLE_STYLE_EN_FALLBACK`等)は`MINIMAL_FALLBACK_REMOVAL_DEPENDENCY_V04.md` 9〜11章。本委任の新規成果物の参照先(下記ファイル群)は実在を確認。
- **Opus独立技術レビューGate**: 本書の設計案(v04)はM1〜M5反映で内容が変わったため、**Production採用提案前(条件C)・新構造の設計(条件A)の再レビュー要否はFable判断**(条件・観点の正本は`docs/pm/PM_GOVERNANCE.md` 11-3節)。

---

## 11. 費用総括と使用モデル
| 項目 | 実費(JPY) | 備考 |
|---|---|---|
| Trial A | 0 | 既存転写のみ |
| Trial B | **12.52** | TTS 3.99 / Azure 7.44 / OpenAI ASR 1.10(`cost_actual_B_01.json`) |
| Trial C | **約35.05** | Azure STT 788.6秒(`cost_actual_C_01.json`、上限40内) |
| Trial D(KP Prompt) | 約1.6 | TTS 1.1(usage実測)+Primary ASR概算0.5 |
| JA LR適用性 | 0.71 | gpt-6-luna 5 call |
| 是正(04A) | 約0.6 | Azure 1回のruntime evidence |
| 05A | 0 | |
| **05B(本委任)** | **0** | 保存ログ・保存転写の再判定、静的ページのみ |
| **合計** | **約50.5円** | 請求画面は未確認。Azure契約tier(F0/S0)の実請求はユーザー確認 |
使用モデル(最新原則報告): TTS=`gemini-3.8-flash-lite-tts`(**最新世代・Production同一**)、Primary ASR=OpenAI `gpt-4o-mini-transcribe`(Production同一、**最新性は未確認**)、Secondary=Azure Speech STT(en-US/ja-JP)、参考=local faster-whisper small/medium。**ASR群はProduction比較のための測定対象=最新原則の例外(種別2)**。JA LR候補生成=`gpt-6-luna`(**最新ではない**: 最上位`gpt-6-astra`・推奨`gpt-6.1-sol`、理由=Production LRの実モデルの適用可否確認、astra/solは単価未登録・上限制約)。評価者LLMは不使用。05Bは新規モデル呼出0。
