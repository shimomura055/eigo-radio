# JA-ASR-FALSE-NG-ROOT-CAUSE-01 ROOT_CAUSE_01(Phase 1 原因究明、2026-10-25、API 0・Production変更0)

結論(先に): 月Std題の3 attemptは**3つとも別々の理由**でNGになった。共通点は「正常な音声を、ASRの“文字の選び方”の違いでNGにしている」ことだが、原因は日本語判定の**4つの独立した欠陥**に分解できる(下記R1〜R4。事実=実コード・実記録で再現済み。原因解釈の一部は「仮説」と明記)。
実音声の再ASRは行っていない(API 0)。代わりに**ローカルWhisper(faster-whisper、API費用0)で3音声を独立に転写**した(`whisper_local_3wav_01.json`)。

## 0. 対象と記録(事実)
- 原稿(canonical)=`月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密`、TTS入力も同一(`reading_safety_changed_text=false`)。`er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/audit/tts_generation_results.json`(segments.japanese_title.canonical_text)。
- Primary=OpenAI `gpt-4o-mini-transcribe`(`er006_asr_provider_routing_01.py:31`、JAもprompt無し=`er003_v1_repro01_main_generate.py:354`は`prompt=asr_prompt if language=="en" else None`)。Secondary=Azure Speech STT ja-JP。
- 判定は`er007_ja_secondary_asr_01.evaluate_attempt_ja_with_cascade_detail`(adapter)→`er078_asr_unified_judge_01.unified_judge`。X/Zとも同じ経路(`er063_family_z_audio_01.py:964,979`が`repro01.generate_narration_snippet_verified_strict`を呼ぶ=X/Z共通)。

## 1. 3 attemptの判定経路 逐次トレース(再現済み: `trace_moon_classify_01.py`/`.out.txt`)
| # | wav sha(先頭) | Primary転写(OpenAI) | Azure | 判定経路(どの検査がどの値でNG) |
|---|---|---|---|---|
| 1 | 5ccb3c48 | 月野詩は**8000句800**本超え。… | 未呼出 | ①`classify_ja_asr_match`: `normalize_ja`後 `protected_check_ja`のopcode差で数字不一致 `number_mismatches=[('9','0008')]`(文字単位diffがcanonical`8,900`とASR`8000句800`を中途半端なspanで切るため。再現値)→TRUE_CONTENT_MISMATCH(`er007_ja_asr_validator_01.py:256-259,382`)。②adapter: `_numeric_value_equivalence`は値ガードがEQUALでないため非適用(`er007_ja_secondary_asr_01.py:521-523`)。③統一judge: 値ガード`DIFF`(`'8,900本'→'8000'`value_differs、`'800本'`脱落)→**P1 `p1_value_diff`で`NG_PROTECTED`、Azure不呼出**(`er078_asr_unified_judge_01.py:566-568`)。 |
| 2 | f0c4b415 | 月の**死は八千九百**本超。… | 月の**詩は8900**本超。… | ①classify: 数字差`('8900','')`(`八千九百`は閉じた助数詞リスト外=`本`でないため漢数字→算用数字化されない)→TCM。②adapter `_numeric_value_equivalence`: 値ガードEQUAL(`8,900本`=`八千九百本`)だが**残り文字が完全一致でない**(`しわ`≠`死は`)→None(`er007_ja_secondary_asr_01.py:529`)。③judge: Primary値EQUAL・否定なし・P2除外なし→P3でAzure 1回(¥0.267)。Azure転写は値EQUAL。④Secondary許容判定`_secondary_accept`=`classify_ja_asr_match`のみで`EXACT/NORMALIZED`以外は不受理(`er007_ja_secondary_asr_01.py:643-650`、`SCG_PASS_CLASSIFICATIONS`=`:83`)。Azure転写は`しわ`↔`詩は`のopcode差+`,`(canonicalの桁区切り)脱落がcontent_diffs→**TCM→`NG_BOTH secondary_not_accepted`**。 |
| 3 | d0dd41e4 | 月の**氏は8000900**本超。… | 未呼出 | ①classify: 数字差`('','000')`→TCM。②値ガードDIFF。③**`p1_value_diff`で`NG_PROTECTED`、Azure不呼出**。(最終slot=minimal fallback。3回目NG→HR Lock、`review_lock_state.json`) |
Whisper(local)独立転写(medium): #1 `月の詩は8,900本超え`/#2 `月の死は8,900本超`/#3 `月のしは8,900本帳`(smallは`8900`は読めるが`本語へ/本長/ポンチョ`と別の崩れ)。**数値`8,900`は3音声とも独立に正しく読めている**。→ 音声側の数値は正しい(ユーザー試聴「問題なし」と整合)。

