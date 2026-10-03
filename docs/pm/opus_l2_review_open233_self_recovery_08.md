# Opus独立レビュー#8: OPEN-233 機械判定(決定論的floor)の正式基準への整合設計と「動機」仕様の整理(2026-10-04)

管理ID: OPEN-233-SELF-RECOVERY-TRIAL-01
(1) レビューの位置づけ: PM_GOVERNANCE 11-3 条件A(新しい構造・処理フローの設計)、ユーザー明示指示(2026-10-04、Safety系の判定処理に触れるためOpusレビュー該当判定を要求)(2026-10-04)
レビュー対象: `docs/pm/design_open233_floor_alignment_01.md`(委任_58)
抽出元: `C:/Users/tensh/.claude/projects/C--Users-tensh-eigo-radio/f9ae115b-0305-437d-ac2d-b452b22a5e2a/subagents/agent-a08354b774dfa39c7.jsonl`(最初のuserメッセージ=依頼文、SubagentHandbackのmessage=Opus報告文をスクリプトで抽出。本文は改変していない)
性質: 読み取り専用の独立レビュー。Production採用可否は判断していない。

## (2) 依頼文(逐語)

---

## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(Opus独立技術レビュー#8: 機械判定[決定論的floor]を正式採用の「重大/軽微/問題なし」基準へ整合させる設計、および「動機」仕様の整理)。並行タスクなし。あなたは読み取り専用で、ファイルを作らない・編集しない。

## 性質/到達上限Status/禁止事項

- 性質: 実装前の設計に対する独立技術レビュー(`docs/pm/PM_GOVERNANCE.md` 11-3節 条件A: deterministic処理とLLM処理の役割分担の変更、Safety判定に触れる。ユーザーが2026-10-04に「該当する場合は必ずレビュー」と指示)。レビュー後はFableが再評価し、実装するか・ユーザーへ戻すかを判断する。
- 到達上限Status: なし。Production採用の可否は宣言しない。
- 禁止事項: ファイル編集、テスト・LLM・Trialの実行、Agent起動、巨大SSOTの全文読み込み。
- 費用上限: 該当なし。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)の該当判定: 条件A。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)

補足: 読み取り専用のためT-0は実行しない(保存は後続のSonnet委任で行う)。

## (g) 発火条件と独立レビューブロック

- 発火条件: 11-3節 条件A(Safety系の決定論的判定処理の変更)。ユーザー明示指示あり。
- 重複レビューの確認: Opus#6(対策全体)・#7(説明文混入)はfloor変更を対象にしていない。新規レビュー。

---
【Opus独立技術レビューの目的】
あなたの役割は「重要な技術設計に対する独立レビュー」である。Claude/Fableの案を
追認することが目的ではない。必ず次を独立に評価すること。
- そもそもその設計が必要か
- より単純な方法がないか
- 既存処理をそのまま利用できないか
- 不要な複雑化をしていないか
- 根本原因に対する対策になっているか
- 別のFailureを生まないか

【最低限、独立してレビューする12観点】
1. そもそもこの変更・設計は必要か
2. より単純な構造にできないか
3. 既存処理・既存データを利用できないか
4. 前段で取得済みの情報を後段で失ったり再探索したりしていないか
5. 不要なLLM処理を追加していないか
6. 非決定性を増やさないか
7. Human Reviewを増やさないか
8. 不要Rewriteを増やさないか
9. コストを不必要に増やさないか
10. retry / fallback / regenerationと矛盾しないか
11. Failure時に安全側へ倒れるか
12. 個別パッチではなく再発防止になっているか

【レビューの姿勢】
Claude/Fableの案を前提として追認しない。代替案の方が良い場合は、その代替案を
明確に提案すること。結論は「必要/不要」「推奨構造」「リスク」「代替案」の順で
簡潔に返す。
---

## ユーザー指示(原文、2026-10-04。全文は`DECISION_LOG.md`の委任_58エントリに逐語あり)

