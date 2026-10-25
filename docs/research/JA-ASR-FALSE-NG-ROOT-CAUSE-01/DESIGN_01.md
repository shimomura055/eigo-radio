# DESIGN_01(Phase 2 対策立案。設計のみ・API 0・Production変更0)

方針: 品質基準は下げない。**「ASRが書いた文字」ではなく「音(かな)と値」で比べる**ことで、①文字の選び方だけが違う正常音声のNGを減らし、②音が違う(わ脱落、値違い、否定、別語)ものは従来どおりNGにする。既存機構(`_numeric_value_equivalence`型のadapter層)を拡張し、新しい判定系統は作らない。

## 推奨: 案A(必須・低リスク・API 0) + 案B-light(条件付き・Phase 3のAzure実測後に採否)

### 案A「日本語 発音・値一致層」(既存の欠陥3つの是正+適用漏れ1つ)
| 部品 | 内容 | 変更箇所(既存機構のどこ) |
|---|---|---|
| A1 桁区切り | 両文のNFKC後、`\d{1,3}(,\d{3})+`の`,`のみ除去(3桁区切りに限定。`1,2,3個`等の列挙は不変) | 新helper。adapter層のvalue_form前処理に入れる(`normalize_ja`本体は変えない=EXACT/NORMALIZED経路を不変に保つ) |
| A2 助詞の発音 | 形態素解析(fugashi/unidic-lite、既に依存済み)で**助詞は→ワ、へ→エ**のみ発音形(`pron`)を使い、他は従来の`kana`。`月の詩は`=`月のしわ`の発音になる | 新helper(`er011_ja_asr_variant_layer_01.morph_kana_reading`は直接編集しない=Candidate B/C/D-1の既存test・挙動を不変にする) |
| A3 値atom化+残り発音比較 | 既存`_ja_value_form`(`er007_ja_secondary_asr_01.py:494`)で両文の数値atomを値トークン化し、**値ガードがEQUAL/NO_VALUES**かつ否定差なし、かつ残りが(a)`normalize_ja`後に完全一致、または(b)A2の発音一致(厳格: 濁点許容なし、漢字候補総当たりなし、LLMなし)のとき一致 | adapter層`_numeric_value_equivalence`(`:511`)の「残り完全一致」条件を「残り発音一致」へ**拡張**(同関数の延長。新関数は`_pron_value_equivalence`として同位置に並置) |
| A4 Secondary受理への適用 | `_secondary_accept`(`:643`)で、`SCG_PASS_CLASSIFICATIONS`不一致のとき上記A3層を試す。(a)値等価のみ=仕様L2865が既に認める範囲(不具合是正)、(b)発音一致が必要な場合は`PASS_WITH_WARNING`(新warning `JA_PRON_EQUIVALENT`)で事後試聴リスト対象 | `er007_ja_secondary_asr_01.py:643-660` |
- ラベル: 数値を含む=既存`NUMERIC_VALUE_EQUIVALENT_MATCH`、含まない発音一致=`PHONETIC_MATCH`(Primary)。いずれも`equivalence_basis`は`APPROVED_EQUIVALENCE_BASES`に**入れない**(最終ANDゲートの値/否定再確認を維持)。
- 手順上の位置: Primary NG(TCM)かつ上記が成立 → Primary PASS(最終AND)。Primary NG→Azure→Azure転写に同層 → PASS_WITH_WARNING。それ以外は従来どおり。
- 規模: 新規約100-130行+test 40件程度。Production編集は`er007_ja_secondary_asr_01.py`の2関数(+1行のflag読取)と新module 1つ。

#### 案Aの誤PASSリスク分析(どんな真の誤発音をすり抜けうるか)
| 区分 | すり抜けるか | 根拠 |
|---|---|---|
| 音素の欠落・追加・置換(`しわ`→`し`、`ちょう`→`こえ`、`間`→`目`、`へ`→`に`) | しない | 発音列が不一致(`adversarial_panel_01.out.txt`で`月の死`、`学校に`、`三日目`=NG) |
| 値違い(8,900→8,800/8000900) | しない | 値ガードDIFFは従来どおり先に落とす |
| 否定差(来ない→来る) | しない | 否定差ガード維持 |
| 十分/10分 | しない | AMBIGUOUSは別機構(Secondary同一表層のみ) |
| **同音異義語の取り違え**(橋/箸、市場いちば/しじょう等) | **する(既存PHONETIC_MATCHと同じ)** | ASR文字は発音だけの証拠。今回の追加ではなく既存仕様(OPEN-258 A4/C2同形異音除外は維持=本案はA4除外を外さない) |
| **値は同じだが読みが違う音声**(三日をさんにち、一日いちにち/ついたち) | 一部する | 既存`_numeric_value_equivalence`と同じ残余リスク(er066 REPORT_02 §8-(4))。A4で不規則読み署名(日1〜10/14/20/24、人1・2、歳20、月4/7/9)を持つ文は`PASS_WITH_WARNING`にして事後試聴対象にする案を推奨 |
| 助詞「は」を実音声が`は(ha)`と発音(TTS不具合) | 検出不能 | どのテキストASRでも不可(ASR文字が同じ)。今回の追加ではなく既存の盲点 |
| 形態素解析の誤分割で別語が同読み | 低い | A3は全文で比較し、厳格(語1つでも違えばNG)。Phase 3でadversarial≥100で測定 |
数値保護仕様(値ガード・v4/J2はWriter段)との整合: 値ガードの判定を**緩めない**(EQUAL/NO_VALUESのみ通過)。中核数値v4/J2は別工程で影響なし。同音救済(er109は英語専用)とは独立。

