# TRIAL_DESIGN_06: 課題① 字義訳 Trial_05 設計確定(OPUS_REVIEW_07 OF-KP1-01〜08反映、委任_22、2026-10-24)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_22 / 前版=`TRIAL_DESIGN_05.md`(本書がarm構成・判定基準・schemaで優先) / 対策案=`DESIGN_07.md`(§0-R改訂) / 原因=`ROOT_CAUSE_04.md`(§0-R改訂) / レビュー=`OPUS_REVIEW_07.md`
状態: **有料runの前に確定(判定基準は出力を見る前に固定=事前宣言)**。DEV/Trial専用(er112、`er112_kp_gm_trial_05*.py`)。Production module(`er003_*`/`er019_*`/`er026_*`/`er105_*`)は編集せずimportのみ。課題②(委任_20)のコード/SSOTには触れない。

## 0. 使用モデル(25節、最新モデル原則)
生成=`gpt-6-luna`、reasoning effort=**high固定**。最新世代の最上位系ではない。例外理由=評価対象がProduction系列のluna生成の品質そのもの(Trial_04と同一条件、armの差だけを見るため)。判定=Fable盲検(API 0)。Sonnet参考Judgeは使わない。luna・effort=high固定での検証であることを採用判断資料にも明記する(OF-KP1 Production判断用資料(c))。

## 1. arm構成(OF-KP1-02/03反映)

| arm | 内容 | 出力schema | rep | 備考 |
|---|---|---|---|---|
| **B0** | 現行Production gloss生成(`ga.build_user_message_corrected`+`GLOSS_ALIGNMENT_JSON_SCHEMA`) | Production | 新規3 | 選択バイアスの対照(既存Trial_02〜04のB0は推定に使わない) |
| **M** | 再整合用の指示・例・qa名を除いたM-base(制約句は残す) | M_SCHEMA(rank,gloss) | 既存2rep(Trial_04)を参照+**新規1rep** | H5の対照(M対X1) |
| **X1** | M-base+制約句の置換のみ(欄追加なし) | **Production互換**(下記) | 新規3 | H5検証。**M対X1**で比較(OF-KP1-02)。Mとはschemaも異なる(Production互換欄を追加)ため、純粋なH5比較でなく『H5+Production互換欄』の比較になる点を限界として記録 |
| **X2** | X1+`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`→gloss | **Production互換+新欄** | 新規3 | 案A |
| **Cp** | Trial_04のCp(自己監査欄、gloss後)をそのまま再実行 | Cp schema(Trial_04と同一) | 新規3(既存1repも参照) | OF-KP1-03: armとして並べる |

KP集合: **R**=hard-core 4KP(`draw a line`/`an unseen clock`/`question shaped like a trophy`/`greener grass`)+co-KP3(`come down`/`behind the scenes`/`sound no one asked for`、同記事)=7KP、4 call/rep(`trial05_plan_counts.json`)。**held-out**: 下記§2。

## 2. held-out challenge set(OF-KP1-04。事前固定の基準、gloss出力は一切見ない)
- 選定script=`er112_output/kp_gm_trial_05/heldout_select_05.py`(再現可能、seed=22)。母集団=Production run由来 `keywords_canonicalized.json`(`er112_kp_gm_kpset_03.candidates`と同じ走査範囲・除外規則)のKPで、(a)all_kps()の115KP(Trial_02〜04使用)・`PRE_A1_DROP`・R 4KPを含まない、(b)canonicalizationの`reasoning`が`比喩|慣用|イディオム|熟語|figurative|idiom`を含む(`canon_reasoning_census.py`の比喩認識と同一基準)、(c)本文からsource_sentenceが復元できる。
- 該当は17KP(X 15、Z 2)。**Z(小説)は全数**(`rise above`・`tiny bomb`)、Xは`random.Random(22)`で抽出。予算に応じた件数は、**抽出順の先頭からN件**(結果非依存)で打切る。Nは費用pilot後に決め`heldout_selection_log_05.json`へ記録。
- 限界: ZのF型KPは母集団に2件しか無い(Z小説の比喩は十分に網羅できない)。
- arm=B0/X2/Cp、各1rep(OF-KP1-04)。

## 3. Production互換schema(OF-KP1-07)
`ga.GLOSS_ALIGNMENT_JSON_SCHEMA`の必須欄(`rank`/`current_gloss_consistent`/`japanese_gloss`/`qa_reflects_all_key_phrase_words`/`reasoning`/`added_word_mappings`)を残す。X2の新欄は**`japanese_gloss`の直前**に挿入: `current_gloss_consistent`→`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`(enum yes/partly/no)→`japanese_gloss`→`qa_reflects_all_key_phrase_words`→`reasoning`→`added_word_mappings`。X1は新欄なし。messageには、Production互換欄の書き方を短く明記する(新規生成のため`current_gloss_consistent`は必ずfalse、`qa`はkey_phrase全体の意味を反映できているときのみPASS、`added_word_mappings`はProduction指示3と同文、`reasoning`は判断の根拠を短く)。item JSONに`added_content_words`を含める(M-baseは持たなかった)。