- 「ユーザー判断では、この表現(`prices began to fall`)は**軽微**です。一部の機械判定によってMajorへ強制昇格する状態は受け入れません。**機械判定も、今回正式採用した「重大 / 軽微 / 問題なし」の基準に合わせて見直してください。**単にこの1文だけを例外登録するのではなく、過去再分類で - LLM判定では軽微以下 - 機械判定だけでMajor となっていた8種類を確認し、現在の正式基準との不整合を修正してください。ただし、主体取り違え・数値改変・否定反転等、本当に重大なケースまで一括して緩めないこと。」
- 「目的は「機械判定を弱くすること」ではなく、**正式基準と機械判定を一致させること**です。個別例外の追加ではなく、同種ケースに再発しない形で修正してください。」
- 動機: 「**既存より厳しくする変更を、今回の線引き採用に便乗して追加しないでください。**整理だけで解消できるなら仕様・実装を整合させてください。本当に新しい価値判断が残る場合のみ `USER_DECISION_REQUIRED` としてユーザーへ戻してください。」
- 正式基準(2026-10-03): 重大=英語学習者に事実関係の重大な誤解を与えるもの/軽微=事実関係の核心は保たれているが表現の精度が少し落ちるもの/問題なし=確認済みFactから自然に導ける描写・推論で新しい具体的事実を追加しないもの。例: 「Also, some calls needed user information to continue.」=軽微、「They enjoyed AI's convenience, but a human was on the other end. They did not realize it.」=問題なし、「Just after the charge plan disappeared, prices began to fall.」=軽微。「数値・主体・否定・比較・時期などの機械的な安全装置については、今回の採用内容だけを理由に勝手に緩めないでください。」
- 「Human Reviewは非常口であり安易な逃げ道にしない」。

## 背景(短く)

Stage 2(判定役LLM)の後に、決定論的なfloor(`apply_floor`)がCheckerのフラグ(`changed_actor`/`changed_number`/`changed_negation`/`changed_comparison`/`changed_time`=`FLOOR_FLAGS`)のいずれかがtrueなら、LLM判定に関係なくBLOCKINGへ昇格させる。委任_58の調査(`docs/pm/design_open233_floor_alignment_01.md`、オフライン再生`er052_output/open233_floor_alignment_offline_01/`)の要点:
- 8種類すべてで、floorはフラグだけを根拠に昇格(裏取りなし)。6種類は列挙の波及(委任_35で是正済み)、2種類(K13・K14)はCheckerが直接フラグを立てた型で再発し得る。K19(`changed_comparison`)も同型。
- floorだけが重大な誤りを止めた記録が2件(Safety-critical A4-0: 13記録中1件、K16: 19記録中1件)。役職名詞に絡む`changed_actor`は、軽微以下(K13・K14)と重大(A4-0・K18)を字面で区別できない。
- 是正後のrun(rep20〜22)では、floor単独でBLOCKING(LLMは非BLOCKING)は14件中1件。
- 設計案: F1=3値の裏取り付きfloor(CONFIRMED=裏取りで不一致確認→BLOCKING維持/CLEARED=整合の証拠→解放/UNDETERMINED=現行どおりfloor維持)。F2=フラグの階層化(actor・comparison・timeをLLMへ委ねる。Safety対照11件を解放しA4-0・K16が止まらなくなるため不採用推奨)。F3=Stage 2へフラグを再提示(priming前例あり)。F4=F1+UNDETERMINED分だけStage 2をフラグを見せずにもう1回独立に呼び、どちらかがBLOCKINGならBLOCKING(推奨。Opus承認後にのみ有効化)。決定論部分のオフライン再生ではF1/F4はSafety対照の解放0件。
- 動機: 「動機の帰属=軽微」(Ledger確認済みの事象に理由づけを添えるだけ)と「動機の創作=重大」(Ledgerに無い意図・仕組みを新事実として書く)は別事象で、整理で解消可(案文はdoc §3)。残る小論点B1-c(notes_for_writerが禁じた因果推論の断定をQUALITYに再ラベル済みの件)。
- V7 rubricの文言「比較の差は…明確にBLOCKING」と例「prices began to fall→QUALITY」の食い違い。

## (a) 論点(限定)

