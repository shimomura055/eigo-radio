# DESIGN_05: 2課題(①Std字義訳 / ②見出し語の人称placeholder)の包括対策設計(委任_13、2026-10-23、API 0・設計のみ)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_13 / 根拠=`ROOT_CAUSE_03.md`(原因)・USER_06(目標=2課題を実際に解消、未承認仕様のProduction Wiring不可、個別対策禁止、X/Z共通、既存の正しいKPを壊さない、不要なLLM工程の追加を避ける)
状態: **設計(未承認の新仕様案)**。Production/Prompt/flag/閾値/golden変更0。Trialは次委任(Opus条件Aレビュー後)。A-1は`APPROVED_FOR_PRODUCTION`のまま(併存設計、§4)。
略語: B仕様=承認済みAdv英語説明仕様(Prompt逐語・`PROMPT_SHA256`、`er019_family_x_kp_explanation_01.py:142`)。

## 0. 結論(推奨案)

| 課題 | 推奨 | 追加LLM call | Adv(B仕様)変更 | 既存KPへの影響 | 単価影響(推定) |
|---|---|---|---|---|---|
| ② 見出し語の人称placeholder | **指示対象の先行判定(`possessor_role`)をcanonicalizationの既存callの出力に追加し、one's/someone's/無変更への写像と検証を決定論で行う**(role↔placeholderが食い違えばroleに合わせてトークン1個を決定論で修復) | **0** | なし | 人称語を含まない項目は不変(約95%。45/885組=5.1%が人称語を含む)。人称語を含む項目も、roleと現行出力が一致する25/29件(86%)は不変、不一致4件だけが変わる(§2-4) | +0.005円/記事以下(出力約3トークン/項目+Prompt約250トークン) |
| ① Stdの字義訳 | **Std glossの独立再読検査+該当itemだけの再生成(検出→是正)**。検査はgloss段の新規生成直後に1 batch call(luna)。「figurative用法なのに日本語意味が字義の像しか持たない」と判定された項目だけを、既存の`previous_attempt_rejected`機構で1回だけ再生成(attempt上限2を守る)。未flagの項目は現行出力とバイト同一 | **+1回/記事**(検査、記事のgloss生成単位ごとに1回以内)+該当時のみ再生成(既存attempt枠内) | なし(glossが変わった項目のAdvは既存の`gloss_signature`で自動再生成) | 未flag項目は不変(構造的に非劣化)。flagされた正しい項目(偽陽性)のみリスク(測定対象、§5) | 約+0.1円/記事(検査0.05+再生成0.03〜0.05、費用見積の出典は§5-3)=70円目標の約0.14% |

- ①の低コスト代替(同一callに自己監査欄を追加し追加call 0): 同じTrialで併測し、検査callと同等以上なら**こちらを採る**(V0、§3-3)。
- ①②とも**個別対策(特定表現の辞書・few-shot)は含まない**。X/Z・a2/b1b共通のモジュール(`er003_key_words_canonicalization.py`、`er003_key_words_gloss_alignment.py`)の構造変更のみ。
- 採用までの経路: Offline Trial(DEV)→VALIDATED→**ユーザー正式採用**→Production配線(11-7の限定例外は本件のように既存Prompt/validatorを直接編集する変更には適用しない)。

## 1. 設計の前提・制約(照合済み)
1. 全KP工程のうち、本文を読んで意味を決める段は **選定**(Prompt 2逐語固定、schemaは`phrase,word_count`のみ: `er105_kp_fulltext_selector_01.py:74-95`)・**canonicalization**(全文を見る: `b1_p2_keywords_canonicalization_fulltext_prompt_template.txt`)・**Std gloss**(全文を見る: `er003_key_words_gloss_alignment.py:575-612`)・**Adv説明**(1文+glossのみ、b1bのみ)。選定の出力に意味を足すのは不可(OPEN-454、Prompt 2逐語固定)。
2. Std gloss段・canonicalization段はX/Z共通、a2/b1b共通(`er003_v1_n3_01_scaffold_generate.py:524-532`の共通経路。Z側は永続化済みartifactの人称整合修復のみ別、`WIRING_DESIGN_03.md` §2)。
3. 既存retry/fallbackの上限を守る: gloss attempt上限2(`MAX_GLOSS_ALIGNMENT_ATTEMPTS`、`er003_key_words_gloss_alignment.py:39`)、canonicalization技術retry上限2(`MAX_CANONICALIZATION_RETRY_ATTEMPTS`、`er003_key_words_canonicalization.py:690`)。新しい工程でこれらを迂回・拡張しない。
4. canonicalization schemaはA/B/C用とfulltext用が別定義(`:117-175`)。fulltext専用schemaにだけ項目を足せば、A/B/C(旧artifact経路)のschemaバイトは不変(`_fulltext_item_properties`、OF-KPFT-P-02(1)の既存方針)。

