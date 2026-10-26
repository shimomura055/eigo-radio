# DESIGN_02: Gate除外候補の補完(Production)設計 改訂版(Opus条件A M-1〜M-7/R-1〜R-10反映、KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_02、2026-10-26)

Status=IMPLEMENTED(test PASS、runtime evidenceは委任_03)。DESIGN_01(`DESIGN_01.md`)との差分のみを書く。差分の無い節(§1 slot抽象、§2 除外の定義表、§5 重複防止の多層、§7 HR/resume/再生成、§10 費用)はDESIGN_01のまま有効。Opus逐語=`OPUS_REVIEW_01.md`。

## 0. 訂正(M-2: 事実誤りの是正)
- DESIGN_01 §9・`CURRENT_FLOW_01.md` §3は「`CURRENT_SPEC.md`にM-7cの記載0件」としたが**誤り**。外側retry条件は`CURRENT_SPEC.md:2021`(KP救済方式、APPROVED_FOR_PRODUCTIONの節)に「外側retry=`n_auto<3 and (gate_dropped or 救済済みauto不可あり)`(Opus M3)」と明記されている。一方、救済のユーザー原文(`delegation_log/…RESCUE…_USER.md`)にretry条件の指定は無い。
- したがって本変更は「承認文の無い実装規則の是正(11-8の不具合)」ではなく、**「承認済みの節に記載された実装規則を、より新しい明示承認(補完仕様§3-1『初回に合格した候補は保持し、再生成・入れ替えをしない』)に合わせて変える挙動変更」**である。Fableがユーザーへ区別報告する事項(本実装はflag `EIGO_KP_BACKFILL=0`で外側retry条件ごと現行へ完全復帰できる)。
- 11-8分類: 補完機構=範囲内(承認済み仕様の実装)、外側retry脚の撤去=範囲内だが挙動変更として区別報告、K1=範囲外(承認済み仕様の変更→ユーザー判断)。

## 1. M-1〜M-7(必須)の反映
| ID | 反映内容 | 実装箇所 |
|---|---|---|
| M-1 | call1(Prompt 2)の最終attemptでitem単位に除外された句(`cmu_excluded`/`exclusion_dropped`)は戻り値に出ない(er105:575-578)。er105を変えず、work dirの`keywords_runtime_metadata.json`の`attempts_detail[-1]`を読んでEへ数える。前周のmetadataを読み違えないよう、call1呼出前にそのfileを削除(select呼出が必ず書き直す作業dir内成果物)。dropped行は`origin=call1`、stage=`cmu`/`excluded`(除外指定のsource)。 | `er119_kp_backfill_01.py` `read_call1_dropped`/`clear_call1_metadata`、`er119_kp_candidates_01._generate_candidates_impl` |
| M-2 | 上記§0。CURRENT_SPEC:2021の更新案は`RESULT_PACKET_KBF2.md`(8)。 | 文書 |
| M-3 | backfill ON(既定)では`gate_dropped`脚と`rescued_not_auto`脚の**両方**を撤去。残すのは候補0件(`not cands`)と技術失敗(call1/call2失敗・live 0・canonicalization全体失敗)のretry。OFFでは現行条件`n_auto<3 and (gate_dropped or rescued_not_auto) and not last`のまま。 | `_generate_candidates_impl`の外側retry判定 |
| M-4 | 補完のAPI呼出の前に`stop_check_fn("kp_backfill:<aid>:round<n>:attempt<k>")`を呼ぶ(try外=STOPは伝播)。未発動(E=0等)では呼ばない。 | `_run_backfill` |
| M-5 | `run_vocab_selection`に`shown_phrases`(LLMに見せる『すでに選ばれた表現』)と`note`を追加。duplicate_of_top3の比較先は常に`already_items`(call1の選定結果)のまま=Gateの意味を変えない。補完では`shown_phrases`=現存候補の選定句+救済前元句、`already_items`=call1の3件。分離をtestで固定。 | `run_vocab_selection`、`TestVocabSelectionInputs` |
| M-6 | `_gate_chain`は外側ループの制御(continue/return)を持たずstatus(`OK`/`CANON_FAILED`)を返す。補完側の失敗(call失敗・live 0・canonicalization全体失敗・技術例外)は`backfill.status=FAILED`+`failure`コードとして**初回候補で続行**(外側retryを起動しない)。 | `_gate_chain`、`_run_backfill` |
| M-7 | `run_vocab_selection`(er119内)の引数追加をここに明記(`shown_phrases`/`note`、既定は従来と同一)。2-V本文のsha・`prompt_prefix_intact`・Prompt 2 shaをtestで固定。既存`ft.build_exclusion_note`を本文後置noteとして添える(新文言なし・件数文言なし)。 | 同上 |

