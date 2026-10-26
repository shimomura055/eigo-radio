# DESIGN_01: Gate除外候補の補完機構(Production)設計(KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01、2026-10-26)

Status=DESIGN_READY(Opus条件Aレビュー待ち。コード未変更・API 0)。根拠=ユーザー正式採用(APPROVED_FOR_PRODUCTION)原文§3-1〜3-3(委任文逐語引用)。現行事実=`CURRENT_FLOW_01.md`。

## 0. 要約(設計の核)
1. 補完は「**AIが選定した候補が、後続Gateで最終的に除外された件数E**」が1以上のときだけ、**1回だけ**、最大E件を追加探索する。E=0(初回が上限未満でも)は不発動・API 0。
2. 初回に正式候補として残ったもの(救済済み・HR限定・auto不可を含む)は**一切触らない**。補完候補は末尾に追加し、同一Gate(救済含む)を通す。
3. 補完のLLM callは**既存Prompt 2-V(sha固定・本文無変更)**を再利用(第一候補)。新Prompt本文は作らない。件数Nは「Gate通過後に先頭N件を採る」ローカル処理で実現(Prompt側に件数文言を足さない)。
4. 現行の外側retryのうち「Gate除外+n_auto<3で全件置換」の脚は、原文§3-1と矛盾するため**補完へ置換**(技術失敗retryは存続)。call1のattempt内全件再選定も同様に是正(§9 K1、Opus論点)。
5. 単一flag読取関数(既定ON=承認済み仕様)・X/Y/Z共通の1配線点・A/B/C不変。

## 1. 抽象: slot(候補枠)
補完は「枠(slot)」単位で定義する。slot={name, cap, first_pass(初回選定のitem群), prompt_fn(補完call), containment_refs}。
- **現行Production経路**: slot 1つ `pool`(cap=`KP_CANDIDATE_MAX`=8、first_pass=call1[3]+call2[最大5])。call1/call2の差は`origin`で保持。単語とフレーズは同一プール(現行Productionに単語専用選定は無い。Adv単語解説は`auto_select`が同プールから先頭5を取る、`er119_kp_human_review_01.py:552`)。
- **将来7+5経路(採用された場合)**: slot 2つ `phrase`(cap=7)と`word`(cap=5)。除外カウントも補完もslot単位で独立に行い、**補完callはそのslotの初回選定Prompt本体をそのまま再利用**する(`prompt_fn`が初回と同じPrompt本体を返す)。これにより単語slotの優先順位(1本文一致 2一語 3上級者向け価値 4易語除外 5単語単体価値[必須にしない])は**初回Promptの順序がそのまま補完にも適用**され、補完側で優先順位を再記述しない=条件5の必須化・順位逆転(Trial-01の再発、`PROMPT_DIFF_01.md §1-2`)が構造的に起きない。
- 上限はslotの引数(7+5固定をコードに埋めない)。補完件数 N = min(E_slot, cap - 現存候補数)。
- `containment_refs`(duplicate_of_top3の比較先)はslot引数。現行pool=call1の3件(現行どおり)、将来word slot=フレーズslotの採用句(Trial-02の経路と同じ)。**Gateは緩めない**(`PROMPT_DIFF_01.md §4`: 含有語除外は承認済みGateとして維持)。