## 2. 原因(R1〜R4)と確信度
### R1(「しわ」→詩/死/氏): 助詞「は」の読みの扱い欠落 — 確信度 高(コード・再現)
- 3つの転写はいずれも「**し＋は**」(名詞+助詞)。助詞「は」の発音は`わ`なので、**音としては「しわ」と完全に同じ**(OpenAI 3/3、Azure 1/1、Whisper medium 3/3が同じ「し|は」分割=音声が「しわ」と聞こえている証拠。TTSが音を欠落させたのではない)。
- 日本語の読み照合は2系統あるがどちらも助詞を「は=ha」で読む:
  - `_reading_equal`(pykakasi): `月の詩は`→`tsukinoshiha`、`月のしわ`→`...shiwa`(再現: `trace_moon_classify_01.out.txt`)。
  - 追加層Candidate B(fugashi+unidic-lite): `morph_kana_reading`が`word.feature.kana`(綴り由来の`ハ`)を先に使い、**発音形`pron`(`ワ`)を使わない**(`er011_ja_asr_variant_layer_01.py:96-100`)。unidicは助詞「は」を`kana=ハ, pron=ワ`で持つ(再現: `rc2`相当、`月の詩は`→(は,ハ,ワ,助詞))。
- 日本語には「既存の表記違い・同音救済」が**ある**(PHONETIC_MATCH、Variant Layer B/C/D-1/E、Reading Resolver)が、(a)助詞/へ・はの読み、(b)数値atomを含む文の“読み”比較、(c)桁区切り、を扱えない。英語の同音救済`er109`(音素列CMUで比較)は**英語専用**(`DESIGN_PROPOSAL_01.md:93` 日本語=対象外、`er078_asr_unified_judge_01.py:373,394,415`の`lang != "en"`)で、JAには適用される設計ではなかった。
- 「しわ」と「し」は区別される: 読み比較で`月のしわ`vs`月の死`(わ脱落)は`pron_differs`でNG(`adversarial_panel_01.out.txt`)。=音素欠落は誤救済されない。

### R2(「8,900本」→8000/800本/8000900本): OpenAI(mini)の日本語数詞→算用数字化が不安定 — 確信度 中(転写の事実は確定、機序は仮説)
- 事実: 同じ種類の音声(「はっせんきゅうひゃくほん」)に対し、OpenAIは attempt1=`8000句800本`、attempt2=`八千九百本`(漢数字のまま)、attempt3=`8000900本`と**3回とも別の崩れ方**。Azureは`8900本`、Whisper mediumは`8,900本`で安定。→ 数値は音声が正しく、OpenAI miniの数詞整形(ITN)が不安定。
- 仮説: ①`8000900`は「8000」+「900」を位取り断片のまま連結した出力(8000+900=8900と復号可能)、②`8000句800`は「九(きゅう)」を「句」と誤認して崩れた出力(復号不能)。JAのPrimaryにprompt/後処理は無く(上記)、`gpt-4o-mini-transcribe`のJA数詞出力は保証されていない。
- 照合側の不具合(R3,R4)とは独立。値ガード`8000900`は正しく`DIFF`(`er078_asr_value_guard_01`)で、**値ガード自体は妥当**(実際に違う数字列は通せない)。問題は「DIFF=即NG_PROTECTED、Azureを呼ばない」というP1設計(`er078_asr_unified_judge_01.py:566-568`)で、**ASR側の整形崩れと真の読み違いを区別せずに、別エンジンで確かめる前に打ち切る**点。JAのP1発火は全1,217 attempt中この月題の2件のみ(頻度は低い)。

### R3(桁区切り): canonicalの「8,900」と転写の「8900」が不一致扱い — 確信度 高(コード・再現)
- `normalize_ja`の`_PUNCT_RE`(`er007_ja_asr_validator_01.py:55-59`)はASCII`,`を除去しない。`月のしわ、8,900本超`vs`月のしわ、8900本超`(他は全て同一)でも**TRUE_CONTENT_MISMATCH**(再現、`rc4`相当/`adversarial_panel_01`の`売上は1,200円です`vs`…1200円です`)。値ガード側(`extract_atoms_ja`)は桁区切りを正しく扱う(attempt2/AzureともEQUAL)が、**文字列比較層が先に落とす**。
- Azureは日本語で桁区切りを付けない(attempt2のAzure=`8900`)ため、canonicalに桁区切りがある限りAzureのSecondary受理は構造的に不可能。
- 影響範囲: JA canonical全363ユニーク中、桁区切りを含むのは**この題1件のみ**(`c4`相当の走査)。頻度は低いが、数値入り見出しが増えれば再発する。