1. **F1の3値設計は妥当か**: CONFIRMED/CLEARED/UNDETERMINEDの各条件(doc §2-4)。特にCLEARED条件(整合の証拠がある場合の解放)が緩すぎないか。Ledgerが日本語・claimが英語である点(言語をまたぐ裏取り)の扱い。固有名詞の日英別名表を入れるべきか(訳語を「新規」と誤判定して解放されない5件、A2A3-0のCONFIRMEDが誤判定による可能性)。
2. **F4の独立再判定(OR)はSafety方針の変更に当たるか**: floorがUNDETERMINEDのとき、Stage 2をフラグなしでもう1回呼び、2回のどちらかがBLOCKINGなら維持。追加LLM呼び出し(UNDETERMINED分のみ)、非決定性、費用。A4-0・K16の救出率の推定(両方が見逃す確率約0.3〜0.6%、独立性の仮定)は妥当か。これはユーザー判断事項にすべきか、Fable判断で進めてよい範囲か。
3. **より単純な代替はないか**: 例えば「floorはBLOCKINGに確定させず、QUALITY下限+人間確認の印だけにする」「Checker側のフラグ定義(er003 Production Promptのため変更不可)の代わりに、Trial追記で『一般化・言い換え・方向のニュアンスではフラグを立てない』と指示する」「K13型(役職の一般化)だけを決定論で識別する(役職語彙の上位語表)」など。それぞれが「本当に重大なケースを緩めない」を満たすか。
4. **役職名詞のactorを字面で区別できない前提**は正しいか。同時に立つ他のフラグやissue文の語彙で区別する案の是非(n=1〜13)。
5. **V7の文言の食い違い**(「比較の差は明確にBLOCKING」対「prices began to fall→QUALITY」): rubric文を直すべきか、floor側の整合だけで足りるか。直す場合の最小文言。
6. **「動機」の整理**(doc §3): 「帰属」と「創作」が別事象という整理、案文(1)〜(3)が既存より厳しくならないか(特に案文(2)の「仕組み・意図」の追加は既存のB4-a=BLOCKINGの書き漏れ補足と言えるか)。B1-cの小論点は整理で解消できるか、ユーザー判断が要るか。
7. **再発防止になっているか**: 列挙複製元の過剰フラグ(K13型)を設計に含めるべきか。Checkerのフラグ品質に依存する構造自体の問題。
8. **安全対照**: オフライン再生(決定論部分)でF1/F4が解放0件という結果の信頼性。再較正計画(委任_55の較正セット+8種類+K19、¥8〜10)で足りるか。Hormuz NG5(Stage 1フラグなし)の扱い。
9. **限定flow確認の計画**(doc §5): 6 instance×n=2、合格基準、29件へ進まない条件、n=2で何が言えるか。
10. **Production配線時のリスク**: floorの変更が、自己修復機構のProduction接続時にretry/fallback/regenerationと矛盾しないか。runtime evidenceに何を残すべきか。

### 論点と材料の対応

| 論点 | 材料 |
|---|---|
| 1〜4、7 | doc §2(2-1表、2-2機械判定一覧、2-3切り分け、2-4設計案)、`replay_01.py`・`replay_01_result.json`・`K_rows.csv`、runner `apply_floor`/`FLOOR_FLAGS`/`build_precheck_floor_claims`/`_ACTOR_NOUN_PATTERN`(Grepで位置特定) |
| 5〜6 | doc §3、`er052_open233_self_recovery_stage2_production_01.py`(rubric V7、Grep `MATERIALITY_RUBRIC_V7`)、`er052_open233_self_recovery_stage2_calibration_01.py`(Grep `V7`)、`er052_output/open233_safety_control_03/rubric_diff.md` |
| 8〜9 | doc §2-5、§5、`er052_open233_element_trial_safety_control_05.py`(較正セット) |
| 10 | doc §2-4の各案の整合欄、`docs/pm/open233_a1_production_reflection_plan_and_ja_scope_2026-10-03.md` A-3 |

## 事前指定Read一覧

- `docs/pm/design_open233_floor_alignment_01.md`: 全文(レビュー対象)。
- `er052_output/open233_floor_alignment_offline_01/replay_01.py`: 全文。`replay_01_result.json`・`K_rows.csv`: 必要部分。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `apply_floor`、`FLOOR_FLAGS`、`build_precheck_floor_claims`、`_ACTOR_NOUN_PATTERN`、`apply_disclosure_gap_downgrade`、`DISCLOSURE_GAP_DISQUALIFYING_FLAGS` → 該当範囲だけ。
- `er052_open233_self_recovery_stage2_production_01.py`: Grep `MATERIALITY_RUBRIC_V7`、`動機` → 該当範囲。
- `er052_open233_self_recovery_stage2_calibration_01.py`: Grep `V7` → 該当範囲。
- `er052_output/open233_safety_control_03/rubric_diff.md`: 全文。
- `docs/pm/open233_materiality_criteria_2026-10-03.md`: 正式採用節。
- `er003_v1_en_direct_vfl_01_generate.py`: Grep `changed_actor` → フラグ定義の範囲(読むだけ。Production Promptで変更不可)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 上記のGrepパターン。追記・更新: なし。

