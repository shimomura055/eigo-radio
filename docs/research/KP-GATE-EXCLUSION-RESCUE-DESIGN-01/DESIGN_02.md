# DESIGN_02: Key Phrase候補「除外→修正救済」方式の設計(DESIGN_01にOpus条件AレビューM1〜M6・R1〜R4を反映。X/Y/Z共通・調査設計のみ・API 0)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-01 委任_02 / 到達上限Status=`DESIGN_DONE_USER_DECISION_PENDING`(Fableが`USER_DECISION_REQUIRED`で報告)。Productionコード・Prompt・Gateは変更していない。実装0・API 0・JPY0。AI島run_ai_01のHR候補は未確定のまま保全。
改訂元=`DESIGN_01.md`(Claude案。本文は無改変で残置)。レビュー原文=`OPUS_REVIEW_01.md`(逐語)。Fable照合結果: DESIGN_01とOpusは「段階1採用推奨・2c保留・救済候補はAUTO不可既定」で一致。Opus M1〜M6・R1〜R4は設計の穴の是正で、既存のユーザー承認内容を変えず新Product原則も加えないため、Fable判断(11-3)で全件採用した。
設計の中心(ユーザー指示・不変): 解決したいのは「8件に届かないこと」ではなく「適切に修正できる候補まで捨ててしまうこと」。**候補数の補充(数合わせ)は目的としない**。救済は「既に選ばれた候補を、承認済みGateを変えずに残す」ことだけを行う。

## 0. DESIGN_01からの変更点一覧(M/R対応)

| ID | Opus指摘(要旨) | DESIGN_02での反映 | 反映先 |
|---|---|---|---|
| M1 | 再導出の全組合せ列挙は、LLMが提案していない誤った基本形(`hoped for`→`hop for`、`takes notes`→`takes note`、`him`→`someone`)を採用し得る | 再導出を「display窓の中で、各tokenを{display側の語, LLMがその位置に出した語}のどちらかから選ぶ」だけに限定。`_verb_base_candidates`や単数化表から新しい語形を生成しない。同点は決定論で決め、迷う場合はrevert優先。source_spanへの拡張は再導出の対象にしない | §2(1) |
| M2 | hookが`is_fulltext`だけで有効になり、HRを経ない経路(`scaffold:883-888`のrun_key_phrases→run_kp_with_outer_retry、Zの`run_kp_with_outer_retry_fulltext` `er062:1364-1373`)でも救済KPが旗・HRなしに確定する | 有効化を`er119 generate_candidates`経路だけに限定(canon_fnへ明示引数を渡す方式・既定OFF)。HRを経ない経路は出力バイト同一をtestで固定。または当該経路がProductionで使われていない証拠を示す | §2(2)・§7 |
| M3 | gloss再整合は「最終KPに表示候補にない語がある場合だけ」動く(`scaffold:523`)。revertでは対象0件となり、LLMが自分のkey向けに作ったglossが残る(例: `hold out one's hands`の「両手を差し出す」が`held out`に付いたまま) | 救済したrankについてgloss再整合を強制(`align_glosses(only_ranks=)`)。再整合できなければ`gloss_hr_pending`旗。「段階1はLLM 0」を訂正: 救済成立時にgloss再整合call 約0.5円/件[出典: a2実測0.526〜0.563円] | §1・§2(a)・§5 |
| M4 | LLMのqa_*欄は救済前のkeyへの判定。HR表にPASSと出るとユーザーを誤らせる | LLMのqa_*欄は上書きしない(roles処理の先例`er105:988`のPASS上書きは救済には入れない)。`gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`を付け、HR表は「QA未再判定」と表示(PASSとは表示しない) | §2(c) |
| M5 | 「外側retryの条件を緩めも厳しくもしない」は事実と違う。救済成功句が`gate_dropped`から消える(`er119:329`)と「AUTO可<3」時のretryが発動しなくなる=M-7(c)の挙動が変わる | 外側retryのトリガー判定では救済句を`gate_dropped`相当として数える(現行挙動を維持)。累積除外リスト(F1)には入れない。現行と異なる挙動を採る場合はOI-1で「挙動変更」として明示しユーザーに諮る | §2(d) |
| M6 | 救済内のvalidator呼出が最終Gateと引数が違うと「救済したのにINVALID」が起きる | 救済内のvalidator呼出は最終Gateと完全に同じ引数(`canonicalization_view_items`のspan、`original_span`、`allow_inflection_normalization=_is_ft`、`role_ok_poss=_role_ok_poss_of(item)`)。rolesがUNVERIFIED/NO_WINDOWなら一般形の所有格tokenをdisplay側の語へ戻す。元の除外理由は`rescue.before.reasons`に保存 | §2(1)・(c) |
| R1 | トリガーが「Rule7(基本形化)」に限定され、revertで救える他の除外を拾わない | トリガーを「LLMのkeyが原因の構造違反全般」+「`cmu_post_canon`」へ拡張。救済手段はrevertのみ(受理面不変)。revert後のCMU再検査は必須 | §2(1) |
| R2 | 2cを将来採用する場合の歯止め | 2cの採用条件として記録(2cは保留のまま): 否定・程度を表す語(`too/not/never/no/only/hardly`等)を削る部分列を決定論で禁止、HR表に元の6語句と元の本文の文を併記 | §2(a)・§6 |
| R3 | 外側retryの候補置換・call1選定retryで消えた句が記録されない | `dropped`とinventoryへ記録(観測のみ。救済はしない) | §2(d)・EXCLUSION_PATTERNS_01 §4 |
| R4 | testの追加 | 実装時必須test 3件: (1)実在語だが誤った基本形(`hoped`→`hop`)を採用しない (2)HRを経ない経路が分離されている (3)救済あり/なしで外側retryの発動回数が同一 | §7 |
| (C) | 棚卸し対象外のGate除外経路4件 | EXCLUSION_PATTERNS_01 §4へ追記(件数は分かる範囲、不明は「未集計」) | EXCLUSION_PATTERNS_01 §4 |
| 記述修正 | `_containment`/overflowの再適用は救済後の句がdisplay窓の中に収まるため実質不要(何もしない処理) | DESIGN_01の「再適用」を「実質不要」に訂正 | §2(b)・(d) |