## 2. R-1〜R-10の採否
- R-1 採用: 候補・除外の`kind`(`word_count==1`=単語)。E_phrase/E_wordを分けて数え、補完は2-V応答のGate通過候補から**種類別に先頭E_phrase件・E_word件**を採る(種類をまたぐ数合わせはしない=単語が除外されフレーズで補う事象を避ける。不足は不足のまま)。N = min(E, 上限8-現存, 2-Vの最大5)。
- R-2 採用: 補完応答の最大5件すべてにGate全段(canonicalization・CMU post-canon・記号・人称整合[Z]・SRC D1[Z])を通してから、種類別の先頭N件を採る(canonicalizationが少し増える代わりに充足率が上がる)。
- R-3 採用: 基本形化後の`used_form`が既存候補(または先に採った補完候補)と完全一致、またはcandidate_idが衝突したら捨てる(stage=`backfill_duplicate`、Nに数えない・再callしない)。選定段では現存候補・救済前元句・除外句・Human NGとのphrase_key完全一致を機械除外。
- R-4 採用: Eはphrase_keyで重複除去してから数える。
- R-5 採用: Z人称整合の補完用dirを分離。Zのrunner(er026)は`person_fn`の中で毎回`make_person_repair_fn(...)(merged)`を呼ぶ形でrunner側を変えられないため、`er119_kp_candidates_01._person_repair_subdir`(contextvar、既定None=従来dir)を`make_person_repair_fn`が実行時に読み、`_run_backfill`が補完のGate連鎖の間だけ`backfill`をセット(finallyで必ず復元)。補完は`<base>/gloss_person_repair_backfill`へ書き、初回の`gloss_person_repair`を上書きしない。canonicalizationの作業dirも`work/backfill_1/`(初回の`keywords_canonicalized.json`を上書きしない)。
- R-6 採用: `_gate_chain`抽出を単独commit(`cbcd29d27`)にし、抽出前(HEAD)のコードで13 scenarioの候補docをgolden固定、抽出後・OFF・E=0で完全一致を確認してから機能追加。flagは生成1回につき1回だけ読みdocへ記録。
- R-7 該当せず: `rescued_not_auto`脚は撤去(M-3)したため「retry判定を補完より先に行う」問題は生じない。
- R-8 採用: 補完側は技術失敗(通信/parse/canonicalization等の一般例外)だけを捕捉。`FulltextSelectionError`(routing違反等)・STOP系(`FamilyZStopSentinel`等)・KeyboardInterrupt/SystemExitは握らず伝播。
- R-9 evidence計画へ(委任_03): freshで自然に補完が発動しなかったFamilyはfreshを追加(1回約¥2)。観測=call1最終attempt除外の計数・補完候補のHR依頼書/フォームJSON表示・Z SRC D1/人称整合・AUTOでn_auto<3(または0)の挙動・`rescued_not_auto`の扱い。
- R-10 採用: 配線位置=ai_rank付番の直後・Redundancy QAの前(DESIGN_01の『:346-349の間』は『QAの後』と食い違っていたため訂正)。補完候補のai_rankは連番継続、Redundancy QAは補完込みの候補全体に1回。

## 3. K0/K1
K0採用(call1のattempt内再選定は不変=CURRENT_SPEC:2010/2016の承認済み記載)。K1(call1もitem単位除外+補完へ)は承認済み仕様の変更でありer003/er105に波及するためユーザー判断(OPEN候補、`RESULT_PACKET_KBF2.md`(7)(8))。M-1によりK0でもcall1最終attemptの除外はEに数える。

## 4. 発動条件(確定)
`backfill_enabled() and E_total>=1 and 現存候補>=1 and 上限8-現存>=1`。E=0は不発動(LLM 0)。初回返答が上限未満でも、除外が無ければ不発動(AI島Adv型)。除外があるときも補完はE件分だけ(返答が5件に満たない分や上限8までの差は補完しない)。human_ng/excluded(AIが再び選んだNG句)はEに数え、別カウンタ(`E.human_ng`/`E.excluded`)にも出す。

## 5. データ契約
`DATA_CONTRACT_01.md`(F-2)。候補に`kind`、docに`backfill`・`shortfall_detail`を追記(既存項目は無変更。golden比較は追記項目を除いて完全一致)。

## 6. 非変更の確認
Prompt 2/2-V本文・sha、`er105`/`er003`/`er125`、正規表現・辞書・閾値、A/B/C。補完moduleはA/B/C非import(静的test)。