### 案B-light「JAの値DIFFをAzure確認へ回す」(P1の範囲見直し)
- 内容: JAのP1(Primary値DIFF→即`NG_PROTECTED`、Azure不呼出)を、「**値DIFFがPrimaryだけ**」なら**Azure 1回**を呼び、Azure転写が**案Aの層で原稿と値一致・発音一致**のときだけ`PASS_WITH_WARNING`(数値警告付き=事後試聴の最優先対象)。Azureが値DIFF/不一致ならNG(従来どおり)。Primary単独の値DIFFを通すのではなく、**独立した2つ目のエンジンが原稿の値を支持**したときのみ。否定差のP1は不変。
- 変更箇所: `er078_asr_unified_judge_01.py:566-568`(P1)のJA限定緩和。`vote`(KP英語3-ASR)方式の前例あり(同:566の`vote is None`条件)。
- 月題への効果: attempt1/3(Azure未呼出)が救えるかは**Azure実測が必要**(未測定・Phase 3で約¥0.6)。
- 誤PASSリスク: 真に違う数字(例: 音声が8,800)をPrimaryが`8800`と正しく転写→Azureも`8800`→NG。**Primaryが8800と書き、Azureだけが8,900と誤転写**した場合のみ誤PASS(エンジンは原稿を見ないため原稿方向へ偏る理由はない。確率は低いが非ゼロ。Phase 3で数値違い音声の負例12件以上で測定)。ローカルWhisper第3票は有効だが、UDR #136の「ローカルWhisperのProduction導入は不採用」(KP英語のみ上書き)に触れるため**本設計では既定に含めない**(判断候補)。
- 費用: JAのP1発火は全1,217 attempt中2件(0.16%)。期待増分=Azure約¥0.27×(発火率≈0.002)≒¥0.0005/attempt。全体では**削減が大きい**(1 TTS再生成+ASR+HR工数回避)。
- 位置づけ: **P1は承認済み安全条件**(`CURRENT_SPEC.md` L2852「重大内容差を警告だけで解放しない」)。B-lightは警告のみ解放ではなく「独立エンジンの支持」を要求するが、承認済みP1の意味変更を含む→**ユーザー判断要(D)**。案Aの効果とPhase 3のAzure実測を見てから提示する(不要なら出さない)。

## 検討して推奨しない案(却下理由)
| 案 | 内容 | 却下理由 |
|---|---|---|
| C 位取り断片の復号 | `8000900`を8000+900=8900と復号して値一致とみなす | 月題では1/2(`8000句800`は復号不能)。復号器という新しい数値解釈系統を増やす(「新システム乱立」回避)。B-lightで両方扱える |
| D JAのPrimary/Secondary入替(Azure primary) | 24件のAzure救済は全てAzureが原稿と同一表層、OpenAI miniはハングル/台風機等の誤転写が多い | 実測母集団は“OpenAIがNGでAzureを呼んだ”サンプルに偏る(選択バイアス)。UDR #136で入替は不採用の確認済み。**提案のみ**、判断は別(Phase 3でAzure単独の誤NG/誤PASS率を同一セットで測れば比較可能) |
| E ASRへ原稿をprompt | JAでpromptを与えて数詞整形を安定化 | ASRが原稿に引っ張られ、**誤発音を原稿どおりに書いてしまう**(検出力低下=誤PASS増)。品質側に悪いため不可 |
| F TTS入力の数字をかな化 | `8,900本`を`はっせんきゅうひゃくほん`で送る | 音声が変わる(品質/声の自然さ)。Writer/TTS段の仕様変更でASR誤認識の根本対策にならない(Azure/Whisperは数字を正しく読めている) |
| G 閉じた助数詞リストに`本`を追加 | 既存D-1の拡張 | 三日坊主型の回帰が実証済み(OPEN-319 追記(3)「閉リスト拡張方式では実装しない」) |
| H 条件緩和(NGをそのままPASS) | 類似度/読み候補総当たり(E)を広げる | 禁止(品質を下げるだけ) |

## X/Z共通化・配線・Rollback
- 判定経路がX/Z共通のため**共通実装**。Family固有例外なし。A/B/Cへの波及は、配線時に`er109_xz_scope_01`型(run-scope X/Z + 単一flag読取関数、既定OFF)にするか全JA共通にするかをFableが決める(開発対象X/Zのみ、27-7)。
- Phase 3はDEV専用module(`er117_ja_pron_equiv_trial_01.py`想定、Production非import、AST test)で実施。**到達上限VALIDATED、配線はユーザー正式採用後**。
- 旧検査の整理: 案A採用後、`_numeric_value_equivalence`の「残り完全一致」は新層の(a)として吸収(撤去でなく包含)。重複する個別救済(Variant Layer BのA2相当)は残置(挙動は広がるだけ、撤去不要)。配線時にGrepで撤去/残置を確定。

## QCD
- Q: 誤PASS増加は上表の区分に限定(既存と同種のみ)。Phase 3の合格基準で0件を要求。
- D: 月題はA単独でHR回避(attempt2で通過)、B-lightありで1 attempt完了。JA HR率は全期間2.2%(25/1,151)で、うち本件型は一部(7/150転写)=ゼロにはならない。
- C: API追加0(A)。B-lightは発火時Azure約¥0.27のみ。量産単価70円目標への影響は±0.01円未満。