## 2. 除外カウント(a)
E_slot = 「AIが選定(call1/call2/将来のslot初回call)した個別item」のうち、**候補組立後の最終処分が`dropped`でstageが下表の“数える”**ものの数。
| 最終処分 | stage | 数える? | 根拠 |
|---|---|---|---|
| 正式候補として残った(auto可) | - | 数えない | 除外ではない |
| 正式候補として残った(`qa_fail`/`gloss_hr_pending`/`similar_to_ng`でauto不可=HR限定) | - | **数えない** | 原文§3-2「Human Review限定候補…整合」。候補表に載る |
| 救済成立(auto可/不可とも。`flags.rescued=true`) | - | **数えない** | 原文§3-2「救済で残ったものを誤って除外と数えない」。救済はdropped前に成立(`DESIGN_03.md §1`) |
| 選定段のitem除外 | validate(語数・本文一致・有限助動詞・数値等のうち救済不成立) | 数える | Gate除外 |
| 〃 | duplicate_of_top3(call1との同一/包含) | **数える** | 現行Gate維持(Gate緩和しない。原文§3-3) |
| 〃 | cmu / cmu_post_canon / canonicalization(救済不成立) / symbol / src_d1[Z] | 数える | Gate除外 |
| 〃 | human_ng(AIが再び選んだHuman NG句)・excluded(累積除外句の再選定) | 数える(別カウンタで記録) | AIが一度選定->NGで除外。置換が必要。Opus論点P2 |
| 〃 | overflow(call2が最大5件を超えた下位) | 数えない | NGでなくprompt上限超過の切り捨て(現行も`gate_dropped`から除外、`er119:347`) |
| Redundancy QA | - | 数えない | 旗のみで除外しない(`:349-366`)。確定集合での除外はfinalize(M-8)の既存処理 |
- 実装は**候補組立後の`dropped`リストのstageの許可リスト**(定数`BACKFILL_COUNTED_STAGES`)で数える。救済候補は`dropped`に入らないので構造的に数えられない(加えて「`cands`に同一`candidate_id`/救済前元句がある項目はdroppedにあっても数えない」二重防御)。
- 初回返答が上限未満(例: call2が4件)は**E=0なら不発動**。AI島Adv(7件・除外0)=不発動。AI島Std(call2=4件返答+除外2)=E=2のみ補完し、「返答4件が最大5件に満たない1件分」と「上限8までの差」は補完しない(原文§3-1の例どおり)。

## 3. 発動条件
`backfill_enabled() and E_slot >= 1 and cands(現存候補)が1件以上`。E=0なら補完moduleを呼ばない(LLM 0、状態は`backfill: {triggered: false, E: 0}`をlogのみ)。call1/call2が**失敗**(技術失敗・live 0・canonicalization全体失敗)した周は補完でなく従来の外側retry(技術失敗)。

## 4. 補完call(b): 既存Prompt 2-Vの再利用(第一候補)
- 呼出: `p2v.build_user_message(text, already, diagnostic_note=<既存ft.build_exclusion_noteの出力>)`。**Prompt 2-V本文は無変更**(`prompt_prefix_intact`・`PROMPT_2V_SHA256_PINNED`維持)。
  - `already`(「選ばない」一覧) = 現存候補(auto可・HR限定・救済済みの`selection_phrase`と、救済済みの救済前元句)。LLMに重複を避けさせる。
  - `diagnostic_note` = 除外された句(Human NG・累積除外を含む)を**理由付き**で渡す既存関数`ft.build_exclusion_note(excluded)`(現行外側retryで使用中の既存文言)。**新しい文言は作らない**。注: 既存noteの括弧書き「無理に3件に揃えず」は呼出元(Prompt 2)の件数文脈。2-Vに添えても数合わせ禁止の趣旨は同じだが、Opus論点P3で確認。
  - 件数Nは**プロンプトに書かない**。LLMは2-V仕様どおり最大5件を学習価値順で返し、Gate通過後に**先頭N件**を採る(余りは`backfill_surplus`としてlog、候補にしない)。Nの上限は2-Vの最大5(N>5のときは5で打ち切り、`backfill_capped=true`とlog)。