## (e) Progressive Disclosure手順

> 上記で診断できない場合のみ、追加でファイルを読んでよい。
> ただし読む前に「読む理由」と「対象ファイル・行範囲」を1行で宣言し、
> 診断結果の最後に「追加で読んだファイル一覧と概算文字数」を自己申告する
> こと。無宣言での巨大ファイル全文読み込みは禁止。診断精度を優先し、
> 必要な事実を省いてまで読込量を減らしてはならない。

docの記述とコード・記録が食い違う場合はコード・記録を正として報告する。

## 実行コマンド全文

なし(読み取り専用)。

## SSOT追記文

なし。

## Git(明示add対象・コミットメッセージ・trailer)

なし。SSOT編集権: なし。

## 報告(RESULT_PACKET項目)

最終メッセージで次を返す(ファイルは作らない)。
1. 総合結論(10行以内): 推奨する案、採るべきでない案、Fable判断で進めてよいか/ユーザーへ戻すべき論点、実装前に必要な確認。
2. 論点1〜10それぞれについて「必要/不要」「推奨構造」「リスク」「代替案」。docと異なる結論は明示。
3. 12観点のうちdocが満たしていない・答えていないもの。
4. docの事実誤認(あれば。該当行・コード行つき)。
5. 確認できたことと推測の区別。今回の材料で十分に答えられなかった論点。
6. 追加で読んだファイル一覧と概算文字数。

---

## (3) Opusレビュー全文(逐語)

---

## Opus独立技術レビュー#8 結果(OPEN-233-SELF-RECOVERY-TRIAL-01、読み取り専用。ファイル作成・編集なし)

### 1. 総合結論
- 機械判定(floor)の整合は**必要**。ユーザーはK19型の強制Majorを明示的に拒否しており、K13/K14型は現行コードで再発し得るため。ただし規模は小さい(是正後のrunではfloor単独のBLOCKINGは14件中1件)。辞書を積み増すような作りにしないこと。
- **F1は今の形では採用しない方がよい**。理由は2つ。
  - 必要なCLEARED(整合確認で解放)は「比較」だけだが、その判定は実質的に空振りする。HF-009の事実文には上昇語と下落語が両方あるため、どんな方向の主張でも解放される。ユーザーが禁じている「撤回後に原油価格が下落した」も、コード上CLEAREDになる。
  - 数値・否定・時期のCLEAREDは、8種類とK19のどれにも必要ない。しかも次の誤りを見逃す危険がある。
    - 数値の付け替え(Ledgerにある20%を別の対象に付ける)
    - 日付の付け替え(7/13と7/14の取り違え)
    - 否定語を使わない反義語による意味の反転
- **F4の「フラグを見せない独立再判定」は事実誤認に立っている**。Stage 2は現行でもフラグを見ていない(`run_stage2_batch_variant`のprompt、calibration_01.py 627〜638行には`dev`が入っていない)。つまりF4は「同じpromptでもう1回引き直すだけ」で、新しい独立性は得られない。
- **推奨構造(代替案「F5」)**:
  - 決定論で不一致を確認できたもの(CONFIRMED)は、BLOCKINGで確定。LLMで外すことはしない。
  - 自動で解放する状態(CLEARED)は廃止する。
  - CONFIRMED以外で、floorとLLMの判定が食い違う場合だけ、別callを1回呼ぶ。そのcallにはCheckerのissue文を「検証すべき仮説」として見せ、Ledgerからの引用付きで判定させる。両方が非BLOCKINGのときだけ解放する。
- **ユーザーに戻すべき論点は1つ**: Checkerのフラグが立ったclaimをLLM判定で解放すること(F4でもF5でも)。「主体・時期・比較」の決定論的な保証を確率的な保証に置き換える新しいリスク許容の判断なので、ユーザー判断が必要。
- **Fable判断で進めてよいもの**:
  - CLEAREDの撤回
  - V7文言の整合(既存R3(e)の文言へ揃える)
  - 動機の整理(文書化のみ)
  - 下記の測定(挙動を変えないTrial)
- **実装前に必要な確認**:
  - 重大ケースと敵対的な合成ケースに対する、Stage 2単体の測定(n≥10)
  - 2-of-2降格との相互作用を塞ぐこと
  - 再判定callが失敗したときにBLOCKINGへ倒れること

### 2. 論点別

