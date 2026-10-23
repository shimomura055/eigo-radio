# OPUS_REVIEW_REQUEST_03: 条件A(工程出力・入力の構造変更)独立技術レビュー依頼

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 委任_06 / 依頼はFableがPM_GOVERNANCE 11-3に従って発行(本書は論点整理のみ。Opusレビュー自体はユーザー承認Gateではない)。
対象: `DESIGN_03.md`(推奨=案A Adv独立化+用法先決め、案B Std律速検証)、根拠=`ROOT_CAUSE_02.md`、probe=`kp_probe_03*.py`/`kp_probe_03_results.jsonl`/`kp_probe_03_summary.json`/`kp_probe_03_report_out.txt`。
レビュー観点(11-3): 前提の妥当性、見落とし、過剰設計、隠れた副作用、検証の十分性。以下の論点のうち**結論に効くもの**を優先。

## 論点

### Q1 因果の読みは十分か(最重要)
- 主張: Adv説明の「acceptable」型の狭さはStd glossの含意が原因(`draw a line`: gloss=一線を引く 3/4、他gloss/なし 0/4、n=4×5条件。`Carry the Load`: 荷物を運ぶ 字義2/4、他0/4)。
- 疑う点: n=4/条件は小さい。glossの語自体でなく「gloss有無によるJapanese-contextの存在」が効いた可能性(「一線」以外の4条件は同系統の中立的訳語)。生成はluna 1 modelのみ、Judgeではなく**目視+語照合**(`acceptable/allowed`出現)。追加で確認すべき統制条件は何か(例: 一線を引く以外の道徳含意glossを複数KPで)。

### Q2 E3(中心義固定)の悪化の解釈
- 実測: E3 13/28(46%) vs E0 22/28(79%)。悪化KPは`take the wheel`・`Carry the Load`・`reach for someone's wallet`で、G2が`usage_type`を字義と判定したKP。
- 解釈案: (1)判断1回の誤りが固定される(独立性喪失)、(2)単に当該modelの判断力不足で、上位modelなら案Sが最善。(2)ならE3-solで案Sが復活する。Trialで案S-solを1回測る計画は妥当か。canonical call carrier(全文を見る既存call)で再検討する価値はあるか。
- 対立する説明: G2の`core_sense_en`が英語で長い、説明Promptと整合しない等の実装由来の悪化はないか。

### Q3 独立化(案A)の設計妥当性
- gloss入力を外すとStd/Adv整合の構造保証が弱まる。現行でも不整合は7件中2件、A-1後のP判定は100%(n小)。条件付き再整合(不一致時のみAdv表示glossを再生成)を最初から入れるべきか、Trial結果次第でよいか。
- E4は`bring in`で字義側に落ち、`pull someone under`で曖昧。独立判断の精度が律速になる点で、Std側と同根(用法判定の律速)。案Aの利得(伝染除去+併記解消)が損失(独立判断の外れ)を上回る判断基準は妥当か。
- usage_type→core_sense→explanationのschema順序は、`english_explanation`のみ採用するため下流不変だが、strict schemaの出力順保証(OpenAI Responses API)は実装上確認が必要。順序が逆転した場合の挙動(core_senseが後付けになる)をどう検査するか。

### Q4 評価系(Judge)の妥当性
- 現行E2の`core`基準は、表現そのものの意味と記事固有条件を区別できず偽陽性が多い(E0/E4不合格14行のうち約半数が『…に限定』)。DESIGN_03 §6-3の修正案(定義的語は混入に数えず、記事の対象・目的・場面・評価条件のみ)とキャリブレーション手順(既存の不合格行を再判定して基準固定)で十分か。2系統+Fable目視20%で足りるか。
- Std gloss側の評価(`literal`/`sense_ok`)は、OF-07の定義(日本語でも同じ比喩が自然に通じる表現は逐語に数えない)を維持してよいか。「一線を引く」と「区別をはっきりさせる」はどちらを正解とみなすか(ユーザー判断事項か)。

### Q5 承認済み仕様との関係
- 案Aは承認済みB仕様(Trial-02 B候補、`CURRENT_SPEC.md:2032`、PROMPT_SHA256・Trial-02逐語性)の入力・Prompt・schema変更。承認時の目的(平易な英語解説)を損なわず、実装選択(日本語参考意味の入力)の変更とみなしてよいか。それとも承認文の「逐語」を厳格に読んでユーザーへ正式にB仕様変更を諮るべきか(推奨=後者の手続きで、VALIDATED後に諮る)。
- 旧ルール・旧testの撤去対象の網羅(`japanese_reference_meaning`行、signatureのgloss項、`er041_..._test_01.py`の固定SHA)に見落としはないか。

### Q6 Std側の方針転換(Charter 5)
- Prompt/構造の変更(A-2、G1、G2)が差し引き0である以上、「Prompt反復停止→model律速検証(Sol)」へ転換する。Solは+約1.9円/セット(+2.7%)。この転換とgate(NG率半減)の妥当性。Sol以外の選択肢(Std glossの候補2案出力+自己選択、事前登録型の慣用句gloss表など)を検討すべきか。
- それでもStdが改善しなかった場合の進言の形(辞書資産整備、ユーザー選定の慣用句リスト等)。

### Q7 統計設計
- 検証セット≥75 KP×2〜3 rep、Judge 2系統+目視。ノイズ床(同一arm再生成のPASSぶれが約25〜50% KP)を考慮して、「現行以上」「5%以下」といった数値基準を方向判断として扱う設計で足りるか。必要なn・rep、またはJudgeの再判定一致率の事前測定は必要か。

### Q8 その他の見落とし
- X/Z差(Zの対話型・物語KPの扱い、Z `he/she`はA-1対象外)。
- 説明signatureからgloss項を外すことのStore reuse(`ReuseKey`/OPEN-471/472統合)への影響。
- 費用: Trial≤60円の内訳と段階gate、本委任probe 13.43円(上限15円)の扱い。
- A-1配線との同時採用順序(A-1は既に`APPROVED_FOR_PRODUCTION`、案AはVALIDATED後のユーザー判断が別途必要)。

## 既知の限界(依頼時点で開示)
- probe-03はn=14 KP×2回、model=gpt-6-luna、Judge 1系統(Sonnet)。E0/E1/E4間の優劣は未確定。Std側の目視判定は1名(Sonnet)。
- G arm・E armは原因切り分けで、Prompt案の最終化ではない。
- 上位modelの判断精度は未測定。