- **新Prompt要否の判定**: 現行pool経路は**新Prompt不要**(2-V再利用+既存note)。ユーザー原文§4「新しい候補生成Promptが必要になった場合は区別して報告」の対象外。ただしevidenceで「2-Vがexcluded/already指示を無視して同じNG句や重複を多発する」「先頭N件がGate通過できない率が高い」場合は、件数1行を足した最小差分note(=新規のuser message末尾文言)が必要になり得る -> その時点で**区別報告**(委任_03のevidenceで判断。委任_02の実装は件数文言を持たない)。7+5のslotは各初回Prompt本体を再利用(同上の原則)。
- 技術/parse失敗の再試行は既存`run_vocab_selection`と同じ最大2回(`ft.MAX_ATTEMPTS`)のみ。**内容起因の再選定はしない**(見込みのない同一処理の反復を避ける、原文§3-2)。

## 5. 重複・同NG防止(c)
多層: (1)LLMに見せる: `already`(現存候補)+note(除外句と理由)。(2)返答の機械処理: 補完候補の`phrase_key`が (a)現存候補の`selection_phrase`・救済前元句 (b)除外された句 (c)Human NG(`ex_keys`、救済前元句のR6照合含む)のいずれかと**完全一致**したら**補完せず捨てる**(Nに数えない・置換のための再callなし)。(3)Gate: `duplicate_of_top3`は`containment_refs`との同一/包含で**現行Gateのまま**(現存候補全体への包含判定を新設してGateを厳しくしない)。意味的重複は既存Redundancy QAの旗(確定集合ではfinalizeのM-8)。(4)補完候補も後段で`match_ng`(used_form・救済前元句)を再照合。
- 「同じNGの繰り返し」: 除外理由を渡して再発を抑えるのは(1)のみ。再び同じ理由(例: 6語)で不合格ならそのまま不合格(補完は1回だけ。累積除外の更新や再補完はしない)。

## 6. Gate再適用と順序(d)
```
初回: call1(Prompt 2) -> call2(Prompt 2-V) -> select gate[救済H2込み] -> canonicalization[救済H3込み] -> CMU post-canon/記号/人称[Z]/SRC D1[Z] -> NG再照合 -> 候補組立+救済annot(H4)
  => cands_1, dropped_1
除外確定: E = count(dropped_1 の BACKFILL_COUNTED_STAGES、AI選定item)   [救済済み/HR限定は cands_1 に残っているため数えない]
E==0 -> 補完なし(API 0)
E>=1 -> 補完call(2-V再利用) -> 補完select gate[validate/重複/除外/CMU、救済H2込み。run_vocab_selection相当をalready=現存候補・containment_refs=現行のまま呼ぶ]
     -> 先頭N件 -> canonicalization[救済H3込み、補完item群だけを別work dir .../work/backfill_1/ で]
     -> CMU post-canon/記号/人称[Z]/SRC D1[Z] -> NG再照合 -> 候補組立+救済annot(H4)
     => cands_2(末尾へ追加、ai_rankは連番継続、origin="backfill")
最終: Redundancy QA(cands_1+cands_2を1回、旗のみ) -> doc永続化(backfillブロック: triggered/E/N/stage別内訳/prompt sha/model_id/補完の各dropped)
```
- 補完分のcanonicalizationは**別work dir・別call**(初回の`keywords_canonicalized.json`を上書きしない=M-1、初回候補の基本形化/glossを再生成しない=保持)。rankは補完item内で1..mのcanonicalization入力にし、後段で`ai_rank`を連番継続へ付替え(`idx_of`相当の対応を保持)。
- 補完候補が不合格でも**基準は緩めない**(救済は初回と同じ機構のみ)。補完後も上限未達ならそのまま許容(`shortfall`記録は現行どおり)。
- **救済との順序**: 救済は各Gate内(除外判定前)で成立する設計のため、E算定は救済後。救済済み候補は保持され`already`に入る(元句も)。
- 実装形: 現行`_generate_candidates_impl`のcanonicalization以降(`er119_kp_candidates_01.py:239-346`)を内部関数`_gate_chain(batch)`に抽出して初回・補完で再利用(挙動不変の純リファクタ。golden/回帰testで担保、委任_02)。

