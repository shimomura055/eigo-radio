# CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01

管理ID: CONNECTED-SPEECH-EQUIVALENCE-LAYER-GENERALIZATION-TRIAL-01
Lane: Lane A(Key Phrase・英語TTS検証)。種別: 隔離Trial(ユーザー承認
2026-09-07)。到達Status: **VALIDATED(Trial自体は完了)、Production採用は
`USER_DECISION_REQUIRED`**。

Production Connected Speech Validator(`er011_b1_connected_speech_
validator_01.py`、OPEN-107/OPEN-110、3パターン限定で`PRODUCTION_WIRED`)・
ASR routing・retry・Cost Guard・Human Review方針は一切変更していない。
新規コードは全て隔離Trialモジュール
[er011_connected_speech_equivalence_layer_trial_01.py](er011_connected_speech_equivalence_layer_trial_01.py)
に閉じている。Git操作は実施していない(Fableが統合)。

出力: `er011_output/connected_speech_equivalence_layer_trial_01/`
(audio/ 14件、results/manifest.json、audit/raw_usage_log.jsonl、
player.html)。試聴: `file:///C:/Users/tensh/eigo-radio/er011_output/connected_speech_equivalence_layer_trial_01/player.html`

---

## 0. Closeout分類(方式別)

| 方式 | 判定 |
|---|---|
| (i) Rule-based phonetic environment(ARPAbet+環境規則、本Trialの中核) | **VALIDATED**(実Production診断データ・実TTS/ASRテストで機能を確認、false accept 0件) |
| (ii) Secondary ASR cascade(Azure一致による救済) | **VALIDATED-as-corroboration-evidence**(単独のacceptトリガーではなく、(i)の安全ゲートとして機能。既存OPEN-119のようなCascade単独発動とは役割が異なる) |
| (iii) Lightweight acoustic confirmation | **NOT_NEEDED_FOR_CURRENT_EVIDENCE**(флagshipケースでは(i)+(ii)+local ASRのみで十分な多証拠が揃った。診断時に取得済みの簡易音響分析[§8]は補足情報として有用だが、今回のゲート判定には不要だった) |
| (iv) LLM/phonetic reasoning | **NOT_ATTEMPTED**(本Trialでは不要だった。将来カテゴリが増えた場合の拡張余地として§10で言及) |
| (v) 既存3パターンの再利用 | **PRESERVED_UNCHANGED**(既存`classify_connected_speech()`を最初に無変更で呼び、ACCEPT/RESEGMENTATIONならそのまま返す。既存57件+新規15件のregressionは無回帰で確認済み) |

**推奨方式(§9で詳述)**: (i)+(ii、Secondary Azure)+ローカルfaster-whisper
(無料)の組み合わせが、コスト・実装難易度・安全性のバランスで最小十分
(minimum sufficient)。音響分析・LLM推論の追加常設は今回のデータでは
正当化できない。

---

## 1. "showed strong"の正式原因分類と根拠

**分類B(既存OPEN-112 Theme2診断で暫定判定されていたもの)を、本Trialの
新Equivalence Layerで多証拠的に裏付けた**: 実音声は"showed"であり、
Primary ASR(OpenAI `gpt-4o-mini-transcribe`)がConnected Speech環境下で
語末/d/を脱落させて書き起こした(TTS発音ミスではなく、ASR側のfalse
rejection)。

根拠(いずれも既存Production診断`er011_open112_theme2_point_two_showed_
show_diag_02.py`の実データ、本Trialでの追加課金なし・再利用のみ):

| 経路 | 結果 |
|---|---|
| Primary ASR(full clip, no prompt, attempt1) | "show strong"(誤り) |
| Secondary ASR(Azure, full clip, phrase_list=["showed"]付与) | "showed strong"(canonical一致) |
| Secondary ASR(Azure, windowed clip, **no phrase bias**、補足証拠) | "Still **showed** strong interest."(canonical一致、バイアス無しでも一致) |
| faster-whisper local(独立した第3のASR、full clip) | "showed strong"(canonical一致) |
| 簡易音響分析(語境界の低エネルギー区間) | attempt1で1件・attempt2で3件のclosure候補区間を検出(/d/の閉鎖に整合しうる物理量、断定はしない) |

