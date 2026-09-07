# CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-02

管理ID: CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-02(追加
検証+Trial-01の2件調査)。Lane: Lane A。種別: 隔離Trial(ユーザー判断
2026-09-07: OPEN-122はVALIDATED継続・Production採用保留)。到達Status:
**VALIDATED(Trial自体は完了)、Production採用は引き続き
`USER_DECISION_REQUIRED`**。Git操作は実施していない(Fableが統合)。

新規コードは`er011_connected_speech_equivalence_layer_trial_02.py`
(Trial-01ファイルの完全コピーを起点に追加、Trial-01自体は無変更を
`git diff`で確認済み)に閉じている。Production Connected Speech
Validator・ASR routing・retry・Cost Guard・Human Review方針は一切
変更していない。

出力: `er011_output/connected_speech_equivalence_layer_trial_02/`
(audio/ 35件、results/manifest.json、audit/raw_usage_log.jsonl、
player.html)。実行ログ: `er011_output/connected_speech_equivalence_layer_trial_02_run.log`

試聴: `file:///C:/Users/tensh/eigo-radio/er011_output/connected_speech_equivalence_layer_trial_02/player.html`

---

## 0. 既知failure mode照合(先に実施)

CURRENT_SPEC.md/OPEN_ITEMS.mdの既存項目と、Trial-01の2件が重複しないか
を先に照合した。

| 既存項目 | 内容 | 今回の2件との関係 |
|---|---|---|
| OPEN-103 | "default"単語のTTS側非決定的誤発音(音訳ゆれ) | 無関係(TTS発話ではなくASR側の書き起こし挙動) |
| OPEN-106 | Key Phrase限定のfunction-word/article reduction(Production仕様化済み) | 無関係(Key Phrase専用、本文経路ではない) |
| OPEN-107 | "opened"語尾脱落(WITHDRAWN、Connected Speech Validator Pattern Bへ統合済み) | 無関係(語尾**脱落**型。今回の2件は脱落ではなく**語幹まるごと別語への置換**[asked→asks]、**2語→1語の縮約**[want to→wanna]) |
| OPEN-110 | "studies/study"・"survey/surveys"の単数複数取り違え(RESOLVED、Pattern A/C) | 無関係(規則的複数形の語尾差、今回の2件とは異なる音素形) |
| OPEN-119 | 英語Key Phrase Primary ASRの非ラテン文字誤変換(Cascade、Key Phrase限定でPRODUCTION_WIRED) | 無関係(非ラテン文字ではなくラテン文字内の文法変化) |
| ER-008/OPEN-83 | 外国由来固有名詞の発音照合(Human Review待ち) | 無関係(固有名詞ではなく一般動詞・助動詞の屈折/縮約) |

**結論**: いずれの既存項目とも重複しない。2件はいずれも既存catalogに
存在しない新しい観測(§4/§5で個別分類)。

---

## 1. 追加検証件数(カテゴリ別・陽性/陰性)

| カテゴリ | 陽性(新規Standard TTS実測) | 陰性(真の内容不一致、実測) |
|---|---|---|
| A | 4 | 1件(T2N1、A/B/D/F複合) |
| B | 4(A/B/D/F複合が主) | 1件(T2N2、A/B/D複合) |
| C | 4 | 1件(T2N3相当、A/B/C複合) |
| D | 4 | 1件(T2N4、D) |
| E | 4 | 1件(T2N5、A/B/D/E/F複合) |
| F | 4 | 1件(T2N6、G/F複合) |
| G | 4 | 1件(T2N7、A/B/D/F複合) |
| 合計 | **28件**(要求20〜30件を満たす) | **7件**(要求7件以上を満たす、各カテゴリ最低1件) |

実際の英語音韻現象として複数カテゴリに同時該当する文が多く(Trial-01と
同様の傾向)、各項目は主対象カテゴリに整理して上表へ配分した(詳細は
`category_breakdown`、manifest.json参照)。

---

## 2. 自然発生救済例(件数・原文)

**今回のTrial-02サンプル(陽性28件)では、新規の自然発生Primary
false-reject救済例は0件だった**(全て既存3パターン/Equivalence Layer
の出番なく`NO_DELETION_SHAPED_DIFF`=exact match、または層の対象外)。

ただし、意図せず2件の非自明なASR差分が発生した(いずれも狙ったA〜G
カテゴリとは無関係な副次的発見):

- **T2A3_drug_store**("drug store"→"drugstore"、3経路[Primary/
  Secondary/local]すべてが一致して複合語1語表記へ正規化): 既存
  `en_validator.classify_asr_match()`が`NORMALIZED_MATCH`として**既に
  正しく吸収済み**(新しい対応は不要という確認)。