## 1. 結論(先に)

1. 実データ(HR導入後のGate除外11件)のうち、**承認済み規則内で機械的に救済できるのは4件(36%)**。残りは新規則(ユーザー承認)が必要な3件(27%)と救済困難4件(36%)。HR導入前の一意句29では同12件(41%)/2件(7%)/11件(38%)/現行で既に通る4件(14%)(RESCUE_ANALYSIS_01 §1)。数値はDESIGN_01から変更なし(M1の制限でS1件数が減るかは、実装時のoffline再生検証で確認=未確認)。
2. 救済の部品は承認済みの先例がある。`postprocess_possessor_roles`(`er105_kp_fulltext_selector_01.py:927`、UDR #173②・2026-10-24承認)が「canonicalization応答のparse直後・validate前に、決定論で『revertのみ』行い、validatorを通ることを確認できなければ無変更」を実装済み(hook=`er003_v1_n3_01_scaffold_generate.py:502-507`)。revertは設計意図`er105:575`(V+名詞等は基本形化せず表層形のまま)をむしろ忠実に実装する形で、現行実装(LLMが基本形化を試みて失敗するとitemごと落とす)のほうが意図とずれている(Opus論点2)。
3. 救済フロー自体は11-8の「新しい処理方式」(Productionの出力=HR候補の集合・表示を意味的に変える)に当たるため、**救済フロー全体は範囲外=ユーザー判断**(Opus(A)もこの判定)。受理面を広げる項目(段階2)は項目ごとにユーザー承認が要る。
4. **「段階1はLLM 0・費用0」ではない(M3で訂正)**: 救済成立時にgloss再整合の追加call(約0.5円/件)が要る。判定・再導出・revertの部分は決定論(API 0)。
5. AI島 `studied separately` は段階1で**表層形のまま**HR候補に残せる(既存validator通過を机上確認)。原形`study separately`は新規則(2b)。`too soon to wave a flag` は段階1では救済できず(2c)、ユーザー例`too soon to do`は現行規則でも段階2の範囲でも通らない別種の新規則(本文に無い語の生成)になる。

## 2. 救済フロー(候補抽出 → Gate検査 → 違反検出 → 修正可能性判断 → 修正 → 再検査 → HR候補登録)

```
[既存] call1(Prompt 2)/call2(Prompt 2-V) -> 選定gate(validate/重複/NG/CMU)
                                          \-> 違反検出(1): 語数>5 = 救済点B(段階2c、保留)
[既存] canonicalization(LLM) -> parse -> postprocess_possessor_roles(roles)
   [新: 救済点A] postprocess_lemma_repair  ※er119 generate_candidates経路のみ(M2: canon_fnへの明示引数・既定OFF)
        トリガー(R1): 最終Gateと同一引数(M6)でvalidatorに通し、LLMのkeyが原因の構造違反
                      (Rule7基本形化/OF-X1/canon段の語数・有限助動詞混入 等)で落ちるitem
                      + cmu_post_canon で落ちるitem(revert後のCMU再検査が必須)
        修正可能性判断(決定論の2段。新語形は生成しない):
          (1) 再導出(M1): display窓の中で各tokenを {display側の語, LLMがその位置に出した語} から選ぶだけ。
              _verb_base_candidates・単数化表から新しい語形を作らない。同点・迷う場合はrevert優先。
              source_spanへの拡張は対象にしない。最終Gateと同一引数のvalidator+CMUを通るもののみ
          (2) revert: key_phrase = display_phrase(無変更。Rule7の『無変更』= er003_key_words_canonicalization.py:599)
              rolesがUNVERIFIED/NO_WINDOWの場合は一般形の所有格tokenをdisplay側の語へ戻す
        修正: item.key_phrase / normalization_reason / changed_from_display_phrase を更新し rescue を記録
        再検査: 同じ validate_canonicalization_response を全体に再適用(M-7(a)「全体PASSのみ受理」を維持)
        失敗: 無変更のまま(現行どおり INVALID -> item除外 -> 残りで再実行 -> dropped記録)
[既存→強制] gloss再整合: 救済したrankは align_glosses(only_ranks=) で強制(M3)。できなければ gloss_hr_pending 旗
[既存] CMU post-canon -> 記号 -> (Z: 人称整合/SRC D1) -> NG(used_form) -> 候補ID -> Redundancy QA
[新] 候補に rescue 記録と flags.rescued を付け、gates.canonicalization="RESCUED_QA_NOT_REJUDGED"(M4)でHR候補(kp_candidates.json)へ登録
```

(1) **修正可能性判断(M1/M6/R1)**
- 再導出が採れる語形は、display窓のtokenと、LLMがその位置に出したtokenのどちらかに限る。例: `studied separately`(display)に対しLLMが`study separately`を出した場合、位置1は{`studied`,`study`}から選べるが、`study separately`は最終Gate(`_guard_ok` `er105:662`)で拒否されるため、結果は`studied separately`(revert)と同じになる。`hoped for`に対しLLMが`hope for`を出した場合は、`hop for`のような「LLMが出していない」語形は候補に入らない(CMUでは`hop`も実在語で区別できないため、新語形生成を許すと誤りを防げない)。
- 人称の一般化(`him`→`someone`等)もLLMがその位置に出した場合に限る。再導出が自分で作った人称置換が`_token_pair_ok`のguard(`er105:664`、key側の次トークンを見る)をすり抜ける経路を塞ぐ。
- `role_ok_poss`は最終Gate(`er003:697`の`_role_ok_poss_of(item)`)と同じ値を渡す。空集合を渡すと受理が狭まるだけだが、最終Gateと判定がずれて「救済したのにINVALID」が起きる(Opus論点2)。
- 元の除外理由は`rescue.before.reasons`に保存する(監査)。

(2) **有効化範囲(M2)**: hookは`er119_kp_candidates_01.py generate_candidates`が`canon_fn`へ明示引数(例: `rescue_lemma_repair=True`、既定False)を渡したときだけ有効。`is_fulltext`だけで有効にならない。HRを経ない経路=`run_key_phrases`→`run_kp_with_outer_retry`(`er003_v1_n3_01_scaffold_generate.py:729,883-888`)と`er062_family_z_writer_01.py:1364-1373`の`run_kp_with_outer_retry_fulltext`は、救済ONでも出力がバイト同一であることをtestで固定する(実装時、R4(2))。あるいは当該経路がProductionで使われていないことを証拠で示す(実装時に確認)。flag名は実装時に決め、`OPEN_ITEMS.md`に「未承認・既定OFF」を記録し、PRODUCTION_WIREDとは呼ばない(11-7)。

(a) **機械的修正で足りるものとAI(追加LLM call)が必要なもの**

| 区分 | 内容 | 方式 | LLM call | 段階 |
|---|---|---|---|---|
| 機械(決定論) | 表層形revert、M1制限付き再導出、人称一般化のみ残す再導出 | `postprocess_lemma_repair` | 0(判定・修正) | 1 |
| 機械+AI(後続) | 救済したrankのgloss再整合(救済前のkey向けに作られたglossは使えない) | 既存`align_glosses`を強制 | **1 call/救済件(約0.5円)** | 1 |
| 機械(決定論・表の拡張) | W1 guard限定詞追加(`no`,`each`…)、W2 guard副詞追加、W3 過去形専用表の補完(`rang`…) | 閉表/guardの拡張(新規則) | 0 | 2a/2b |
| 機械(検査精緻化) | lexical `have`を有限助動詞扱いしない | `_contains_finite_auxiliary`の精緻化(新規則) | 0 | 2e |
| **AI判断要** | 6語以上の短縮(どの部分列が意味を保つか。`too`を落とすと意味が反転する実例あり) | 新規「短縮提案」1 call(Prompt 2/2-Vはsha固定のため新Promptが必要=Opus条件A/ユーザー承認) | 1/該当句 | 2c(保留) |
| 不可 | 本文に無い語の生成(`too soon to do`)、CMU未登録、modal/進行形auxを核とする句、本文不一致、Human NG | 救済しない(2d: スロット一般化は非推奨) | - | - |

2c(AI短縮提案)の呼出条件・回数上限(保留案): 選定段で語数>5のみ・1句につき最大1回・1レベル最大2句まで・候補は元句の連続部分列に限る(本文対応保持)。提案は`dropped[].rescue_options`に記録するだけとし、候補にするかは(i)出た部分列を既存パイプラインに通す、(ii)通過したものだけ`rescued`旗付きで候補化、の順。**将来採用する場合の必須条件(R2)**: 否定・程度を表す語(`too/not/never/no/only/hardly`等)を削る部分列を決定論で禁止し、HR表に元の6語句と元の本文の文を併記する。これに加えHR選択と`auto_eligible=False`が必要(Opus論点1)。**推奨は2cを今回は採用せず保留**(発生率が低い=HR導入後14イベント中1件、かつ意味反転リスクのため)。

(b) **再検査**: 新Gateは作らない。救済点Aは既存`validate_canonicalization_item`/`validate_canonicalization_response`を、最終Gateと同一引数(M6)でそのまま呼ぶ(`postprocess_possessor_roles`が`er105:976-978`で同関数を呼ぶ先例)。修正後の候補はその後の全段(CMU post-canon・記号・gloss・Z限定SRC D1/人称整合・NG・Redundancy QA)を通常候補と同条件で通る。**`_containment`と最大件数overflowの再適用は実質不要**(救済後の句はdisplay窓の中に収まり、順位・件数が変わらないため何もしない処理。DESIGN_01の「再適用」を訂正)。選定段で句を差し替える場合(2c)のみ、差替え句を選定gateの先頭(語数→重複→NG→CMU)から再適用する。

(c) **記録形式**(`kp_candidates.json`の候補に追加するフィールド案):

```json
"rescue": {"applied": true, "method": "mechanical_revert|mechanical_rederive|llm_shorten",
           "rule": "revert_to_surface|rederive_display_or_llm_token|...",
           "before": {"selection_phrase": "studied separately", "llm_key_phrase": "study separately",
                      "stage": "canonicalization", "reasons": ["Rule7 ..."]},
           "after":  {"used_form": "studied separately"},
           "recheck": {"validator": "PASS", "cmu": "PASS", "words": 2},
           "gloss": {"realigned": true, "status": "OK|gloss_hr_pending"},
           "scope": "S1"},
"flags": {"rescued": true},
"gates": {"canonicalization": "RESCUED_QA_NOT_REJUDGED"},
"auto_eligible": false
```

`dropped[]`には救済で候補化した場合も元の除外理由を残し`rescued_as`(candidate_id)を付ける(監査性)。LLMの`qa_*`欄は上書きしない(M4)。HR依頼書(`render_request_md` `er119_kp_human_review_01.py:1193-1213`)の「旗」列に `修正済み(元: studied separately / 原形化不可: 動詞+副詞)` と **「QA未再判定」** を出し(PASSとは表示しない)、元形はその行に常に見える。gloss再整合に失敗した場合は`gloss_hr_pending`をHR表に表示する。「Gateで除外された候補(参考)」節(`:1214-1218`)には「→候補Nへ救済」を追記。`candidates_sha256`は救済込みの文書全体に対して従来どおり固定される(既存の仕組みのまま)。

(d) **既存仕様との整合**
- 順位: 救済候補は`live`から外れないため元のLLM順位(call1の順/call2の`raw_rank`)の位置にそのまま戻る。`ai_rank`の付番(`er119_kp_candidates_01.py:308-310`)は無変更で、AIが順位を付け直さない。
- 重複排除・最大件数: 救済後の句は元の選定句と同じdisplay窓に収まるため、`_containment`とoverflowの再適用は実質不要(上記(b))。Redundancy QA(`:312-327`)は通常どおり適用される。実測: AI島の救済案は現行a2の5候補と包含/同一にならない。shortfallの定義(`:353`)は無変更。最大8・数合わせ禁止は維持。
- AUTO/NG: 救済候補は**`auto_eligible=False`(Human選択のみ)を既定**。理由(Opus(B)): QAとglossが救済前のkeyに対する判定で古いまま残るため、段階1では過剰な制約ではない。revertだけのitem(key==display)は実データ蓄積後にAUTO可へ緩める余地があるが、それはユーザー判断事項(OI-7)。NGは`match_ng`がselection_phraseとused_formの両方を見る既存の仕組み(`er119:288-293`)でNG復活禁止を担保する(救済で迂回できない)。
- **外側retryとF1累積除外(M5で訂正)**: 救済に成功した句は`gate_dropped`から消えるため(`er119:329`)、そのままでは「AUTO可<3 かつGate除外あり」のretryが発動しなくなり、AUTO可を3件以上に届かせる再挑戦の機会が減って承認済みM-7(c)の挙動が意味的に変わる(DESIGN_01の「緩めも厳しくもしない」は事実と違っていた)。DESIGN_02では、retryのトリガー判定上は救済句を`gate_dropped`相当として数え(現行挙動を維持)、累積除外リスト(DECISION_LOG.md:87)には入れない。救済に失敗した句は現行どおりdropped+累積。除外リストにある句は選定gate(LLM前)で落ちるため救済は試みない。現行と異なる挙動を採る場合はOI-1で「挙動変更」として明示する。実装時はR4(3)の「救済あり/なしで外側retry発動回数が同一」testで固定する。
- OPUS R-1「vocabのshortfall受容・数合わせretryなし」(`OPUS_REVIEW_01.md:54`、前案件のOpus台帳行はGrepで特定できず=未確認): 救済は補充ではないので矛盾しない。
- **観測の追加(R3)**: 外側retryによる候補一覧の置換で消えた句、およびcall1選定のretryで消えた句を、`dropped`とinventoryへ記録する(観測のみ。救済はしない。EXCLUSION_PATTERNS_01 §4経路2・4)。

(e) **X/Y/Z共通核での位置**: `er119_kp_candidates_01.py generate_candidates`が呼ぶ`sc.run_key_phrase_canonicalization`内の`run_canonicalization_gate(postprocess=)`(`fulltext_p2`のときのみ設定、`er003_v1_n3_01_scaffold_generate.py:502-507`)。X・Y・Zは同じ経路で、差はZ限定のSRC D1・人称整合(救済後のitemにも既存どおり適用)のみ。rolesの後に置く順序は妥当(Opus論点5(i))。A/B/C旧経路は`_is_ft=False`のため無影響(`scaffold:502-505`、27-7)。Yの正式経路が未存在でも共通moduleとしては問題ない。**ただしhookが`is_fulltext`だけで有効になる点はHRを経ない経路に副作用を及ぼすため、(2)のM2の明示引数方式で限定する**。

## 3. 制作速度への影響

決定論部分はミリ秒。待ち時間を足すのはgloss再整合の追加call(救済成立時1 call。実測の所要は未確認、canonicalization 1 callは約27秒=AI島raw_usage_log scaffold行のelapsed_secondsなので同程度と推定)。一方、現行の「INVALID→item除外→canonicalization LLM再実行(1 callあたり約27秒)」を避けられる場合は相殺される。外側retryが発動したのはHR導入前の`fulltext_p2` outer_retry_log 78件中25(32%、tell-tale heart等の再実行を含み過大評価)、HR導入後は13 level-run中0。段階2cのみ該当句で+1 call(10〜30秒)。

## 4. 品質リスクと歯止め

| リスク | 歯止め |
|---|---|
| 表層形(非原形)の候補が増える | `rescue.method`と旗で明示、`auto_eligible=False`、HRがユーザー判断 |
| 再導出で意味が変わる・LLM未提案の誤形が採用される(`hoped for`→`hop for`等) | M1: {display側の語, LLMがその位置に出した語}のみ。新語形を生成しない。迷えばrevert。R4(1) testで固定 |
| 古いglossが救済後のkeyに付いたまま(`hold out one's hands`の訳が`held out`に残る) | M3: 救済rankのgloss再整合を強制、失敗は`gloss_hr_pending` |
| QAがPASS表示でユーザーを誤らせる | M4: `RESCUED_QA_NOT_REJUDGED`、HR表は「QA未再判定」 |
| HRを経ない経路に救済が漏れる | M2: 明示引数・既定OFF、バイト同一test(R4(2)) |
| 外側retryの挙動が意味的に変わる | M5: トリガー判定では救済句を`gate_dropped`相当として数える。R4(3) test |
| 所有格のrole(self/other_person)を無視した人称一般化 | 再導出は`postprocess_possessor_roles`の後。rolesがUNVERIFIED/NO_WINDOWなら一般形をdisplay側へ戻す(M6) |
| 本文対応の喪失 | revert・M1再導出はdisplay窓内のみ。選定段の短縮(2c)は元句の連続部分列に限る |
| 意味反転(`too soon to wave…`→`soon to wave…`) | 機械の左削り・右削りは行わない。2cは保留。採用時は否定・程度語削除を決定論で禁止+元の文を併記(R2)+`auto_eligible=False` |
| 救済でGate基準が実質緩む | 段階1は「受理面を広げない」: 受理されるのは「validator通過」かつ「LLM提案/displayの部分集合」で現行より狭い(Opus(A))。受理面を広げる項目は段階2で個別にユーザー承認 |

## 5. 追加コスト(70円/記事セット目標に対して)

単価の出典: `er009_n1_routing_governance_10_actual_model_cost.py:30`(gpt-6-luna 入力0.10/キャッシュ0.01/出力0.50 USD per 1M token)、`:21`(1USD=160円)、AI島`raw_usage_log.jsonl`実測3行(gloss再整合0.563円・同0.526円・part2_cand 0.322円)。

| 案 | 追加LLM call | 追加コスト/記事セット(2レベル) | 備考 |
|---|---|---|---|
| 段階1(revert+M1再導出+gloss再整合) | 救済1件につきgloss再整合1 call | **約+0.5〜0.6円/救済件**(出典: a2実測0.526〜0.563円)。救済で現行の再実行(canonicalization 1回分、約0.3〜0.6円)を避けられる場合は相殺され差し引き約0〜+0.3円/件 | 70円目標への影響は無視できる(<1%)。DESIGN_01の「0円・節約」は訂正 |
| 段階2a/2b/2e(表・検査の拡張) | 救済時にgloss再整合(同上) | 判定が変わるのは0円、救済件のgloss再整合は同上 | |
| 段階2c(AI短縮提案) | 該当句ごとに1 call+通過句のcanonicalization/gloss | 発生率8%(HR導入後13 level-runで1件)として期待値約+0.03〜0.05円/レベル、発生時約+0.8〜1.7円 | 保留推奨 |
| AI島a2の今回分を救済して再発行する場合 | gloss再整合 1 call | 約0.5〜0.6円(a2のみ) | §9 |

費用承認区分: 本設計はJPY0。実装後の運用増は0〜1.7円/発生時で、7-7の案件300円閾値には遠い。

## 6. 推奨する必要十分な実装案(段階化。ユーザーが段階ごとに採否を決められる)

| 段階 | 内容 | 受理面 | 11-8分類 | 実装規模 | 推奨 |
|---|---|---|---|---|---|
| **1** | 救済点A: `postprocess_lemma_repair`(M1制限付き再導出→revert)+`rescue`記録+HR表の旗(「修正済み」「QA未再判定」「gloss_hr_pending」)+`auto_eligible=False`+救済rankのgloss再整合強制+er119経路限定の明示引数(既定OFF) | **広げない**(Opus(A)) | **範囲外=ユーザー判断**(新しい後処理工程・HR候補集合の意味的変更。同型の先例UDR #173②もユーザー承認を経ている) | `er105`に1関数+`er119_kp_candidates_01.py`の旗付け/明示引数+`render_request_md`の旗3種 | **採用推奨** |
| 2a | guard限定詞に`no`/`each`/`every`/`all`/`both`/`another`等を追加(`accepts no responsibility`等) | 広がる(閉表網羅の是正の側面もあり、Fableが範囲内/拡大を判定) | 範囲内の可能性/拡大 | 表1行 | 判断(影響小) |
| 2a' | 過去形専用表の補完(`rang`等) | 広がる | 同上 | 表数行 | 判断(影響小) |
| 2b | guardに副詞追加(`studied separately→study separately`) | 広がる(`er105:575`の設計意図との関係を整理要) | 拡大(ユーザー承認) | guard関数1行+副詞判定 | 判断 |
| 2c | 6語以上のAI短縮提案(新Prompt/新1 call)。採用時はR2の条件必須 | 広がる(新Prompt=Opus条件A) | 拡大 | 中 | **保留**(発生率低・意味反転リスク) |
| 2d | スロット一般化(`wave a flag`→`do`) | Rule7原則の変更 | 拡大 | - | **非推奨**(本文に無い語を生成) |
| 2e | lexical `have`を有限助動詞から区別(`have a say`・`had our eye on`) | 広がる | 拡大 | 検査関数の精緻化 | 判断(HR導入後14中2件=X1・Y1) |

段階1だけで、HR導入後のGate除外の36%(4/11)を残せる見込み(M1の制限後の実数はoffline再生検証で確認。未確認)。段階2は個別に効果が小さい(各1〜2件)ため、**ユーザーが「原形で見たい」を重視するなら2b、`have`系を重視するなら2eを選ぶ**、という選び方を推奨する。

## 7. 検証計画(実装する場合)

DefaultOffIsolation型testは「受理面を広げない」ことと既定OFFの確認に使う: (1)既存の除外全件(`inventory_01.json`)に対し、修正後keyが最終Gateと同一引数のvalidatorで通ること (2)救済OFF(既定)の入力で出力がバイト同一 (3)A/B/Cが無影響 (4)NG/累積除外/重複/overflowとの結合test。**R4の必須test3件**: (1) 実在語だが誤った基本形(`hoped`→`hop`)を採用しないこと (2) HRを経ない経路(`scaffold:883-888`、`er062:1364-1373`)が分離され、救済ONでも出力がバイト同一 (3) 救済あり/なしで外側retryの発動回数が同一。runtime evidenceは既存記事の保存済みparsed応答を使うofflineで可能(新規有料run不要)。

**進め方(Opus(A)の記録と本案件での扱い)**: Opusは「保存済みparsed応答を使ったoffline DEV実装と再生検証はFable判断で先に進めてよい。Production配線はユーザー承認(OI-1)を得てから、または承認済みの限定例外(既定OFFのflag)の範囲内で行う」との意見。ただしユーザー原文は「今回は調査・設計のみ承認」のため、**本案件では実装しない**(ユーザー判断後)。Opus条件A(新しい処理フロー)のレビューは本案件で実施済み(OPUS_REVIEW_01)。実装後・Production採用提案前には条件C(重要変更のProduction採用提案前)に該当し得る(別途判断)。

## 8. 11-8判定(修正範囲の線引き)

- 救済フロー全体=**範囲外**(新方式、ユーザー判断)。Opus(A)も同判定。
- guard次トークン条件のCURRENT_SPEC記録漏れ=**範囲内の文書是正**(OPEN-530。本委任では起票のみ。CURRENT_SPECは本委任では編集しない)。
- guard限定詞語彙(2a)・過去形専用表(2a')の網羅漏れ=Fable判定(範囲内是正か拡大か)。

## 9. AI島 run_ai_01 のHR候補へ救済分を追加する場合(今回は実施しない)

HR状態はa2/b1bともPENDING_REVIEW・round 1・選択なし。救済を加えるとa2の`candidates_sha256`(`b030652528b0…`)が変わり、`kp_human_review.json`・`kp_human_review_request.md`の再発行が必要。既存CLI(`status/show/select/reselect/ng/…`、`er119_kp_human_review_cli_01.py:64-121`)に再発行コマンドは無く、`reselect`は選び直し(round+1・NG付き)用。追加するなら(1)段階1の採否→(2)実装→(3)再発行手順の新設(sha再固定・`--accept-ai`のsha一致・round扱いの確認)が必要で、**現時点では候補は未確定のまま保全**している。a2に追加できる救済は`studied separately`(表層形)の1件のみ(b1bは除外0)。**gloss再整合1 call(約0.5〜0.6円、M3)が必須**(revertのためLLMのgloss(`study separately`向け)をそのまま使えない)。

## 10. 残るOpen Item

| # | 内容 | 分類 |
|---|---|---|
| OI-1 | 救済方式(段階1)の採否。外側retryトリガーはDESIGN_02では現行維持(M5)。変える場合は挙動変更としてここで諮る | ユーザー判断要(新方式、11-8範囲外) |
| OI-2 | guardの記録漏れ(CURRENT_SPEC.md:1997に次トークン条件・閉表を追記)=OPEN-530 | 修正へ進む(範囲内・文書是正。次委任案: CURRENT_SPEC追記のみ、API 0) |
| OI-3 | guard限定詞の網羅(2a)・過去形専用表(2a') | Fable判定(範囲内是正/拡大) |
| OI-4 | 2b/2c/2e各項目の採否 | ユーザー判断要 |
| OI-5 | AI島a2への救済追加の要否と再発行手順(gloss再整合約0.5〜0.6円) | ユーザー判断要+実装確認 |
| OI-6 | lexical `have`の扱い(現行は語形リストでhave/has/had/is/was等を一律拒否) | ユーザー判断要(2eに含む) |
| OI-7 | revertだけのitem(key==display)のAUTO可への緩和(実データ蓄積後) | ユーザー判断要(将来) |
| OI-8 | 棚卸し対象外経路(EXCLUSION_PATTERNS_01 §4)の観測追加(R3) | 段階1に含める(観測のみ・救済なし) |