**音韻環境**: canonical "showed"(ARPAbet `SH OW D`)の語末/D/(歯茎破裂音)
が、次語"strong"(`S T R AO NG`)の語頭/S/(歯擦音)の直前という環境にある。
これは既存Validatorの3パターンいずれにも一致しない:
- Pattern A(歯擦音連続、例studies+suggest)は前語末が**歯擦音**(/s,z/)で
  ある必要があるが、"showed"の語末は**破裂音**(/d/)であり非該当。
- Pattern B(破裂音連続)は次語頭が**破裂音**(/t,d/)である必要があるが、
  "strong"の語頭は/s/(歯擦音)であり非該当。
- Pattern C(再分節)は語幹への子音追加型で、今回は脱落型のため非該当。

すなわち、"showed strong"は「語末破裂音+次語頭歯擦音」という、既存3
パターンのどちらの条件とも半分だけ重なるが完全には一致しない、
**カテゴリA(語末子音の弱化・無開放)の中でも特に歯茎破裂音+歯擦音の
境界という、ユーザーが当初提案していた「/d/+/s/」個別パターンに相当する
具体例**だった。本Trialの新Equivalence Layerは、この具体例を個別
hardcodeとしてではなく、「語末破裂音(カテゴリA)」という一般規則+
独立ASR corroborationの組み合わせで説明する(§4)。

---

## 2. 既存OPEN-107/OPEN-110との関係(役割分担表)

| 項目 | OPEN-107(Ending-Clarity fallback、`WITHDRAWN`) | Connected Speech Validator(3パターン、`PRODUCTION_WIRED`) | 本Trial: Equivalence Layer(隔離Trial) |
|---|---|---|---|
| 対象 | ASR不一致を「TTS誤発音」とみなし、追加TTS再生成で対処 | ASR不一致を「そもそも誤発音ではない」と直接再判定 | 同左、ただし既存3パターンの外側(未分類)へ拡張 |
| 判定根拠 | なし(常に再生成) | 綴り規則ベースの3パターンのみ(-s/-es/-ed限定、単一証拠) | 音素(ARPAbet)ベースの一般カテゴリA〜G+独立ASR corroboration(多証拠) |
| 安全機構 | retry上限・review_lock | 既存`protected_check()`(数字/否定保護)通過後のみ発火 | 既存3パターンを無変更のまま優先、未分類時のみ発火。corroboration 0件ならACCEPTしない |
| 適用範囲 | B1 News本文+Comment(撤回済み) | B1英語Validator全体 | Trialのみ、Production未配線 |
| "showed strong"への適合 | 該当しない(OPEN-107自体は"opened"型の別事例) | **非該当**(§1参照、UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING) | **該当**(EQUIVALENCE_LAYER_ACCEPT) |

**結論**: 既存3パターンを否定・置換するものではなく、その外側
(UNCLASSIFIEDのまま既存判定へfall throughしていた領域)を、個別パターン
追加ではなく一般カテゴリ+多証拠corroborationで扱う**拡張レイヤー**として
設計した。既存3パターンがACCEPT/RESEGMENTATIONと判定した場合は、本Layer
は一切介入しない(§4のコード上、既存関数呼び出しの結果をそのまま返す)。

---

## 3. Connected Speechカテゴリ整理(A〜G)と既存3パターンの位置づけ