- **T2C1_trip_plan**("rest days"→"Rustys"/"rusties"、3経路すべてが
  類似した誤変換に収束): 既存Validatorは正しく`TRUE_CONTENT_MISMATCH`、
  Equivalence Layerも正しく`NOT_A_PHONEME_PREFIX_DROP`(層の対象外)。
  3経路が独立に類似の誤りへ収束した点から、ASR側の偶然ではなくTTS発話
  自体に何らかの非典型性があった可能性が疑われる(音響検証はしていない、
  断定はしない)。新しいTTS content-accuracy候補(OPEN-103/107/110と
  同系統)の可能性はあるが、**本Trialのスコープ外**(1件のみの観測、
  Equivalence Layerは安全側で正しく不介入)。

**"showed strong"(既存Production診断データ再利用のFlagship、追加課金
なし)は今回もEQUIVALENCE_LAYER_ACCEPT(secondary/local双方が支持)を
維持し、引き続き唯一の実運用由来カテゴリA/C型救済例のまま**。

既存Production本文音声履歴(rerun-02・Trial-13・No.18関連ディレクトリ、
`er011_output`配下の全`tts_generation_results.json`)からの無料
マイニングでは、非trivial(EXACT_MATCH/NORMALIZED_MATCH以外)な英語ASR
差分レコードは3件のみ検出され、うち2件はflagship("showed strong")の
別attempt、1件は既に`HIGH_SIMILARITY_SAFE`として安全側処理済みの句読点
挿入型diff("A nearby"→"and nearby"、Connected Speechカテゴリとは無関係)
だった。**新たな無料救済例は追加で見つからなかった**(詳細:
`production_history_mining`、manifest.json)。

---

## 3. false accept / false reject

| 指標 | 結果 |
|---|---|
| false accept(陰性7件中、既存3パターンまたはEquivalence LayerがACCEPT相当と誤判定した件数) | **0/7**(要求どおり0件必須を達成) |
| 陰性の内訳 | 5件`EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE`(3経路とも実際に発話された改変後テキストで一致、corroboration無し)、**1件`EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT`**(T2N4、§7参照、Secondary ASRが誤ってcanonical側を支持したが、local ASRが正しく実発話を支持したため、MIXED判定でacceptに至らず安全側で停止) |
| false reject(陽性28件中、新規に自然発生した層の出番) | 該当なし(§2参照、今回のサンプルでは自然発生のfalse rejectそのものが0件だったため、層による救済/非救済の測定対象自体が発生しなかった) |
| Flagship実例(既存データ再利用) | 引き続きEQUIVALENCE_LAYER_ACCEPT(無回帰) |

---

## 4.「時制置換」("asked"→"asks")具体例

| 項目 | 内容 |
|---|---|
| canonical | "She asked them to wait outside."(P1_asked_them、Trial-01で実測) |
| Primary(OpenAI、prompt無し) | "She **asks** them to wait outside." |
| Secondary(Azure) | "She **asked** them to wait outside."(canonical一致) |
| faster-whisper(local) | "She **asked** them to wait outside."(canonical一致) |
| 差分 | canonical_word="asked"、asr_word="asks"(index 1) |
| 対象外理由 | ARPAbet: "asked"=`AE S K T`、"asks"=`AE S K S`。末尾音素がT(破裂音)とS(歯擦音)で**manner自体が異なる**ため、`phoneme_prefix_drop()`(末尾1〜2音素の脱落のみ)にも`phoneme_final_place_substitution()`(manner/voicing同一・placeのみ異なる)にも一致しない。物理的に連続的な音韻変化(弱化・脱落・同化)では説明できない、語幹の屈折形(過去形→3人称単数現在形)まるごとの置換 |
| 既存Validator結果 | 既存3パターン=`UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING`、`classify_asr_match()`=`TRUE_CONTENT_MISMATCH`(正しく非PASS、false acceptなし) |
| 分類 | **morphology/tense normalization**(Connected Speechの音素的部分集合ではない)。TTS自体が"asks"と発話した可能性については、Secondary・localが双方とも独立に"asked"(canonical)を支持しているため、**TTS発話自体の誤りである可能性は低い**(TTSが正しく"asked"と発話し、Primary ASR単体が言語モデル的な事前分布に基づき過去形を現在形へ正規化した、というASR側の文法正規化[grammatical normalization]が最も整合的な説明)。ただし1件のみの観測であり音響的な断定はできない |
| 命名提案(実装なし) | "ASR Verb-Inflection Normalization"(既存OPEN-103[TTS側の誤発音]・OPEN-110[TTS側の単数複数取り違え]とは、原因の所在[ASR側 vs TTS側]が異なる点で区別すべき) |

**Connected Speech Layerへ吸収せず、別failure modeとして分離提案する
(実装はしない)。**

---

## 5.「wanna正規化」("want to"→"wanna")具体例