## 2. 課題②: 見出し語の人称placeholder

### 2-1 候補の比較
| 案 | 内容 | 追加call | 長所 | 短所・リスク | 採否 |
|---|---|---|---|---|---|
| **(a) role先行判定+決定論写像/修復** | fulltext schemaに`possessor_role`(none/self/other_person/non_person)を`key_phrase`の**前**に追加(strict structured outputではproperties順=生成順)。規則3の末尾に判定基準を3行追記。決定論側で role→許可集合: self→{one's,oneself}、other_person→{someone's,somebody's}、non_person→人称placeholder不可。食い違いはトークン1個の決定論修復 | 0 | 原因(選択基準と指示対象判定の欠落)に直接対応。選択を「確率的な好み」から「判定+写像」へ分離。LLMは易しい判定(誰を指すか)だけを担う。修復でINVALID/retryを増やさない | roleをLLMが誤判定すると、整合した誤りが残る(測定対象)。擬人化主語(`your wallet pumps its fist`)の扱いを基準文に明記する必要 | **推奨** |
| (b) 規則3の文言明確化のみ | 「本文の指示対象が主語自身ならone's、別の人ならsomeone's」と書く | 0 | 最小変更 | 確率的選択のまま。検証手段がなく、揺れ(同一入力でone's/someone's/無変更の3通り)を測れない・止められない。ユーザー指示「既存Promptの微修正に固執しない」に反する | 不採用(本設計の規則追記は(a)の入力定義に必要な範囲に限る) |
| (c) gloss側の逆検査 | 日本語意味から見出し語を逆検査 | 0〜1 | 既存の人称整合検査を拡張 | 日本語意味は見出し語に忠実に従うため、見出し語が誤っていればglossも整合してしまい検出できない(`ROOT_CAUSE_03.md` A-2-4) | 不採用 |
| (d) 一般化を廃止(原形維持) | 所有格は常に原形 | 0 | 誤りゼロ | 承認済み仕様(ER-011-NO18、PRODUCTION_WIRED)の撤回=ユーザー判断事項。学習価値(辞書見出し形)を失う | 不採用(仕様変更) |

### 2-2 推奨(a)の仕組み
1. **スキーマ**(fulltext専用、`er003_key_words_canonicalization.py` の`_fulltext_item_properties()`): `possessor_role`: enum[`none`,`self`,`other_person`,`non_person`]。`key_phrase`の前に置き、required。A/B/C schemaは不変。
2. **規則3追記**(A-1が規則5を足したのと同じ`_EDITS`方式、テンプレートの規則3の直後に挿入、特定の語句・記事に依存しない一般基準のみ): 「display_phraseに所有格・再帰代名詞が含まれる場合、置換の前にpossessor_roleを判定する。その語が指す対象が、この表現の動作主(または表現が述べる経験・所有の主体)自身ならself、動作主とは別の人ならother_person、人ではないもの(研究・組織・物・場所など)ならnon_person。動作主が擬人化されていて、その所有格が動作主自身を指す場合はself。該当語が無ければnone。置換はselfならone's/oneself、other_personならsomeone's/somebody'sに限る。non_personは人称のplaceholderに置換せず元の語のまま残す(規則1に従う所有限定詞の除去が適切な場合を除く)。迷う場合は置換しない」。
3. **決定論写像/検証**(`er003_key_words_canonicalization.py`、`_is_valid_person_generalization`の隣に`resolve_person_headword`を1関数追加): `person_generalization_pairs`相当で(display側トークン→key側トークン)の置換組を取り出し、role別の許可集合と照合。食い違いは**修復**(self: someone's/somebody's→one's、other_person: one's→someone's、non_person: placeholderを元の所有格へ戻す)。修復は語数不変の1対1置換のみで既存validator(`:452-473`、`er105_kp_fulltext_selector_01.py:676,694`)を通る。修復の事実は`person_role_repair`として項目に記録。許可表`_PERSON_DEPENDENT_TO_GENERIC`は、`my`・`our`にother_person用の`someone's`を追加するだけ(現状`my`→{one's}、`our`→{one's}のみで、`he will die in my place`型を表せない)。
4. **fail-safe**: roleが欠落・enum外・`none`なのに置換がある場合は、既存どおりINVALID扱い(技術retry枠内)。修復で解決できるものはretryを使わない(新しいINVALID原因を増やさない)。
5. **下流**: gloss段の`person_reference_mismatch`(`er003_key_words_gloss_alignment.py:205-228`)・人称制約文は**無変更**で残す(見出し語が正しくなれば日本語意味・Adv説明は見出し語に従って整合する)。Adv説明は`explanation_phrase`=`used_form`基準のsignatureで見出し語が変わったときだけ既存どおり再生成。

### 2-3 A-1(規則5)との整合・同梱
- A-1は規則5(this/that→a/an、目的格him/her/me/us→someone)をテンプレートへ追加(`er112_kp_gm_trial_01.py:94-125`の`A1_RULE5`/`_A1_EDITS`)。所有格は規則3の領域と明記(`:102`)されており、**責務は重ならない**。本案は規則3の追記と schema 欄の追加であり、規則5の文言・目的格の扱いには触れない。
- 目的格(`told her the truth→tell someone the truth`、`kept you company`)の指示対象はもともとother_person固定で、本案の対象外(roleは`none`でよい)。
- 配線順は A-1(承認済み・未配線)→本案(採用後)。同一テンプレートを触るため、同一の配線委任で`_EDITS`を連結し、同一回帰で確認する。テンプレートの`drift guard`(`oldは元templateにちょうど1回`)は追加の編集にも適用する。

### 2-4 決定論部分のAPI 0再計算(既存KP、`t3_possessive_sim.py`)
- 入力: 所有格を含み一般化された29件(Production artifact 24+DEV Trial_01 5)。role=T-1の目視ラベル(LLMのrole判定精度は次Trialで測定するため、ここは「roleが正しければ写像は正しい」の確認)。
- 結果: 不変25件、変更4件。

| 見出し語(現行) | 本案の見出し語 | role | 改善の種類 |
|---|---|---|---|
| `reach for someone's wallet` (display `reach for your wallet`) | `reach for one's wallet` | self | 自分→別の人 の取り違えを解消 |
| `go out of someone's way` | `go out of one's way` | self | 同上 |
| `lose someone's job` (she lose her job) | `lose one's job` | self | 同上 |
| `apply one's findings` (display `apply its findings`) | `apply its findings` | non_person | 人でない所有者(研究)を人称化していた誤りを解消 |

- 不変25件には `pump one's fist`(擬人化された主語のself)・`in your place→in someone's place`(other_person)・`shock your wallet→shock someone's wallet`(other_person)等が含まれる=正しいKPは壊れない(roleが正しい前提)。
- 限界: roleは目視ラベル。LLMが同じroleを出せるかは未測定。non_personの`its`が原形のまま残る場合は学習用の見出し語としてはやや具体的になる(意味関係は変わらない側へ倒す方針)。

### 2-5 retry/fallback・費用・Store reuse
- 追加call 0。canonicalizationの技術retry(上限2)・外側retry・Strategy L fallbackは不変。修復はretryを消費しない。
- 費用: 出力+約3トークン/項目、入力+約250トークン/call(推定)。0.005円/記事以下。
- Store reuse/signature: 見出し語が変わった項目のみ`used_form`が変わり、既存のsignature(`explanation_phrase`基準)でAdv説明とTTSが再生成される。reuse keyへの仕様ID追加は不要(新しいフィールドは`possessor_role`と`person_role_repair`の記録のみ、reuse判定に使わない)。

## 3. 課題①: Std日本語意味の字義訳

### 3-1 候補の比較
| 案 | 内容 | 追加call | B仕様変更 | 非劣化 | 長所 | 短所 | 採否 |
|---|---|---|---|---|---|---|---|
| A. Std/Adv用法整合チェック | StdとAdvが`usage_type`を出し、不一致ならStdのみ再生成 | 0〜1 | **あり**(Adv出力項目の追加=`PROMPT_SHA256`変更) | — | 独立な2つの目 | **a2のKPにAdvが無い**(カバレッジ欠如)、B仕様変更、判定の核はStd側の意味判断で結局LLMが要る、共有は先行データで悪化(E3)。既存データでは検出可能な3/3は上限値(`ROOT_CAUSE_03.md` B-5) | 不採用 |
| B. 生成構造の変更(G2/G3の本採用) | Std gloss生成にusage先決め(G2)/定訳→慣用句→中心義の案選択(G3)を足す | 0 | なし | **全項目の出力が変わる**(薄い△の増加、G2は`take the wheel`等を壊した) | 追加call 0 | G2は差し引き0(NG 6/28→7/28)。G3は字義NG 0だが△が増える(4対1)。層別の検出力不足で効果が確定していない。**全項目を変えるため、正しいKPを壊さない保証が構造的に無い** | 比較arm(参考)として併測。単独では不採用 |
| **C. 独立再読検査+該当itemのみ再生成(推奨)** | gloss新規生成後に、(KP・本文の該当文・gloss)だけを入力に、別callで「本文での用法」と「glossだけを読んだ学習者の受け取る意味」の食い違いを判定。flagされた項目だけをattempt 2で再生成 | +1/記事 | なし | **未flag項目は現行とバイト同一** | 原因(検査ゼロ)に直接対応。生成Promptを変えないので既存の正しいKPを壊さない。a2/b1b・X/Z共通のgloss段で完結。Advの独立性を保つ | 追加call(約0.05円/記事)。検査自体の偽陽性・偽陰性 | **推奨** |
| C'(=V0) 同一callの自己監査 | 既存gloss callの出力に`gloss_alone_reading_en`と`matches_usage`を追加し、食い違えば既存の検証失敗→retry(attempt 2)へ | 0 | なし | 生成Prompt追加あり(全項目の生成文脈が変わる)。出力は変わりうる | 追加call 0 | 同じ文脈での自己点検で独立性が弱い(同一callの確証バイアス)。生成と判定が同じ確率過程 | C'と同時にTrial。Cと同等以上ならC'を採る |
| D. 上位モデル(Sol)へ全面切替 | gloss生成を上位モデルに | 0 | なし | 全項目変化 | 単純 | Sol 1 call≈1.13円(luna比約15倍)で記事あたり約+2円、70円目標の約3%。字義/慣用判定精度の改善は未検証(Trial_02はdraw a lineのみ3/3) | 不採用。検査でflagされた項目の再生成だけSolを使う案をTrial armに入れる(§5) |
| E. Prompt文言のみの調整 | 「字義訳を避ける」を強化 | 0 | なし | 全項目変化 | 最小変更 | G1/G2の先行結果で効果不確定、ユーザー指示に反する | 不採用 |

### 3-2 推奨Cの仕組み(`er003_key_words_gloss_alignment.py`のalign_glosses内、attempt機構に接続)
1. 対象: **新規生成されたgloss**(`is_fulltext_gloss_missing`だったitem、`:253`)のみ。既存glossの修復経路(Zの人称整合修復、HUMAN_RESOLVED)は対象外=挙動不変(`WIRING_DESIGN_03.md` §2と同じ条件分岐)。
2. 検査call(luna、effort medium、strict structured output、記事のgloss生成単位あたり1回): 入力=各itemの`key_phrase`・`source_sentence`・`japanese_gloss`(記事全文なし、Advの出力なし)。出力(properties順=生成順):
   - `usage_in_sentence`: enum[literal, figurative, term, plain]
   - `gloss_alone_reading_en`: string(日本語意味**だけ**を読んだ日本語学習者が受け取る意味を、英語の短い句で)
   - `gloss_conveys`: enum[same_meaning, literal_image_only, narrower, broader, other]
3. flag条件(決定論): `usage_in_sentence == "figurative"` かつ `gloss_conveys == "literal_image_only"`。これだけを再生成の対象にする(narrower/broaderは対象外=偽陽性を抑える。薄い△は本件の範囲外)。
4. 検査Promptの原則(特定の語句・例を載せない): 「日本語として確立した慣用句・比喩で、日本語の読者もその比喩の意味で理解するものは`same_meaning`とする。字義の動作・物の像として受け取られる危険がある場合のみ`literal_image_only`」。
5. 再生成: flagされたitemだけ、既存の`previous_attempt_rejected`(`build_user_message_corrected`の`prior`、ITEM1 F1-3)に`{gloss, reasons:["日本語意味だけを読むと『<gloss_alone_reading_en>』の意味に取れる。本文での比喩の意味を日本語で表す"]}`を渡してattempt 2として再実行。attempt上限2を超えない(attempt 1が検証合格済みの項目のみが対象で、再生成はattempt 2)。
6. 失敗時の最終成果物: attempt 2が既存validate(括弧禁止・数字・人称整合・qa)に失敗した場合は**attempt 1のgloss(検証合格済み)を採用**し、`usage_check="FLAGGED_UNREPAIRED"`を項目に記録(HR/STOPにはしない。新検査は追加の品質管理であり、新しい停止原因を増やさない。既存のHR経路は既存validate失敗の場合のみ)。検査call自体の技術的失敗は**検査をスキップ**して現行出力を採用(`usage_check="SKIPPED_TECH_FAIL"`を記録しrun summaryで件数を表示)。**この「fail-open」は設計判断として明示し、Opusレビューの論点**とする。
7. 記録(監査用、reuse判定には使わない): 項目の`gloss_alignment.usage_check`(status、`usage_in_sentence`、`gloss_alone_reading_en`、`gloss_conveys`、再生成前のgloss)、run単位のflag件数・再生成件数・検査call費用。
8. Adv: 無変更(Prompt/schema/`PROMPT_SHA256`不変)。glossが変わった項目を含むb1bでは、既存の`gloss_signature`(X `er019_family_x_audio_production_runner_01.py:1073-1086`、Z `er026_family_z_fiction_production_runner_01.py:1517-1528`)により5件一括でAdvが再生成される(既存仕様)。

### 3-3 低コスト代替C'(V0)
Std gloss callのschemaに、`japanese_gloss`の**後**に`gloss_alone_reading_en`・`usage_in_sentence`・`gloss_conveys`を追加。flag条件はCと同一で、flag時は検証失敗として既存のattempt 2へ。追加call 0・追加出力約50トークン/項目(約0.004円/項目)。Cとの差は「判定が別callか同一callか」のみ。TrialでCと同条件に比較する(Cの方が検出率が有意に高い場合のみCを採る)。

### 3-4 既存データでの事前検証(API 0)と、できない部分
- 既存のStd字義NG 5出力・2KPを、本案の検査入力(KP・文・gloss)で検出できるかは、検査call(API)なしには測れない。**API 0で言えるのは次のみ**: (i)本案は生成Promptを変更しないので、未flag項目の出力は現行とバイト同一(構造的保証)。(ii)Std/Adv不一致型の検出はカバレッジが60%(Advがある3/5出力)でa2に無いため不適(§3-1 A)。(iii)通常KP(整合0件のE0@G0 40組)・難例E0@G0 60組の目視では、字義/比喩の両読みがありうるStd(`take the wheel`、`on the throne`等)が約2%あり、検査の偽陽性が起きうる型の目安になる(偽陽性率は次Trialで測定)。
- 検査の recall/FP は次Trialで測る(§5)。

## 4. 横断事項

### 4-1 既存仕様・過去Trial・撤去対象の整合
- 維持: `person_reference_mismatch`と人称制約文(`er003_key_words_gloss_alignment.py:205-228`、`PERSON_CONSTRAINT_TEXT`)・`qa_person_reference_generalized`・`_is_valid_person_generalization`(修復後も通る)・gloss attempt上限2・HR経路・canonicalization retry。**撤去する規則・検査・testは無い**(新規追加のみ)。Grep対象(採用時の旧規則残存確認): `_PERSON_DEPENDENT_TO_GENERIC`(`er003_key_words_canonicalization.py:431`、`er003_key_words_gloss_alignment.py:167,243`、`er105_kp_fulltext_selector_01.py:676`、`er003_test_key_words_canonicalization.py`、`er064_kp_idiom_*`)。
- 影響testの想定: canonicalization schemaのsha固定test(fulltext schema分のみ更新、A/B/Cのshaは不変)、gloss alignmentのgolden request(新規生成messageは本案で変わらない=検査は別call)。
- 過去Trialとの関係: `ROOT_CAUSE_02`が示した「検査・retryは意味品質に作用しない」を直接埋める(Cは検査工程の追加)。G2/G3の知見は比較armとして再利用する。E3(判断の固定共有は悪化)とは逆に、Cは判断を共有せず、**独立した第2の読みを足す**設計。

### 4-2 11-7限定例外の適用可否
本案はいずれも既存Production Prompt/validator/schemaの直接編集を伴う。**11-7の限定例外は適用しない**(条件(2)に反する)。採用前にProductionへ入れない。DEVでの実装は新規ファイル(`er112_kp_gm_trial_04.py`等)でProductionの関数を呼び、注入(`call_fn`)で差し替える。

### 4-3 Production到達経路に入る未承認機能の既定値
該当なし(Trial専用経路のみ)。採用時の既定値は「ON(採用された仕様として配線)」だが、採用はユーザー判断。

## 5. 検証計画(次委任、上限60円。X/Z共通のDEV注入、Production変更0)

### 5-1 対象・arm・判定
**② 人称placeholder**
- 対象: 既存45件(`t1_possessive_items.json`)+全artifact本文(64記事+725 keywords_canonicalized由来の文)から決定論で抽出した「所有格を含む3〜5語窓」約100件(KP候補として自然なもの)=約150件。層: self/other_person/non_person(Fableが事前ラベル)。
- arm(いずれもA-1の規則5入りをベースとする=配線後の現実): **C0A**=現行+A-1、**C1A**=C0A+`possessor_role`+決定論写像/修復。各2rep。
- 判定: Fableがroleと見出し語の正否を盲検でラベル。指標=(i)role判定精度、(ii)見出し語の指示対象整合率(C0A→C1A)、(iii)人称語を含まない項目の不変率(非劣化: C0Aの2rep間の不変率をノイズ基準にして比較)、(iv)修復の発火率、(v)費用。
**① 字義訳**
- 対象: 既存artifactの異なる(KP,文)885組(`t2_pool_census.py`)から、**結果に依らない事前層別**(1回のluna分類callで「字義読みも文法的に成立する比喩・慣用」F層/「コロケーション・用語・句動詞」N層)。F層から90KP、N層から30KP、既知NG 2KP(anchor、主評価からは除外)。
- arm: **B0**=現行(G0) 2rep、**C**=B0の出力→独立再読検査→flag項目のみluna再生成、**C'**=同一call自己監査(新規生成2rep)、**G3参考**=1rep(F層のみ)、**C-Sol**=Cのflag項目の再生成をSolで(luna再生成で残存NGがある場合のみ実行、1rep)。
- 判定: Fable盲検(arm伏せ、同一文字列は1回採点、PASS/△/FAIL+字義訳/語義誤認/文法・意味関係/その他の分類)。Sonnet Judgeは使わない(費用・参考値の混乱を避ける。過去のSonnet参考と最終Fableの乖離83/360セル)。
- 指標(事前宣言): (i)F層の字義訳NG率 B0 vs C vs C'(出力・KP単位)、(ii)検査のrecall(flag∩NG/NG)・precision(flag∩NG/flag)、(iii)flag項目のBefore→After(改善/不変/悪化)、(iv)未flag項目の不変性(構造的に100%の確認)、(v)△率の変化(N層、非劣化)、(vi)追加call数・費用/記事相当、(vii)Std薄化がC(再生成)で起きていないか。
- 事前宣言の判定基準(Fable/ユーザー確認事項): VALIDATED候補= F層の字義訳NGが B0の1/3以下、かつ全出力に対する新規悪化(PASS→FAIL/△)≤1%、かつ追加費用≤0.15円/記事相当。基準値は提案であり、ユーザー定義水準ではないため、Trial前にFableが確認する(品質基準の自己引き下げ・引き上げをしない)。
**X/Z E2E(text工程のみ)**: Production関数を`call_fn`注入で呼び(`er112_kp_gm_e2e_02.py`の方式)、X1記事+Z1記事のcanonicalization→gloss(検査込み)→Adv説明まで実行。artifact構造・signature・再生成連鎖・Advの`PROMPT_SHA256`不変・retry統計・Production hashの前後一致を確認。

### 5-2 Before/After例・件数の出し方
改善件数/残存NG/新規悪化件数を、KP単位のflip表(improve/regress/same)とWilson CIで報告。Before/Afterは各課題上位5例+全悪化例を逐語。

### 5-3 費用見積(出典付き、上限60円。見込み=約40円、Sol arm含む最大約54円)
単価の出典: gloss 1call平均 G0 0.070円/G3 0.104円(`WIRING_DESIGN_03.md` §4、Trial_03 `paid_calls.jsonl`)、canonicalization等の生成1unit平均0.103円(Trial_01 `paid_calls.jsonl` gen 400件41.32円)、Adv説明1KP 0.0139〜0.0156円(Trial_02/03 `paid_calls.jsonl`)、Sol 1call 1.13円(Trial_02実測)。検査call単価0.05〜0.06円とluna再生成0.1円は**トークン数からの推定**(実測は次Trial冒頭の小規模実測で更新)。
| 区分 | 呼出数 | 単価 | 小計 |
|---|---|---|---|
| ①層別分類(885組/40件) | 22 | 0.08 | 1.8 |
| ① B0 gloss(120KP/3件×2rep) | 80 | 0.070 | 5.6 |
| ① C' gloss(同上、自己監査込み) | 80 | 0.09(推定) | 7.2 |
| ① G3参考(F層90KP/3件×1rep) | 30 | 0.104 | 3.1 |
| ① 検査call(120KP/8件×2rep) | 30 | 0.06(推定) | 1.8 |
| ① luna再生成(flag想定15%≈36KP/3件) | 12 | 0.10(推定) | 1.2 |
| ② C0A/C1A(150件/5件×2arm×2rep) | 120 | 0.103〜0.12 | 12.4〜14.4 |
| E2E text(X1+Z1) | 約40 | 0.03〜0.1 | 約3 |
| **見込み小計** | | | **約37〜39** |
| ① C-Sol(条件付き、flag項目12call) | 12 | 1.13 | 13.6 |
| **最大(上限内)** | | | **約52〜54** |
KP案件累計≈170円→最大≈224円(7-7の300円内)。**60円を超える設計になった場合は設計書へ明記しFableがユーザーへ諮る**(本設計は超過しない)。

## 6. 既存の正しいKPを壊さない保証
- ②: 人称語を含む項目(約5%、45/885組)のみ対象。roleが正しければ現行から変わるのは不一致項目(29件中4件)だけ。人称語を含まない項目は`none`で不変。ただし規則3追記・schema変更はcanonicalization call全体の文脈を変えるため、**人称語を含まない項目の不変率をC0Aの2rep間ノイズ基準で測る**(非劣化の測り方: 第3回の自己一致率基準=同一入力2repの一致率を基準線として、差が基準線のノイズ内かを判定)。
- ①C: 未flagの出力は現行とバイト同一(生成Promptを変えない)。flagされた項目のみ再生成され、その品質(Before→After)を全件盲検で確認する。
- 採用判断までProductionは無変更。

## 7. ユーザー判断が必要になる事項(採用段階。Trial実施自体はUSER_06の「改善Trialまでの継続承認」の範囲内、B既判断)
- D(真に新しい判断、採用時): (1)記事あたり+1回のLLM call(検査)を許容するか、同一call自己監査(C')で足りるか。(2)canonicalizationの規則3追記とschema欄追加(承認済みPromptの変更)。(3)検査call失敗時のfail-open(スキップ)と、再生成失敗時のattempt 1採用(WARN記録、STOPなし)という安全方針。(4)事前宣言の判定基準値(新規悪化≤1%等)をユーザー定義水準として確認するか。
- 上記はいずれもTrialでVALIDATEDになってから、採用提案としてまとめて諮る。現時点で新たなユーザー判断は不要。

## 8. 失敗終了時の最終成果物
本委任は設計のみ。成果物=`ROOT_CAUSE_03.md`・`DESIGN_05.md`・`OPUS_REVIEW_REQUEST_05.md`・分析script・`docs/pm/RESULT_PACKET_KPGM13.md`。Trialが失敗・不採用となっても、2課題は未解消のまま残る前提で、Closeせず再設計する(USER_06「Trialが失敗しても課題を終了扱いにしない」)。