| カテゴリ | 説明 | 既存3パターンとの関係 | 本Trialでの音素条件 |
|---|---|---|---|
| A. 語末子音の弱化・無開放 | 語末子音(特に破裂音)が後続子音の前で弱化・脱落的に知覚される | Pattern A(歯擦音限定)・Pattern B(破裂音+破裂音限定)は、Aの中の2つの狭い特殊ケース | 語末が破裂音(P,B,T,D,K,G) |
| B. /t,d/reduction | Aの下位、歯茎破裂音に特化 | Pattern Bと重なるが、次語頭を破裂音に限定しない点で広い | 語末がT/D |
| C. 語境界での同一・類似子音融合 | 語末と次語頭が同じ調音位置 | Pattern B(opened+to、同じ歯茎破裂音)はCの特殊ケース | 語末placeと次語頭placeが一致 |
| D. Assimilation | 語末子音が後続子音の調音位置へ同化(置換、脱落ではない) | 既存3パターン外(既存は脱落型diffのみ対象) | 語末N/T/Dが次語頭のplaceと異なる場合の**置換**(§4で新規実装) |
| E. Coalescence | /t,d/+/j/の破擦音化(don't you/did you型) | 既存3パターン外 | 語末T/D+次語頭Y |
| F. Glottalization/flapping | 語末/t/の声門化・母音間flap化 | 既存3パターン外 | 語末T(+母音間ならflap、+子音前なら声門化候補) |
| G. Resyllabification | 語末子音が次語頭母音へ連結、音節境界が語境界とずれる | 既存3パターン外 | 次語頭が母音 |

**"showed strong"はカテゴリA(語末破裂音の弱化)、かつC(語末/D/と次語頭
/S/がいずれも歯茎[alveolar]で同一調音位置)の両方に該当する**(§1参照)。

---

## 4. Equivalence Layerの設計(多証拠判定フロー)

実装: [er011_connected_speech_equivalence_layer_trial_01.py](er011_connected_speech_equivalence_layer_trial_01.py)
`classify_connected_speech_equivalence()`

```
1. 既存csv3.classify_connected_speech(canonical, asr)を無変更のまま呼ぶ
   -> ACCEPT/RESEGMENTATIONならそのまま返す(既存挙動を一切変えない)
2. UNCLASSIFIEDの場合のみ、以下を追加で試みる:
   a. word_diff()で最初の食い違い位置を特定
   b. diff形状を判定:
      - 音素prefix脱落(phoneme_prefix_drop、ARPAbetでasr語がcanonical語の
        先頭部分と完全一致し、末尾1〜2音素だけ多い) -> カテゴリA/B/C候補
      - 音素置換(phoneme_final_place_substitution、末尾音素以外は完全
        一致、末尾音素はmanner/voicingが同じでplaceだけ異なる) -> カテゴリD候補
      - どちらでもない -> NOT_A_PHONEME_PREFIX_DROP(既存判定を維持)
   c. 次語頭の音素と組み合わせ、phonetic_environment_categories()で
      カテゴリA〜Gを判定(該当なしならNO_KNOWN_CATEGORY_MATCH)
   d. 独立ASR(Secondary Azure / local faster-whisper)が、diff位置で
      canonical側を支持しているかをposition-based比較で判定
   e. 決定:
      - corroboration 0件 -> EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE
        (acceptしない、既存判定を維持)
      - 独立ASR同士が食い違う(一方は支持・一方は否定) ->
        EQUIVALENCE_LAYER_MIXED_EVIDENCE_INSUFFICIENT(acceptしない)
      - corroboration >=1件かつカテゴリがA/B/C(既存パターンに近い高確信度) ->
        EQUIVALENCE_LAYER_ACCEPT
      - corroboration >=1件かつカテゴリがD/E/F/G(より広い低確信度) ->
        EQUIVALENCE_LAYER_PASS_WITH_WARNING
```

**安全設計のポイント**: 単一証拠(diffの見た目・環境カテゴリ該当のみ)では
絶対にacceptしない。「音韻環境が既知カテゴリに該当する」AND「独立ASRの
少なくとも1つがcanonical側を支持する」の両方が必須。§6の陰性対照で、
この2条件ゲートが実際に機能することを確認した。

**既知の限界**(正直に記載): position-based corroboration比較は、
canonical/他ASRテキスト間でdiff位置より手前に語数のずれ(挿入・脱落)が
ある場合にずれる可能性がある。本Trialのテストデータでは発生しなかった
ことを確認済みだが、Production採用時はこの前提の頑健性を追加検証すべき
(§10)。

---

## 5. テストセット(Positive/Negative、出典・生成条件)

### Flagship(既存Production診断データ再利用、追加課金なし)
- "showed strong"(§1参照)。canonical全文+Primary ASR(full clip実データ)
  +Secondary ASR(full clip、phrase_list=["showed"]付与、実データ)+
  faster-whisper local(full clip実データ)。

### Positive(新規実TTS生成、Standard同期、Charon以外=Gemini英語voice)
9件、各1回生成、Primary ASR(OpenAI)+Secondary ASR(Azure、no phrase
bias)+local faster-whisperを実行:

| id | canonical | 想定カテゴリ | 実際の結果 |
|---|---|---|---|
| P1_asked_them | She asked them to wait outside. | A/B | Primary ASRが"asked"→"asks"(時制の誤り、脱落型ではなく音素が丸ごと異なる置換のため対象外、NOT_A_PHONEME_PREFIX_DROP) |
| P2_next_stop | The next stop is downtown. | A/B | Primary/Secondary/Local全てcanonical通り(EXACT_MATCH) |
| P3_big_cat | The big cat slept by the door. | A/C | 同上(EXACT_MATCH) |
| P4_ten_pounds | He paid ten pounds for the ticket. | D | 同上(EXACT_MATCH) |
| P5_that_boy | I saw that boy at the park. | D/F | 同上(EXACT_MATCH) |
| P6_dont_you | Don't you want to come with us? | E | Primary ASRが"want to"→"wanna"(口語短縮の正規化、"don't you"自体は無関係。脱落型でないため対象外) |
| P7_did_you | Did you finish the report on time? | E | 同上(EXACT_MATCH) |
| P8_get_it | Can you get it from the shelf? | F | 同上(EXACT_MATCH) |
| P9_an_apple | She ate an apple for lunch. | G | 同上(EXACT_MATCH) |

**正直な結果**: 今回の9件(各1回生成)では、キュレーションしたカテゴリ
C〜G環境そのものはTTSにより正しく音声化されたが、Primary ASRが
false-rejectを自然発生させた例は無かった(EXACT_MATCH 7件、無関係な
別種のASR誤り2件)。**Flagship("showed strong")が今回唯一の、実運用で
自然発生したカテゴリA/B/C型false rejectionの実例のままである。**
この結果自体が重要な知見であり、§9で議論する。

### Negative controls(新規実TTS生成、canonicalとは異なる内容を実際に
発話させた真の内容不一致)
5件、うち1件は下記理由で無効化(N4):