| 項目 | 内容 |
|---|---|
| canonical | "Don't you want to come with us?"(P6_dont_you、Trial-01で実測) |
| Primary(OpenAI、prompt無し) | "Don't you **wanna** come with us?" |
| Secondary(Azure) | "Don't you **want to** come with us?"(canonical一致) |
| faster-whisper(local) | "Don't you **want to** come with us?"(canonical一致) |
| 差分 | canonical_word="want"、asr_word="wanna"(index 2、ただし実質は2語"want to"→1語"wanna"の縮約) |
| 対象外理由 | ARPAbet: "want"=`W AA N T`、"wanna"=`W AA N AH`。末尾音素がT(破裂音)とAH(母音)で、母音/子音の別自体が異なるため`phoneme_prefix_drop()`/`phoneme_final_place_substitution()`いずれにも一致しない。加えて、実際には"want"+"to"(2語)が"wanna"(1語)へ縮約されており、**既存の1語対1語word_diff()モデルの前提(語数不変)自体が成立しない**現象 |
| 既存Validator結果 | 既存3パターン=`UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING`、`classify_asr_match()`=`TRUE_CONTENT_MISMATCH`(正しく非PASS) |
| 分類 | **transcript style normalization**(Connected Speechの音韻現象[want to→wanna coalescence]自体は英語として実在し自然だが、既存diffモデルが1語対1語比較を前提とするため構造的に対象外)。TTSが物理的に"wanna"(縮約形)と発話したのか、正規形"want to"を発話しつつPrimary ASRのみが口語表記へ書き起こしたのかは、既存音声データの再利用のみでは音響的に断定できない。ただしSecondary/localが両方とも正書法表記("want to")で一致し、Primaryのみ口語表記("wanna")である非対称性は、**ASR側の書き起こしスタイルの違い**(Primary=口語表記を許容するモデル傾向、Secondary/local=正書法へ正規化する傾向)を強く示唆する |
| 命名提案(実装なし) | "ASR Transcript Style Normalization (Contraction Spelling)"。既存の1語対1語diffモデルの拡張(N-gram/多語diff対応)が必要になるため、現行Equivalence Layer実装の対象外の別課題として分離提案する |

**Connected Speech Layerへ吸収せず、別failure modeとして分離提案する
(実装はしない)。**

---

## 6. Main(Primary)/Secondary ASR比較(一致率・傾向)

Trial-02の全35件(陽性28+陰性7、実際にTTSへ渡したテキストを基準)での
一致率:

| 経路 | 実発話テキストとのexact match率 |
|---|---|
| Primary(OpenAI、prompt無し) | **33/35(94.3%)** |
| Secondary(Azure) | 29/35(82.9%) |
| local(faster-whisper) | **32/35(91.4%)** |
| Primary==Secondary完全一致 | 30/35(85.7%) |
| Primary==local完全一致 | 33/35(94.3%) |

**正直な傾向**: 今回のサンプルでは、Primary(OpenAI)は実発話テキストとの
一致率がSecondary(Azure)より高く、Secondaryの方がむしろ独自の誤り
(例: T2G3で"trust"→"through"、T2N4で実際は"turn"なのに"turned"と誤って
支持)を複数示した。これはSecondary ASRが常にPrimaryより信頼できる
"正解源"ではないことを示す重要な知見であり、corroborationゲートが
「Secondaryの言うことを鵜呑みにしない」設計(MIXED_EVIDENCE時は
acceptしない、§3のT2N4参照)になっていたことの実用的な正当性を補強
する。Flagship("showed strong")のようにPrimaryが誤りSecondary/localが
正しいケースと、今回のT2N4のようにSecondaryが誤りPrimary/localが
正しいケースの両方が実測されたことで、**単一のSecondary ASRだけに
依存せず、独立ASRを複数[Secondary+local]束ねてMIXED_EVIDENCE時は
acceptしないという既存設計が、両方向のASR誤りに対して安全に機能する**
ことを追加確認できた。

---

## 7. Connected Speech対象内外の分類(2件+新規に見つかったもの)

| ケース | 対象内/外 | 分類 |
|---|---|---|
| Trial-01 P1 "asked→asks" | **対象外** | ASR Verb-Inflection Normalization(§4) |
| Trial-01 P6 "want to→wanna" | **対象外** | ASR Transcript Style Normalization(§5) |
| Trial-02 T2A3 "drug store→drugstore" | 対象外(かつ既存Validatorが既にNORMALIZED_MATCHとして無害化済み) | 複合語スペリング正規化(新しい対応不要) |
| Trial-02 T2C1 "rest days→Rustys/rusties" | 対象外(Equivalence Layerが正しく不介入) | 3経路収束型の未知content-accuracy候補(1件のみ、断定せず、スコープ外) |
| Trial-02 T2N4 "turned→turn"(陰性、Secondary誤支持) | 対象外のまま維持(MIXED_EVIDENCE) | Secondary ASR自体の誤りに対する安全ゲートの実証 |
| Flagship "showed→show" | **対象内**(EQUIVALENCE_LAYER_ACCEPT、カテゴリA/C) | Connected Speech(語末破裂音の弱化+同一調音位置融合) |