### 3-1. 経路の確定(OF-KP1-07。Grep根拠は§5)
- **今回のTrialの対象=新規生成経路のみ**(current gloss=null、`is_fulltext_gloss_missing`が真のitemだけ、全itemがnull)。X1/X2のmessageはこの経路専用に組み立てる。
- **混在batch(current glossありとnull)**: Productionでは`select_generation_targets`が再整合対象(人称一般化・語の追加)と新規生成を同一callにまとめうる。X2はnull項目専用の指示であり、混在時の挙動は**未検証**。採用設計時の課題として、第1案=『null項目はX2 call、current glossあり項目は現行Productionのcall』の2 callに分離(混在記事のみ追加call、費用は混在率に依存)、第2案=単一callで項目別の条件分岐(未検証)。今回は判断しない。
- **Z repair経路(`er026_family_z_fiction_production_runner_01.py` l.1552 `ga.align_glosses(... only_ranks=ranks)`)と再整合経路**: current glossが非nullの項目(人称不整合の修復)が対象で、M-base/X2は適用されない(現行Prompt+人称規則のまま)。今回の対象外。採用設計時の課題として明記。
- X/Y/Zとも`align_glosses`(`er003_key_words_gloss_alignment.py:813`)を共有するため、採用時の変更箇所は`build_user_message_corrected`の新規生成分岐+新規生成用schema分岐の1箇所。

## 4. 事前宣言の判定基準(OF-KP1-06。出力を見る前に固定)

### Stage 1 R(hard-core、4KP×3rep=12出力/arm)。ラベル=PASS/THIN/FAIL/FAIL_LIT(Fable盲検)
- **有効(X2またはX1またはCp)**: 次の**3つを全て**満たす: (1) (FAIL_LIT+FAIL)≦**1/12**、(2) 3rep中**2rep以上**失敗するKPが**0**、(3) THIN≦**B0のTHIN数+1**。
- B0の期待FAIL_LIT≧4/12(未満なら『検出力不足/平均への回帰』と記録しrep追加の要否を報告)。
- M2(診断): X2の`naive_ja_conveys`がR 12出力で`no`/`partly`になる割合(期待≧10/12)。`yes`が多ければ確証バイアスで形骸化と判定。
- **X1対M**(H5): X1の(FAIL_LIT+FAIL)がMより減るか。Mは既存2rep+新規1rep(計3rep)。
- **X2対Cp**: X2が(FAIL_LIT+FAIL)・THINともCp以下かつ1call費用が安い→案A。X2がCpに劣る→案C最適化版(英語文を1文にし未使用の`gloss_conveys`を削除)を次案。

### held-out(各1rep、arm=B0/X2/Cp)
- 通過: **X2とCpがB0より悪化(B0がPASSでX2/CpがTHIN/FAIL/FAIL_LIT)したKPが0**。かつ X2/Cp の(FAIL_LIT+FAIL)がB0以下。

### Stage 2(S+co-KP 57KP、1rep、Stage 1通過後のFable連絡を受けて実施)
- 主基準(strict): **B0の良い方のrep**(KPごと、2rep中ラベルが上位)に対する悪化: **PASS→FAIL/FAIL_LITが0**、**PASS→THINが≦2/57**。
- 併記(lenient): B0の悪い方のrepとの比較。
- 追加計測(決定論、0円、OF-KP1-05): (a) `gloss==naive_ja`率、(b) N層の直訳調THIN(Fable盲検でTHIN理由が直訳調と分類されたもの)、(c) 文字数比(X2のgloss文字数/B0のgloss文字数)>1.5倍の件数、(d) 説明文型語尾(「～こと」「～もの」「～ようす」「～という」等で終わる、または全角30字超)の件数。
- 提示資料(OF-KP1-06): B0とX2/X1/Cpの文字列、`meaning_in_text_en`、conveys、ラベルのBefore/After、残存NG、新規悪化、yes/partly/no分布と誤判定例。

## 5. Grep確認(OF-KP1-07、API 0)
- A/B/C旧ライン(凍結中)が新規生成経路を通らない: `is_fulltext_gloss_missing`(`er003_key_words_gloss_alignment.py:270-273`)は`fulltext_source_ref`マーカーがあるitemのみ真(docstring: 『A/B/Cのitemは該当しない』)。`fulltext_source_ref`の設定箇所=`er105_kp_fulltext_selector_01.py`/`er003_key_words_canonicalization.py`のみ(全文選定=X/Z/Y系)。Gloss再整合の呼出元は`er003_v1_n3_01_scaffold_generate.py:539`(X/標準経路)と`er026_family_z_fiction_production_runner_01.py:1552`(Zの人称修復、current glossあり)のみ(`align_glosses(`のGrep、Trial/test除く)。
- 結果はTRIAL_RESULT_05.mdにもGrep出力を引用する。

## 6. Fable盲検の再現性(OF-KP1-08、0円)
盲検表`fable_blind_05.md`に、Trial_04で確定済み(`fable_labels_04.json`)の文字列を約10件(R・Sから、PASS/THIN/FAIL/FAIL_LITを混ぜる、seed固定)、arm伏せのまま混在させる(key別ファイルに分離)。Fable再判定と既存ラベルの一致率を記録し、新造比喩(trophy等)の正解幅のぶれの指標とする。

## 7. 費用・実行(委任_22 §0)
- 残存個別枠=Trial_04枠3.43円+rep2枠4.90円=**8.33円**(台帳`er112_output/kp_gm_trial_04/paid_calls.jsonl`の合計76.672円=56.57+20.10で再確認、60+25枠)。Stage 1+held-outはこの範囲。Stage 2はStage 1通過後にFableが7-7自律判断で実行。
- 費用pilot(上限0.20円/call)→本実行。cap検査=発行前累計+そのcallの見込み。workers≤2〜3。台帳=`er112_output/kp_gm_trial_05/paid_calls.jsonl`、記録=`TRIAL_05/BUDGET_LOG_01.md`。
- 追加計測: 各callの`reasoning_tokens`を新ledgerに記録(OF-KP1-03、既存ledgerのluna gen行には未記録)。

## 8. 撤去・残置
撤去する規則・検査・testは無い(新規DEV追加のみ)。残置: Production現行Prompt/schema(B0)、Trial_04の`M_HEAD`/`M_NEWGEN`/`CP_BLOCK`/`cp_schema`(DEV、再利用)。