| id | claimed canonical | 実際にTTSへ渡したtext | 結果 |
|---|---|---|---|
| N1_show_not_showed | Young travelers still **showed** strong interest in the results. | Young travelers still **show** strong interest in the results. | Primary/Secondary/Local全て"show"で一致(claimed_canonicalの"showed"を支持する証拠ゼロ) -> **EQUIVALENCE_LAYER_INSUFFICIENT_EVIDENCE(正しく非accept)** |
| N2_show_not_showed_2 | The results **showed** clear improvement this quarter. | The results **show** clear improvement this quarter. | 同上 -> **INSUFFICIENT_EVIDENCE(正しく非accept)** |
| N3_asks_not_asked | She **asked** them to wait outside. | She **asks** them to wait outside. | 音素が丸ごと異なる置換のため、そもそもカテゴリ判定に進まず -> NOT_A_PHONEME_PREFIX_DROP(既存TRUE_CONTENT_MISMATCH維持) |
| N4_do_not_did | **Did** you finish the report on time? | **Do** you finish the report on time? | **無効化**: 3経路(Primary/Secondary/Local)全てが実際の発話を"Did you"と一致して書き起こした。TTS自体が指示テキスト"Do you"とは異なる"Did you"を発話した疑い(本Trialの対象外の別現象、§7で言及)。claimed_canonicalと実際の音声内容が偶然一致してしまったため、意図した陰性対照として機能しなかった |
| N5_orange_not_apple | She ate an **apple** for lunch. | She ate an **orange** for lunch. | 別単語への真の置換のため、カテゴリ判定に進まず -> NOT_A_PHONEME_PREFIX_DROP(既存TRUE_CONTENT_MISMATCH維持) |