---

## 8. 推奨次判断(Production採用可否の材料、範囲は本文経路)

1. **Equivalence Layer自体(音韻環境ルール+多証拠corroboration)は、
   今回もfalse accept 0件を維持**し、Trial-01のFlagship 1件に加え、
   Trial-02では新規の自然発生救済例こそ0件だったが、**危険な方向への
   逸脱(false accept)も一切発生しなかった**(陰性7件全PASS、T2N4の
   Secondary誤支持もMIXED_EVIDENCEゲートで正しく吸収)。
2. 一方、**自然発生の救済例は依然として"showed strong"1件のみ**
   (Trial-01・02合計、陽性37件[9+28]中1件も新規に見つからず)。
   Production採用の費用対効果(Secondary ASR常設コスト)を正当化する
   実運用頻度の証拠は、今回もFlagship 1件のまま増えていない。
3. Trial-01の2件("asked→asks"、"want to→wanna")は、**いずれも
   Connected Speech Equivalence Layerの対象外として正しく処理されて
   おり、Layerへ無理に吸収する必要はない**ことを確認した。両者は
   ASR側の異なる正規化挙動(文法正規化/表記スタイル正規化)であり、
   Production採用するとしても、本Layerとは別の課題として扱うべき
   (実装しない、命名提案のみ§4/§5)。
4. **Key Phrase経路は本Trialでは未検証のまま**(本文経路のみを対象)。
   採用候補に含めない。
5. 総合すると、**Equivalence Layer自体の安全性(false accept 0)は
   Trial-01・02の2回の独立検証で強化されたが、Production採用を正当化
   するだけの実運用頻度の証拠(自然発生救済例)はまだ乏しい**。
   Production採用は引き続きユーザー判断が必要(`USER_DECISION_REQUIRED`)。
   仮に採用する場合も、A2 Point Two相当(カテゴリA/C、corroboration
   必須)に限定し、"asked/asks"型・"want to/wanna"型は別途独立した
   課題として扱うことを推奨する。

---

## 9. Trial status

**VALIDATED**(Trial自体は完了、false accept 0件・既存回帰無回帰を
確認)。**Production採用は`USER_DECISION_REQUIRED`のまま据え置き**
(OPEN-122は引き続きVALIDATED継続、Production採用保留)。

---

## Cost

**合計 ¥22.66**(cap ¥800、大幅に未達)。

| provider | 用途 | ¥ |
|---|---|---|
| gemini | 英語TTS(Standard同期、35件) | ¥12.39 |
| openai_asr | Primary ASR(gpt-4o-mini-transcribe、35件) | ¥0.54 |
| azure | Secondary ASR(35件、audio_hour単価) | ¥9.73 |

生ログ: `er011_output/connected_speech_equivalence_layer_trial_02/audit/raw_usage_log.jsonl`
Trial-01再利用データ(2件調査・Flagship)・production history mining・
regression・synthetic sanity checkは追加課金なし。

---

## SSOT登録案

Trial-01の登録案(§12、Trial-01 Report参照)を維持しつつ、以下を追記
提案する(**本Trialでは記載しない、提案のみ**):

- Equivalence Layer自体は2回の独立検証(Trial-01・02、合計陽性37件・
  陰性12件)でfalse accept 0件を維持しており、安全性の実証は強化された。
  ただし自然発生救済例はFlagship 1件のまま増えておらず、Production
  採用の費用対効果の判断材料としては引き続き限定的。
- "asked→asks"(ASR Verb-Inflection Normalization)・"want to→wanna"
  (ASR Transcript Style Normalization)は、Connected Speech Equivalence
  Layerとは別の、ASR側の正規化挙動に関する新しい観測カテゴリとして
  記録する(実装は提案しない)。
- 既存Production Validatorが既に`NORMALIZED_MATCH`で吸収している
  "drug store→drugstore"型の複合語スペリング差は、追加対応不要の確認
  事例として記録する。

---

## 試聴Player

- 本Trial(陽性28件+陰性7件): `file:///C:/Users/tensh/eigo-radio/er011_output/connected_speech_equivalence_layer_trial_02/player.html`
- Trial-01(既存、陽性9件+陰性5件): `file:///C:/Users/tensh/eigo-radio/er011_output/connected_speech_equivalence_layer_trial_01/player.html`
- Flagship(既存Production診断、"showed strong"実音声): `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/point_two_showed_show_diag/player.html`