**論点1 F1の3値設計**
- 判定: 一部だけ必要。CONFIRMEDは必要、CLEAREDは不要かつ危険。
- 推奨構造: CONFIRMEDは「維持する方向にしか働かない」ので安全。誤判定しても現状維持になるだけ。CLEAREDは廃止する。
- リスク(コード根拠):
  - `corr_comparison`は事実ブロックからnotes_for_writer行を除外したうえで方向語の集合を比べている。HF-009の1行目には「上げ幅を縮小」(上げ=上昇、縮小=下落)と「高い水準へ戻った」(高・戻=上昇)があるので、主張の方向語が何であってもCLEAREDになる。K19が解放されるのは「整合の証拠」があるからではない。
  - `corr_number`と`corr_time`はLedger全文のどこかにトークンがあればCLEAREDにする。そのため付け替えを検出できない。例: Hormuzでは「10時16分」があるため、主張中の「10」がLedgerにあると扱われる。
  - `corr_negation`の「両方とも肯定ならCLEARED」は、反義語による反転(withdrew/kept等)を見逃す。
- 言語をまたぐ扱いと日英別名表: F5ではCONFIRMED側にしか効かないので、国名・主要組織など汎用の別名表は入れてよい。誤っても「判定LLMへ回る」だけで、自動解放は起きない。役職名詞の辞書は不要(docと同意見)。
- 代替案: K19型も下記F5の確認ルートで扱う。

**論点2 F4の独立再判定**
- 判定: Safety方針の変更に当たる。**ユーザー判断事項**。
- 推奨構造: 見えていない状態での引き直し(F4)より、Checkerのissue文を見せる別callの確認(F5)を推奨する。
  - 1回目が見落とした観点(主体の取り違え)を直接検証させられる。
  - 委任_16のprimingは、同じbatch内の他claimへ寛容化が波及した現象だった。claim単体の別callなら、その経路はない。
  - issue文を見せるとBLOCKING寄りになるが、その場合のリスクは「解放が減る=現状維持」で済む。
- リスク:
  - 救出率の推定(0.3〜0.6%)は点推定にすぎない。A4-0は13記録中1件の見逃し、K16は19記録中1件で、95%の上側信頼限界はそれぞれ約36%・約26%。二乗しても上限は約13%・約7%になる。
  - 13記録は複数のrubric版にまたがっていて、V7は従来より緩い。V7での見逃し率は未知(n=2しかない)。
  - 実装上の落とし穴: `apply_stage2_two_of_two`は`run_stage2`を呼び直しており、その中で`apply_floor`が再適用される(2346行)。流用すると2回目の`materiality`は常にBLOCKINGになる。`llm_materiality`で比較する必要がある。
- 代替案: ユーザーが確率的な解放を受け入れない場合は、主体と時期はfloorを現状維持し、K13/K14は過剰品質として受容する。

**論点3 より単純な代替**
- 「QUALITYを下限にして人間確認の印」: 不可。A4-0型が自動で止まらなくなり、Human Reviewも増える。
- 「CheckerへのTrial追記」: 不可。Production Promptとずれるうえ、本物の取り違えの検出率にも影響する。「Prompt変更なし」の決定にも反する。
- 「役職の上位語表」: 不可。K13はusersとemployeesの関係で上位語関係ではなく、A4-0と区別できない。個別例外にもなる。
- 結論: F5(CONFIRMEDは確定、それ以外の食い違いは確認callを1回)が最も単純。方向語・否定語・日付の辞書を新たに増やさずに済む。

**論点4 役職名詞のactorを字面で区別できない前提**
- 前提は正しい。K13とA4-0は、どちらも「users」が絡む`changed_actor`。K14とK18も同じ構造。
- Ledgerは日本語(「ユーザー」)なので、英語の役職語はLedger全文に常に存在しないと判定される。`_ACTOR_NOUN_PATTERN`系のチェックでは両方ともCONFIRMEDになり、区別できない。
- 同時に立つフラグで区別する案(n=1〜13)は過学習になるので不採用。