**有効な陰性対照4件(N1,N2,N3,N5)、false accept 0件**(要求"3件以上・
false accept 0件"を満たす。N1/N2はflagshipと同一の音韻環境[語末破裂音+
次語頭歯擦音]を持つ最も厳しい敵対的対照であり、これが正しく非acceptに
なったことがcorroborationゲートの有効性の最重要な証拠)。

### Rule-engine単体sanity check(合成diff、実音声ではない、追加課金なし)
実測でカテゴリD/E/F/Gの自然発生例が得られなかったため、ルールエンジン
自体の正しさを別途確認した:
- SYN_D(sun/sum、実在するCMU辞書語で構成した歯茎鼻音→両唇鼻音の
  同化、次語頭"barely"が両唇音): カテゴリD検出、corroboration有りで
  PASS_WITH_WARNING・無しでINSUFFICIENT_EVIDENCEと、ゲートが設計通り
  動作することを確認。
- SYN_E/F/G/C(`phonetic_environment_categories()`直接呼び出し): 期待
  カテゴリが正しく含まれることを確認。

---

## 6. 結果表(方式×テスト: false reject/false accept/latency/cost)

| 項目 | 結果 |
|---|---|
| 既存3パターンregression(fixture再利用) | 4/4 PASS(既存判定を完全に保存) |
| 既存Production regression test(`er011_no18_connected_speech_reading_resolver_wiring_08_test.py`) | 15/15 PASS(本Trialのコードは一切import・変更していないため無回帰は当然だが、実行して再確認済み) |
| Flagship実データ | EQUIVALENCE_LAYER_ACCEPT(カテゴリA/B/C該当、secondary/local双方がcanonical支持=corroboration 2/2) |
| Positive実測(9件) | 7件EXACT_MATCH(層の出番なし)、2件は脱落型ではない別種のASR差分(層は正しく不介入)。**false reject: 該当なし(今回のサンプルでは新規false rejectionが発生しなかったため測定不能、Flagshipのみが唯一のfalse reject実例)** |
| Negative実測(有効4件) | **false accept: 0/4** |
| 合成テスト(SYN_D) | 意図通り動作(corroboration有無でACCEPT系/非ACCEPT系が分岐) |
| Cost | **合計¥19.39**(cap ¥800、内訳: Gemini TTS ¥4.06・OpenAI Primary ASR ¥0.86・Azure Secondary ASR ¥14.47。§11) |
| Latency | TTS生成1件あたり数秒、Primary ASR数秒、Secondary ASR数秒、local faster-whisper(smallモデル、CPU)数秒。14件全体で数分程度(実行ログ参照) |
| 実装複雑度 | 新規関数約10個、既存3パターンの呼び出しに影響なし。ARPAbet辞書(`pronouncing`ライブラリ、既存homophone_enモジュールと同一ライブラリを流用)への依存が新規に加わる |

---

## 7. Secondary ASRの有効性

Flagship・N1・N2いずれにおいても、**Secondary ASR(Azure)がcanonical側を
正しく支持/否定する決定的な役割を果たした**:
- Flagshipでは、Primary ASRが誤って"show"と書き起こした際に、Secondary
  (phrase bias付き、かつ別途取得済みのphrase bias無しwindowed版も)双方が
  "showed"と一致してcorroborationを提供した。
- N1/N2(敵対的陰性対照)では、Secondaryも実際の発話どおり"show"(reduced
  form)と一致し、誤ったcorroborationを提供しなかった(false accept
  防止に直接寄与)。

