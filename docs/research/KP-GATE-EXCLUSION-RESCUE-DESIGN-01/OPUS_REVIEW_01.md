# OPUS_REVIEW_01(条件A、2026-10-26、read-only、JPY0。以下Opus所見の逐語)

## KP-GATE-EXCLUSION-RESCUE-DESIGN-01 Opus独立技術レビュー(条件A、read-only、JPY0)

### 前提
- 新しい処理フローを共通核へ入れる設計なので、条件Aに該当すると判断した。
- 段階1の骨格(revert(表層形へ戻す)と、validator(機械的な検査関数)の再適用)は妥当。
- ただし、救済された候補が「HRを経ない経路」へ漏れる点と、glossとQAが古いまま残る点に穴がある。この2点は実装前に必ず塞ぐ必要がある(M2〜M4)。

### 論点別の所見

**論点1 本文対応: 段階1は問題なし。2cはユーザー判断要(保留に賛成)**
- (b) revertは本文対応を保つ。`er003_key_words_canonicalization.py:599` の「無変更=常に安全」の経路そのものなので、対応関係を失わない。
- (a) 再導出は、M1の制限を付ければ対応を保つ。
- (c) 2cについて。HR選択と`auto_eligible=False`は必要だが、それだけでは足りない。もし将来採用するなら、HR表に元の6語句と元の本文の文を必ず並べて出すこと、さらに否定・程度を表す語(`too/not/never/no/only/hardly`等)を削る部分列を決定論で禁止すること、の2点を追加する必要がある。今回は保留のままでよい。

**論点2 Rule7との整合: 要修正(M1、M6)**
- revertは受理面を広げない。設計意図の`er105:575`(V+名詞は基本形化せず表層形のまま)をむしろ忠実に実装する形になっている。現行実装は、LLMが基本形化を試みて失敗するとitemごと落としており、ここが意図とずれている。
- 穴は再導出のほうにある。`DESIGN_01.md:22-23` は「許可表の1対1置換の全組合せ」を列挙するとしている。validator自体の受理面は変わらないが、validatorはLLMの意味判断の後ろに置く「安全枠」として作られている。全組合せを機械的に列挙すると、LLMが一度も提案していない形が採用され得る。
  - 例1: `hoped for`→`hop for`。`_verb_base_candidates`(`er105:637-643`)はstem(語幹)とstem+eの両方を作る。どちらもCMU辞書の実在語なので、CMUでは区別できない。
  - 例2: `takes notes`→`takes note`。`er105:689` の句末の単数化は、guardなしで通る。
  - 「LLM案に最も近い案を採用」はLLM案と位置がそろわない場合に機能せず、同点時の規則もない。
- `role_ok_poss`について。救済処理の中の判定で空集合を渡すと、受理が広がるのではなく狭まる。ただし最終validator(`er003:697`、`_role_ok_poss_of(item)`)と判定がずれると、「救済したのにINVALID」が起きる(M6)。
- `_token_pair_ok`のguardはkey側の次トークンを見ている(`er105:664`)。そのため、LLMが提案していない人称置換(例: `him`→`someone`)を再導出が自分で作ると、それがguardを通してしまう経路がある。これもM1で塞がる。

**論点3 重複・順位・NG: 要修正(M5)**
- 順位の扱いは正しい。救済されたitemは`live`から外れないので、`ai_rank`(`er119_kp_candidates_01.py:309`)は自然に元の位置になる。
- NGは、`match_ng`がselection_phraseとused_formの両方を見る既存の仕組み(`er119:288-293`)で足りる。
- `_containment`の再適用とoverflowの再適用は実質不要(何もしない処理)。救済後の句がdisplayの窓の中に収まるため。記述を「不要」に直すのが正確。
- 問題は`DESIGN_01.md:67`の「外側retryの条件を緩めも厳しくもしない」という記述。これは事実と違う。
  - 救済に成功した句は`gate_dropped`から消える(`er119:329`)。
  - そのため「AUTO可<3」のときにretryが発動しなくなる。AUTO可を3件以上に届かせるための再挑戦の機会が減り、承認済みM-7(c)の挙動が意味的に変わる。