**論点5 V7文言の食い違い**
- 判定: 直すべき。F4でもF5でも解放をLLMに委ねるため、rubricの内部矛盾(比較の差は明確にBLOCKINGと書きつつ、K19の例はQUALITY)は判定の揺れに直結する。
- 最小文言: 同じpromptにすでに入っている既存R3(e)(calibration_01.py 136行)に揃える。
  - 現行: 「数値・主体・否定・比較・時期の差は、この原則の対象外で、従来どおり明確にBLOCKING」
  - 案: 「数値・主体・否定・比較・時期について、Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は、この原則の対象外で、従来どおり明確にBLOCKING」
  - 新しい基準を作るのではなく、既存の基底rubricへ整合させるだけ。
  - s2p側の`_V7_NEW_TIEBREAK`(「機械的にBLOCKING」)も、Production配線時に同じ修正をする。
- 再較正は必須(Safety-critical 5件とSafety12)。

**論点6 動機の整理**
- 「帰属」と「創作」は別の事象という整理に同意する。
- 案文(1)(s2pのQUALITY行): 内容は妥当。ただしs2pは現行flowで使われていないので、Production配線時に回してよい。
- 案文(2)(V7(1)(イ)に「仕組み・意図」を追加): **不要で、むしろ危険**。
  - B4-aがBLOCKINGに保たれているのは、同じprompt内の基底R3(b)(c)による。書き漏れの補足をする必要がない。
  - 限定なしの「意図」を、条件→断定を扱う(1)の中に入れると、B1-c型の動機の帰属がBLOCKINGへ戻る可能性がある。V7より厳しくなる。
- 案文(3)(設計書の文言): 文書だけの変更なので可。
- B1-cの小論点: 整理で解消できる。
  - ユーザー自身が2026-09-30に、ほぼその文(「市場が海上リスクを重視したから価格が戻った」)を「ぎりぎり許容」と述べている。
  - 基底R3のQUALITY行(calibration_01.py 138〜143行)も「市場や読者が特定の要因を重視したとみられる」を明示している。
  - 残るのは「notes禁止=BLOCKING」(s2p)と自然な推論の優先順位という一般則の潜在的な矛盾だけ。Production配線時の確認項目として記録すれば足り、ユーザー判断は不要。

**論点7 再発防止**
- 判定: 列挙の複製元にある過剰フラグも、設計の対象に含めるべき。
- 推奨構造: F5は種類を問わず「floorとLLMの食い違い」に対して1つの仕組みで効く。複製元も「直接立ったフラグ」として同じ経路に乗るので、個別パッチにならない。
- Checkerへの依存は構造上残る(Prompt凍結のため)。CONFIRMEDは確定、それ以外は確認、という形で影響を限定する。

**論点8 安全対照**
- オフライン再生で「解放0件」という結果の信頼性は低い。
  - Safety12の比較・否定のfixtureは`related_fact_id`が無く、UNDETERMINEDで終わっている。CLEAREDのロジックは一度も試されていない。
  - 敵対的なfixture(方向の反転と両方向を含む事実の組み合わせ、数値の付け替え、日付の付け替え)が無い。
  - 再生側のコードは実装予定のコードではない。
  - Ledgerを取得できなかった記録が8件ある。
- 再較正計画(¥8〜10)では不足。次を追加する。
  - 敵対的な合成ケース。例: HF-009に`changed_comparison`を付けて「After the plan was withdrawn, oil prices fell.」、20%の付け替え、7/13と7/14の取り違え。
  - 重大ケース(A4-0・K16・K18・A2A3-0)を確認call単体でn≥10。
  - 過剰ケース(K13・K14・K19・B2「vanished overnight」・B4「Names…」)。
  - 概算: 単体callで¥10〜30。
- Hormuz NG5: 「Stage 1フラグが無いので影響外」とするのではなく、合成フラグを付けて解放経路の試験に入れる。

**論点9 限定flow確認**
- n=2で言えるのは配線・回帰・JA不変まで。A4-0の見逃し(1/13程度)は12 runではまず起きない。解放経路を通らないまま「合格」になり、意味のある結果にならない。
- 合格基準の「floor単独BLOCKINGが0〜1件/run」は、解放するほど良く見える逆向きの指標。合格基準から外し、監視値にする。
- 代わりに次を置く。
  - 解放された件は全件をログに残し、人がラベル付けする。
  - 重大ラベルのclaimが1件でも解放されたらSTOP。
- 解放経路の安全性は、論点8の単体測定(記録済みの1回目判定を再生して2回目だけを呼ぶ)で担保する。
- 29件へ進まない条件は妥当。