## 7. HR / Human NG / retry / fallback / resume / 再生成(e)
- **Human NG**: seed `excluded`(human_ng)を補完のnote/`ex_keys`に含む。補完候補にも選定段+canon後(used_form/救済前元句)の`match_ng`。NG句の復活は初回と同じ多層で阻止(`KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/DESIGN_01.md:89`の(1)〜(5)がそのまま効く)。
- **HR**: 補完候補は通常候補としてHR依頼書の候補表に載る(`render_request_md`は`origin`を使わない[Grep済み: `er119_kp_human_review_01.py:1223`はai_rank/used_form等のみ]、`ai_rank`連番)。`candidates_sha256`は補完込み文書全体のsha(不変性保証は従来機構)。HR限定候補・救済済み候補は保持。
- **retry**: 技術失敗の外側retryは存続。補完は外側retryの**1周ごとに最大1回**(外側retryが全件再生成する周では、その周の初回結果に対する補完)。補完call自体の技術失敗は`run_vocab_selection`の2回までで、全失敗なら`backfill.status=FAILED`を記録し**初回候補をそのまま採用**(外側retryも起動しない=初回合格の保持)。
- **fallback**: 補完の失敗は新たな停止を作らない(初回候補で続行)。Gate・基準のfallback追加なし。
- **resume**: 補完結果は`kp_candidates.json`に永続化され、`ensure_kp_review`は読み戻すだけ(`er119_kp_human_review_01.py:1284`)=補完の再課金0。補完は生成時(`generate_fn`呼出内)にのみ行う。
- **再生成**: `--regenerate-stage`/RESELECTION_REQUESTED/STALEでは**初回選定からやり直し**(新roundでround内に補完も新規1回)。確定済みHRは再抽選しない既存規則のまま。
- **kill switch**: 単一読取関数`backfill_enabled()`(新module内)。環境変数`EIGO_KP_BACKFILL`、**既定ON**(ユーザー正式採用の承認済み仕様。`EIGO_KP_RESCUE`/`EIGO_KP_GLOSS_ALIGNMENT`と同型)。`"0"`のときのみ補完無効かつ**外側retryは現行条件に完全復帰**(安全停止スイッチ)。起動script/.envで暗黙にON/OFFにしない。11-7限定例外は不要(承認済み機能)。

## 8. 配線点(f)
| # | 場所 | 内容 |
|---|---|---|
| B1 | `er119_kp_candidates_01._generate_candidates_impl`: 候補組立直後・Redundancy QAの前(:346-349の間) | `backfill_enabled()`なら新module(ファイル名はer番号衝突を避け委任_02で確定。er127はTTS並行Agent使用)の `plan_and_run_backfill(...)` を呼ぶ。引数=初回の`cands/dropped/originals/meta`・`already`材料・`ng_entries`・`excluded`・`_gate_chain`・`text/units/work/process`・テスト注入用`vocab_call_fn`/`canon_fn`。 |
| B2 | 同:355 外側retry条件 | `gate_dropped`の脚を撤去(補完へ置換)。`rescued_not_auto`脚と技術失敗continueは存続(§9 R1)。kill switch OFF時は現行条件。 |
| B3 | 同:371 doc | `backfill`ブロック追加。`outer_retry_log`の各周に`backfill`要約。 |
| B4 | `_gate_chain`抽出(§6) | 純リファクタ。 |
- X/Y/Zは同一`_generate_candidates_impl`を通るため**Family別の追加配線なし**(Yは`er121:562`、Zは`er026:1974`、Xは`er019:452`経由で自動適用)。Zの`src_fn`/`person_repair_fn`は`_gate_chain`内で補完候補にも適用。
- A/B/C: `er119`をimportしない(`er119_isolation_test_01.py`)。補完moduleもA/B/C非import(同test拡張)。A/B/C golden(1002件)バイト不変をtest。
- `er105`・`er003`・Prompt・正規表現・辞書・閾値は**無変更**(K1を採る場合の`er105`後方互換引数追加を除く)。