**論点4 LLMの範囲: 要修正(M3、M4)**
- 新Promptが必要なのは2cだけ、という判断は正しい。
- ただし「段階1はLLM 0」とは言い切れない。gloss再整合は「最終KPに表示候補にない語が含まれる場合だけ」動く(`er003_v1_n3_01_scaffold_generate.py:523`)。
  - revertの場合は対象が0件になるので、LLMが自分のkey向けに作ったglossがそのまま残る。例: `hold out one's hands`の「両手を差し出す」が、`hold out`/`held out`に付いたまま残る。
  - 設計書§7の「a2はgloss 1 call」という記述とも矛盾している。
- QAについて。`qa_meaning_or_usage_unchanged`などは、救済前のkeyに対する判定である。
  - `auto_eligible=False`があればAUTO採用は防げる。しかしHR表にPASSと表示されると、ユーザーを誤らせる。
  - roles処理の先例(`er105:988`)のようにQAをPASSへ上書きする処理は、救済には入れないこと。

**論点5 X/Y/Z共通核: 要修正(M2)**
- (i) rolesの後に置く順序は妥当。
- (ii) A/B/Cは`is_fulltext`が偽なので無影響(`scaffold:502-505`)。
- (iii) Z限定のSRC D1/人称整合は、救済後のitemにも通常どおり適用される(`er119:271-282`)。
- (iv) Yの正式経路が未存在でも、共通moduleとしては問題ない。
- 重大な副作用がある。このhookは`is_fulltext`だけで有効になる。そのため、HRを経ない経路にも効いてしまう。
  - 該当経路: `run_key_phrases`→`run_kp_with_outer_retry`(`scaffold:729,883-888`)、およびZの`run_kp_with_outer_retry_fulltext`(`er062_family_z_writer_01.py:1364-1373`)。
  - これらの経路では、救済された表層形KPが旗もHRもないまま`keywords_canonicalized.json`に確定する。

**論点6 見落とし・過剰制約: 推奨(R1〜R4)**
- `lexical have`を2eに回したこと、救済候補を一律AUTO不可にしたことは、いずれも過剰な制約ではない。

### (A)〜(D)