**論点10 Production配線時のリスク**
- 必須対策:
  - (a) 解放したclaimは`apply_stage2_two_of_two`の降格対象から外す。外さないと、Normal群では`floor_reason=None`になり、LLMが2回連続でBLOCKINGを出さない限り降格される緩みが生じる。docの§3-3「緩む箇所」に記載がない。
  - (b) `dev`のフラグは書き換えない。丸めの前例はフラグを書き換えているが、今回は解放理由を別のフィールドに持たせる。そうすればdisclosure降格とhook降格のガードは閉じたままになる。
  - (c) 確認callのAPI失敗やschema不一致は、BLOCKING固定にする。
  - (d) Rewriteの後のrecheckでは、解放状態を引き継がず、cycleごとに再評価する。
- runtime evidence: claimごとに次を残す。
  - フラグごとのCONFIRMED判定と、根拠になったトークン
  - 1回目の`llm_materiality`
  - 確認callの判定・basis・Ledger引用・`prompt_sha256`・費用
  - 解放の有無と理由
- 未確認: A-3(Production反映計画)のdocは読んでいない。

### 3. docが満たしていない・答えていない12観点
- 観点4: Checkerのissue文は手元にあるのに、F4は見ないまま引き直す設計で、その情報を捨てている。
- 観点6: Safety経路に非決定性が入ることによる再現性・監査への影響を評価していない。
- 観点10: 2-of-2との相互作用、`run_stage2`内でのfloor再適用、cycleごとの再評価が書かれていない。
- 観点11: 再判定callが失敗したときの扱いが未定義。
- 観点12: CLEAREDの方向語辞書はK19に合わせて調整されたもので、汎用的な再発防止になっていない。

### 4. docの事実誤認
- §3-1 F4と§3-2の理由(3): 「フラグを見せない独立呼び出し」はすでに現行の状態。calibration_01.py 627〜638行で、Stage 2の入力は`claim_text`・`local_context`・`origin`・`related_fact_id`・`section_type`だけ。
- §0-3と§2-2'の「非列挙floor単独18件」: このうち4件(iter2・iter3のフラグが空のもの)は、旧`changed_certainty`由来のfloor。現行コードで関係するのは14件(stdout 31〜48行)。
- §3-1所見「UNDETERMINEDの旗付き非列挙5件(重大2:過剰3)」: 実際は8件。B4「Names, plans…」(comparison)と、number 2件(rep19・rep21)が抜けている。number 2件もF4の再判定対象になる。
- §2-1 K19「事実側にも縮小があるのでCLEARED」: 整合の証拠ではない。事実文が両方向の語を含むため、どんな方向でも解放される。

### 5. 確認できたことと推測の区別
- コードと記録で確認したこと:
  - Stage 2がフラグを見ていないこと
  - floorの評価順とガード条件
  - CLEAREDロジックの挙動(replay_01.pyを読んで決定論的に導いたもの)
  - 再生の集計
  - V7とR3の文言
  - MUSE-HC-011に「1件」とあること(iter8の数値CLEAREDは、この件については正しい)
- 推測:
  - issue文を見せる確認callの方が、見逃しの相関が低いこと
  - 信頼区間の上限(二項分布の近似)
- 十分に答えられなかったこと:
  - V7での実際の見逃し率
  - K19のclaim_textが2文とも含んでいるか(K_rows.csvに本文が無く、doc記載を前提にした)
  - `HOOK_AWARE_OTHER_FLAGS`の中身
  - A-3の内容
  - er003のフラグ定義(前提は記録から判断した)
- `rubric_diff.md`と`open233_materiality_criteria_2026-10-03.md`は読んでいない。V7の本文はコードから直接読んだ。

### 6. 追加で読んだファイル(宣言どおり、該当範囲のみ)
- `C:\Users\tensh\eigo-radio\er052_output\open233_floor_alignment_offline_01\replay_01_stdout.txt`(全文、約6千字。replay_01_result.jsonの代わりに要約出力を読んだ)
- `C:\Users\tensh\eigo-radio\er019_output\family_x_refresh_e2e_01\meta\run_03\ledger\verified_fact_ledger.txt`(Grep「人種」±8行、約1.2千字。iter8の数値CLEAREDの妥当性を確認)
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_stage2_calibration_01.py` 120〜160行と540〜665行(約8千字。R3の基底文言、V7、Stage 2の入力)
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_stage2_production_01.py` 35〜59行(約1.5千字)
- `C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01.py` 440〜535行、1870〜1960行、2119〜2435行(約2万字。hook降格と2-of-2の相互作用を確認)

---

## (4) FableのPM評価