## 9. 外側retryとの関係(最重要)と11-8分類
事実: `CURRENT_FLOW_01.md §3`。外側retry(Gate除外+n_auto<3で全件置換)とcall1のattempt内全件再選定は、原文§3-1「初回合格候補は保持し再生成・入れ替えをしない」と運用上矛盾する。
| 案 | 内容 | Q | D | C | 判定 |
|---|---|---|---|---|---|
| R0 併存(現行維持+補完追加) | 除外->補完、その後n_auto<3なら全件置換 | 初回合格が入れ替わり原文違反 | - | retry+補完で二重課金 | 不採用 |
| **R1 条件変更(推奨)** | 外側retryから`gate_dropped`の脚を撤去し補完へ置換。技術失敗(call1/call2/live0/canon全体失敗)のretryと`rescued_not_auto`脚は存続 | 原文適合。n_auto<3のまま確定は`auto_select`の「不足は不足のまま」(`er119_kp_human_review_01.py:539`)と整合 | 同等 | 全件再生成が減り下がる方向 | **採用案** |
| R2 全撤去 | 外側retry自体を廃止 | 技術失敗の回復力が落ちる | - | - | 不採用 |
- **11-8分類**: 原文§3-1がユーザー正式採用の仕様であり、外側retry(M-7c)はFable/Opus設計でユーザー承認文を持たない(`CURRENT_SPEC.md`にM-7c記載0件)。したがってR1は「新仕様の追加」でなく**承認済み仕様(原文§3-1)との矛盾の是正=不具合(11-8)**で委任範囲内(分類B)。ただしProduction挙動の実質変更を伴うため、Opus条件Aレビューで確認し、Fableが受入時に「M-7c変更」をSSOTへ反映する。残る小論点(`rescued_not_auto`脚を残す是非)は分類C(原文§3スコープ外・OPEN候補)。
- **K1(call1のattempt内全件再選定)**: 現行`run_selection_gate`は不合格1件でも3件全体を再選定(`er105_kp_fulltext_selector_01.py:530`)。原文§3-1に厳密に従うなら、call1もitem単位除外->補完に統一すべき。
  - 案K0: call1の現行挙動は「初回選定の一部(attempt内の技術的再選定)」として存続し、補完は**初回選定フェーズ完了後**の除外から数える。
  - 案K1: `er105`へ後方互換のkeyword-only引数(既定False、HR候補生成だけがTrue)を足し、hard requirement不合格itemのみ除外して補完へ回す。
  - **推奨=K1を委任_02に含める**(原文への忠実性)。ただし`er105`はA/B/Cとの共有可能性があり影響が大きいため、**Opus論点P5**として是非を問う。K1がOpusで否決ならK0で実装し、差をOPEN化。分類B(承認範囲内。Gate基準そのものは不変)。

## 10. 費用・原価
補完が発動したレベルのみ追加: 2-V 1 call(約¥0.2)+補完分canonicalization(約¥0.3)+gloss整合(約¥0.2)=約¥0.7〜1.0/発動(過去実測の分解は`BUDGET_PLAN_01.md`)。不発動(E=0)は¥0。外側retryの全件再生成(約¥1.0〜1.9/周)が減る方向。記事セット(Std+Adv)あたり増分上限約¥2、平均では差引ほぼ中立〜微減見込み(委任_03で実測)。70円/記事セット目標への影響は軽微(上限でも約3%)。

## 11. 非採用・残リスク
- 7+5 Promptの数合わせ品質問題(Trial-02で5件枠に4件など)は補完で解決しない。7+5 Promptのproduction採用は自動確定しない(原文§4)。
- 補完候補も初回と同様の除外率を持つ(`duplicate_of_top3`など)。1回限りなので上限未達は許容。
- 2-Vがexcluded/alreadyを無視する率は未測定(委任_03で測る)。