**(A) 段階1を「受理面を広げない」と呼んでよいか**
- revertと、M1で制限した再導出に限れば、そう呼んでよい。受理されるのは「validator通過」かつ「LLM提案の部分集合」なので、現行より狭い。
- ただし11-8では範囲外と判定する。新しい後処理工程であり、Productionの出力(HR候補の集合、表示)を意味的に変えるため。同型の先例もユーザー承認(UDR #173②)を経ている。
- 進め方の意見:
  - 保存済みparsed応答を使ったoffline DEV実装と再生検証は、Fable判断で先に進めてよい。
  - Production配線はユーザー承認(OI-1)を得てから。または承認済みの限定例外(既定OFFのflag)の範囲内で行う。

**(B) `auto_eligible=False`既定は過剰制約か**
- 段階1では過剰ではない。QAとglossが古いまま残る以上、妥当な既定値。
- revertだけのitem(key==display)については、実データが蓄積した後にAUTO可へ緩める余地がある。ただしそれはユーザー判断事項。

**(C) 見落としているGate除外経路**
1. `cmu_post_canon`による除外(`er119:264-266`)。救済はvalidateの前に置かれるので、ここで落ちる句は救済されない。displayへrevertすれば救える可能性がある(revert後にCMUの再検査は必須)。
2. 外側retry発動時の「候補一覧ごとの置き換え」(`er119:334-341`、`dropped_all=[]`)。Gateを通過済みの良い候補まで捨てる、最大の破棄経路。棚卸しの対象外になっている。
3. canonicalization段の非Rule7の構造違反。具体的には、OF-X1(左端条件)違反(`er003:600-605`)、canon段で語数>5、LLMが有限助動詞を混入させたケース。revertで救えるのに、トリガーが「Rule7(基本形化)」に限定されている。
4. call1の選定段のgate失敗(`sc.run_key_phrase_selection`内のretry)。句は記録されずに消える。

**(D) M(必須修正)/R(推奨)一覧**
- M1: 再導出は「display窓の中で、各tokenを{display側の語, LLMがその位置に出した語}のどちらかから選ぶ」だけに限定する。`_verb_base_candidates`や単数化表から新しい語形を生成しない。同点時は決定論で決め、迷う場合はrevertを優先する。source_spanへの拡張は再導出の対象にしない。
- M2: 救済の有効化をer119の`generate_candidates`経路だけに限定する(canon_fnへ明示引数を渡す方式で、既定OFF)。HRを経ない経路(`scaffold:883-888`、`er062:1364-1373`)では出力がバイト同一であることをtestで固定する。あるいは、それらの経路がProductionで使われていないことを証拠で示す。
- M3: 救済したrankについてはgloss再整合を強制する(`align_glosses(only_ranks=)`)。再整合できなければ`gloss_hr_pending`の旗を付ける。費用はa2実績の約0.5円/件。「LLM 0」の記述を訂正する。
- M4: LLMのqa_*欄は上書きしない。`gates.canonicalization="RESCUED_QA_NOT_REJUDGED"`を付け、HR表では「QA未再判定」と表示する(PASSとは表示しない)。
- M5: 外側retryの条件を現行と同一に保つ。救済された句はretryのトリガー判定上は「gate_dropped相当」として数え、累積除外リストには入れない。現行と異なる挙動を採るなら、OI-1で「挙動変更」として明示してユーザーに諮る。
- M6: 救済処理の中のvalidator呼出は、最終Gateと完全に同じ引数で行う。具体的には`canonicalization_view_items`のspan、`original_span`、`allow_inflection_normalization=_is_ft`、`role_ok_poss=_role_ok_poss_of(item)`。rolesがUNVERIFIED/NO_WINDOWの場合は、一般形の所有格tokenをdisplay側の語へ戻す。元の除外理由は`rescue.before.reasons`に保存する。
- R1: トリガーを「LLMのkeyが原因の構造違反全般」と「cmu_post_canon」に広げる。救済手段はrevertのみとする(受理面は不変)。
- R2: 2cを将来採用する場合は、否定・程度語の削除を決定論で禁止し、HR表に元の句と本文の文を併記することを条件にする。
- R3: 外側retryによる候補一覧の置き換え、およびcall1選定のretryで消えた句を、`dropped`とinventoryへ記録する(観測のみ。救済はしない)。
- R4: 検証にtestを3つ追加する。(1) 実在語だが誤った基本形(`hoped`→`hop`)を採用しないこと、(2) HRを経ない経路が分離されていること、(3) 救済ありとなしで外側retryの発動回数が同一であること。

### 参照ファイル
- `C:\Users\tensh\eigo-radio\docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\DESIGN_01.md`(:22-23、:67)
- `C:\Users\tensh\eigo-radio\er105_kp_fulltext_selector_01.py`(:575、:637-643、:664、:689、:976-978、:988)
- `C:\Users\tensh\eigo-radio\er119_kp_candidates_01.py`(:264-266、:288-305、:329-341)
- `C:\Users\tensh\eigo-radio\er003_v1_n3_01_scaffold_generate.py`(:502-507、:523、:729、:883-888)
- `C:\Users\tensh\eigo-radio\er062_family_z_writer_01.py`(:1364-1373)
- `C:\Users\tensh\eigo-radio\er003_key_words_canonicalization.py`(:599-620、:697)

### 要約
revertは承認済みの設計意図(`er105:575`)に沿っており、受理面を広げない。
ただし再導出の全組合せ列挙は、LLMが提案していない誤った基本形を生む。LLM提案の部分集合に制限する必要がある(M1)。
救済のhookはHRを経ない経路にも効いてしまう(M2)。glossとQAは救済前のkeyのまま残る(M3、M4)。外側retryの条件は実際には変わる(M5)。
受理面は不変だが、新しい処理方式のため11-8では範囲外と判定する。offline DEV検証はFable判断で進め、Production配線はユーザー承認後にする。
2cの保留と、救済候補を既定でAUTO不可とすることには賛成する。