**Fable PM評価(2026-10-04、Opus独立レビュー#8)**
1. 照合(11-3節8項目): 委任_58の設計doc・Opus#8・ユーザー指示(2026-10-04 §1B・§2・§3)・正式採用の線引き・「本当に重大なケースを緩めない」・QCD・予算を照合した。
2. 採用(Fable判断で確定): (a)F1の「整合の証拠による自動解放(CLEARED)」は廃止する。Opusがコードで示したとおり、比較の裏取りは事実文に両方向の語があるとどの方向でも解放され、ユーザーが禁じる「撤回後に原油価格が下落した」も解放されうる。数値・時期・否定の自動解放は付け替え・反義語の反転を見逃す。(b)F4は撤回する。Stage 2は現行でもフラグを見ておらず(calibration_01.py 627〜638行)、「フラグを見せない独立再判定」は同じpromptの引き直しにすぎない。(c)決定論で不一致を確認できたもの(CONFIRMED)はBLOCKING確定を維持する(維持方向にしか働かず安全)。(d)V7の文言「数値・主体・否定・比較・時期の差は…明確にBLOCKING」は、既存の基底rubric R3(e)に揃えて「Ledgerと矛盾する重大な変更(数値の改変、主体の取り違え、否定の反転、方向の反転、時期の取り違え)は…明確にBLOCKING」へ直す(新基準の作成ではなく既存への整合。再較正必須)。(e)動機: 「帰属」と「創作」は別事象。委任_58の案文(2)(V7(1)(イ)へ「仕組み・意図」を追加)は採らない(B4-aは基底R3(b)(c)でBLOCKINGが保たれており不要。限定なしの「意図」は既存より厳しくなりうる)。案文(1)はProduction配線時に、案文(3)は文書のみ反映可。B1-cはユーザーの2026-09-30の判断と基底R3のQUALITY行で整理済みとし、「notes禁止=BLOCKING」と自然な推論の優先順位はProduction配線時の確認項目として記録する(ユーザー判断は不要)。(f)限定flowの合格基準から「floor単独BLOCKING 0〜1件/run」を外し監視値にする。解放は全件ログ+人がラベル付け、重大ラベルのclaimが1件でも解放されたらSTOP。(g)Production配線時の必須対策(解放claimを2-of-2降格の対象から外す/`dev`のフラグを書き換えない/確認callの失敗はBLOCKING固定/cycleごとに再評価)とruntime evidence項目を`OPEN-233-A1-PROD`に追加する。
3. ユーザーへ戻す(Opus指摘に同意): 「Checkerのフラグが立ったclaimを、LLMの確認で解放するか」。機械判定の決定論的な保証を、確率的な保証(確認callが見逃す可能性)に置き換える新しいリスク許容の判断であり、ユーザーのSTOP条件「Safety原則の変更が必要」に当たる。決定論だけでは、役職の一般化(K13・K14)と主体の取り違え(A4-0)を字面で区別できず、比較の目印(K19)も安全に解放できない。したがって「機械判定を正式基準に一致させる」には、(i)LLM確認による解放を導入する(F5)か、(ii)現状維持で一部の軽微な文が機械判定で重大のまま残ることを受容するか、のどちらかになる。
4. Fableの推奨: F5を**比較(`changed_comparison`)と時期(`changed_time`)に限って**導入し、主体・数値・否定は決定論のまま維持する。理由: ユーザーが「本当に重大」と名指しした主体取り違え・数値改変・否定反転を確率的な判定に委ねない。K19型(比較)はこれで解放され、K16型(時期)は確認callで止める(2回とも非BLOCKINGのときだけ解放、失敗はBLOCKING固定)。K13・K14型(主体の一般化)は過剰品質として受容する(是正後の実行で機械判定単独は14件中1件)。導入前に、Opus指摘の単体測定(重大ケースK16・A4-0・K18・A2A3-0と敵対的合成ケース[「After the plan was withdrawn, oil prices fell.」・20%の付け替え・7/13と7/14の取り違え]、過剰ケースK13・K14・K19・B2「vanished overnight」・B4「Names…」をn≥10、¥10〜30)で見逃し0・解放の妥当性を確認してから有効化する。
5. 進行判断: 上記3はSTOP条件に該当するため、`USER_DECISION_REQUIRED`としてSTOPする。限定flow確認と29件横断(承認済み)は、機械判定の扱いが決まってから1回で行う(2回に分けて費用を重ねない)。
6. Production採用の可否は判断していない。