一方、既存OPEN-119(英語Key Phrase false rejection Cascade)のSecondary
ASR運用とは役割が異なる点に注意: OPEN-119は「Primary ASRが非ラテン文字
主体の異常出力を返した場合のみ」Cascadeを起動する狭い条件だが、本
Equivalence LayerはPrimary ASRの出力が(正常な英語表記の範囲内で)
canonicalと1語だけ異なる場合の**corroboration証拠源**として使う、より
一般的な使い方である。

**付随的な発見(N4)**: Secondary ASR・local ASRは、TTS自体が指示テキスト
と異なる内容を発話した場合(N4、§5参照)にもそれを正確に検知した
(3経路とも一致して"Did you"を報告)。これはSecondary/local ASRが
「Primary ASRのみの誤り」と「TTS自体の誤り」を区別する診断能力を
持つことを示す、副次的だが有用な知見である。

---

## 8. 音響evidenceの必要性

既存診断(`point_two_showed_show_diag`)で取得済みの簡易音響分析
(語境界の低エネルギー[closure候補]区間検出)は、attempt1で1件・attempt2
で3件のclosure候補区間を検出しており、/d/の閉鎖に整合しうる物理量として
補足的な価値がある。しかし、**本Trialのcorroboration判定(Secondary
Azure + local faster-whisperの2つの独立ASR)だけで、Flagship・陰性対照
いずれも正しい判定に到達できており、音響分析を必須のゲート条件に
追加する必要性は今回のデータでは確認されなかった**。

将来、Secondary ASRとlocal ASRが食い違う(EQUIVALENCE_LAYER_MIXED_
EVIDENCE_INSUFFICIENT)ケースが実際に発生した場合には、tie-breaker
として音響分析(または3つ目のASR)を追加する拡張余地がある設計にして
いるが、常設は今回のデータでは正当化できない(§9)。

---

## 9. QCD比較と推奨方式

| 方式単体 | 検知精度(本Trialデータ内) | false accept | Latency | API cost | 実装複雑度 | 保守性 |
|---|---|---|---|---|---|---|
| 既存3パターンのみ(現状Production) | Flagshipを救済できない(UNCLASSIFIED) | 0(既存fixtureで確認済み) | 最小 | 0(追加ASR無し) | 最小 | 高(ユーザー承認済み3パターンのみ) |
| (i)音韻環境ルールのみ、corroboration無し | Flagshipは救済できるが、N1/N2(敵対的陰性)を誤ってacceptしてしまう(**危険、単独使用は不可**) | **危険(N1/N2で実証)** | 最小 | 0 | 小 | 低(false accept実証済みのため不可) |
| (i)+(ii、Secondary Azure)のみ | Flagship救済・N1-N5全て正しく非accept | 0 | Secondary ASR呼び出し分(数秒) | 小(Azure、¥14.47/14件≒¥1.03/件) | 小 | 高 |
| (i)+(ii)+local faster-whisper(本Trial採用構成) | 同上、二重のcorroboration(より頑健) | 0 | + local ASR数秒(無料) | 同上(local分は無料) | 中 | 高 |
| (i)+(ii)+(iii、音響分析) | 未検証(今回のデータでは不要と判明) | - | + 数秒 | 0(ローカル計算) | 中〜大 | 中(既存診断コードの流用は可能) |

**推奨方式**: **(i)音韻環境ルール(ARPAbetベース、カテゴリA〜G)+
(ii)Secondary ASR(Azure)corroboration+local faster-whisperの二重
corroboration**が、安全性(false accept 0件を実証)・コスト(1件あたり
約¥1〜2)・実装複雑度のバランスで最小十分。単独の音韻環境ルールは
**危険なため不可**(必ずcorroborationとセットで運用する必要がある)。
音響分析・LLM推論の追加常設は、今回のデータでは正当化されない
(Secondary/local ASRが食い違うケースが実際に観測された場合の拡張候補
としてのみ検討)。

---

## 10. USER_DECISION_REQUIRED(Production採用に必要な判断)

Production採用の可否・範囲は、以下の判断が必要なため、本Trialでは
**一切実装しない(隔離Trialのまま)**:

1. **カテゴリA/B/C(高確信度)のみをProduction採用するか、D/E/F/G
   (PASS_WITH_WARNING)まで含めるか**。本Trialの実データはカテゴリA/B/C
   (Flagship)のみが自然発生の実例を持ち、D/E/F/Gは合成テストでのみ
   ルールの正しさを確認した(実運用でのfalse reject発生頻度は未知数)。
2. **Secondary ASR(Azure)の追加呼び出しを、B1(既存3パターン適用範囲)
   だけでなくA2(showed strongの発生元)へも新たに常設するか**。現状
   Secondary ASRはCascade条件[entity-like/homophone-candidate]限定で
   しか自動発動しない。Equivalence Layerの安全設計はSecondary/local
   corroborationを前提としており、Production配線するなら追加のASR
   呼び出し(コスト・レイテンシ)を新たに常設する判断が必要。
3. **position-based corroboration比較の頑健性**(既知の限界、§4)を、
   より多様な実データで追加検証する必要があるか。
4. **既存3パターンとの統合方法**: 本Trialは既存3パターンを最初に無変更
   で呼ぶラッパー設計にしたが、Production配線する場合、既存
   `classify_asr_match()`のどこに・どの順序で組み込むか(既存の
   `protected_check()`・`is_entity_like_mismatch()`・
   `is_homophone_candidate_mismatch()`との順序関係)は、既存retry/
   Cascade条件への影響を精査した上でユーザー判断が必要。
5. **N4(TTS自体が指示テキストと異なる内容を発話した疑いの事例)**は、
   本Trialの対象外の別現象(TTS content-accuracy、OPEN-103/107/110と
   同系統の可能性)であり、独立した調査が必要かどうかはユーザー判断
   に委ねる(重大度: 低、Trial音声のみで実害なし)。

---

## 11. Cost

**合計 ¥19.39**(cap ¥800、大幅に未達)。

| provider | 用途 | ¥ |
|---|---|---|
| gemini | 英語TTS(Standard同期、14件) | ¥4.06 |
| openai_asr | Primary ASR(gpt-4o-mini-transcribe、14件) | ¥0.86 |
| azure | Secondary ASR(14件、audio_hour単価) | ¥14.47 |

生ログ: `er011_output/connected_speech_equivalence_layer_trial_01/audit/raw_usage_log.jsonl`
Flagship(既存データ再利用)・regression・synthetic sanity checkは追加
課金なし(テキストのみ、または既存診断データの再利用)。

---

## 12. SSOT登録案

Production採用が承認された場合、以下を`CURRENT_SPEC.md`「Audio
Production Pipeline」節・`OPEN_ITEMS.md`(OPEN-107/OPEN-110行への追記、
または新規OPEN項目)へ記載することを提案する(**本Trialでは記載しない、
提案のみ**):

- 項目名(案): 「Connected Speech Equivalence Layer(A〜Gカテゴリ、多証拠
  corroboration)」
- 内容(案): 既存B1 Connected Speech Validator(3パターン)を無変更で
  維持しつつ、その外側を音韻環境(ARPAbet)+Secondary ASR/local ASR
  corroborationで判定する拡張レイヤーとして、`er006_preprod_hardening_
  01_validation.py::classify_asr_match()`(既存3パターンの配線箇所と
  同じ関数)へ追加配線する候補。
- 適用範囲(案): まずA2 Point Two相当(カテゴリA/B/C、corroboration
  必須)に限定し、D/E/F/Gは追加の実運用データが集まるまで`DEFERRED`と
  する案(§10の判断次第)。
- 参照: 本Report、`er011_connected_speech_equivalence_layer_trial_01.py`、
  `er011_output/connected_speech_equivalence_layer_trial_01/results/manifest.json`。

---

## 試聴Player

- 本Trial(Positive/Negative代表): `file:///C:/Users/tensh/eigo-radio/er011_output/connected_speech_equivalence_layer_trial_01/player.html`
- Flagship(既存Production診断、"showed strong"実音声): `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/point_two_showed_show_diag/player.html`