### R4(Secondary受理に値等価層が無い): 仕様と実装の不一致 — 確信度 高(mock実行で再現)
- CURRENT_SPEC L2865は「日本語のSecondary受理集合は`EXACT_MATCH`/`NORMALIZED_MATCH`のみ(…**値等価正規化後の一致を含む**)」と明記。しかし実装の`_secondary_accept`は`classify_ja_asr_match`だけで、Primary側にだけある`_numeric_value_equivalence`(三人=3人)を**Secondary転写には適用していない**(`er007_ja_secondary_asr_01.py:643-650`)。
- mock再現(`mock_secondary_gap_01.py`、Azure関数を差替・実wav生成・API 0): canonical`三人で、お店に行きます`/Primary(NG)/Azure転写`3人で、お店に行きます` → **`NG_BOTH secondary_not_accepted`**(同一内容を漢数字で返したAzureなら`PASS_WITH_WARNING`)。Azureは数字を算用数字で返すのが通常のため、漢数字canonicalの数値入り文はSecondaryで救えない。
- 月題attempt2でも、仮にR1が無くてもR3とR4が重なって落ちる構造。

## 3. 3 attemptの“最小の是正”での帰結(オフライン試算、`proto_reading_compare_01.py`=Design A)
| attempt | 現行 | A1(桁区切り)+A2(助詞読み)+A3(値atom化＋残り読み比較)のみ | さらに案B(P1でAzure確認) |
|---|---|---|---|
| #1 `8000句800` | NG_PROTECTED | NG_PROTECTED(値DIFF=正しい) | Azureが`8900`を返せば救済可(Azure未呼出のため**実測不能**=Phase 3で¥0.3) |
| #2 `八千九百`/Azure`8900` | NG_BOTH | **Primary PASS**(値EQUAL+発音一致) | 同左 |
| #3 `8000900` | NG_PROTECTED | NG_PROTECTED | 同#1(Whisper medium=`8,900`) |
つまりA案だけで月題はattempt2で通り(HR回避)、attempt1/3の救済には案B(JAのP1で別エンジン確認)が必要。

## 4. 過去母集団での位置づけ(`ng_pool_cases_01.json`、`marginal_flip_eval_01.out.txt`)
- JA attempt 1,217件(attemptsファイル、`er*_output/**/attempts/*.json`でlanguage=ja)。JA lock状態1,151中HUMAN_REVIEW_REQUIRED=25(2.2%、検証・Trial含む全期間)。
- canonical復元可能なNG系150転写のうち、**現行Production(classify+numeric_equiv)が落とし、Design Aが通すもの=7件**(月題2、Melos「三日間/3日間」+同音(支配者/し|敗者)で4、Melosプレビュー1)。それ以外のNGの大半は**本当に違う文字列**(台風機/風師波、疲れきって→力きって/浸かり切って、渋滞→中断/中退、七晩→しつばん/七番、`42何々46`等)で、読み照合では通らない=真NGの候補(音声ラベルは未確認)。
- Primary(OpenAI mini)の誤転写は多い(`하실의 메로스`等のハングル、`台風機`)。PASS_WITH_WARNING(Azure救済)24件はいずれもAzureが原稿と同一表層=**AzureがJA ASRとして安定**(仮説: Primary/Secondary役割の最適化余地。ただしUDR #136で入替は不採用=ユーザー判断事項、本タスクでは提案のみ)。

## 5. 結論と未確認事項
- 月題の誤NGは**単一原因ではなく**、R1(助詞読み)・R3(桁区切り)・R4(Secondary値等価欠落)の“照合側3欠陥”+R2(OpenAI数詞崩れ+P1即打切り)の複合。
- 未確認: (a)attempt1/3をAzureが救えるか(Azure未呼出=実測なし。¥0.6/Phase 3)。(b)OpenAIの数詞崩れの再現性(同wav再転写。¥0.5以下/Phase 3)。(c)`超え`⇔`超`(Whisper `本超え`と#1のOpenAI`超え`):`ちょう`と`こえ`は読みが異なり、Design Aでは(厳格のため)通らない。実際の発音は不明(ユーザーは問題なしと判定)。Phase 3で扱いを決める(閉集合の表記ゆれ表 or 非対象)。
- なおmoon comment_2の「42から46メートル」(`約42〜46`・`42何々46`・Azure`4 16m`)は別事案(範囲値+単位メートル/m、値ガードUNKNOWN、`なになに`は2エンジン一致の可能性=TTS側の真の読み違い疑い、Whisper mediumは attempt3のみ`42何46`)。本タスクの対象外だが、Phase 3負例候補にする。
