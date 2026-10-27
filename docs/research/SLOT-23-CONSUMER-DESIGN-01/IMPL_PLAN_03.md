# IMPL_PLAN_03 実装分割計画(IMPL_PLAN_02を置換。Opus条件A所見反映、read-only設計・API 0)
設計正本=`DESIGN_03.md`、契約=`CONTRACT_03.md`、矛盾一覧=`SPEC_CONFLICT_02.md`(+DESIGN_03 §J)。優先順位 Q>D>C。独立作業は並列化。

## 1. 前提・先行作業
- 並行中: A班(委任_04A: `er_learning_highlight_01.py`新設+**オフライン解決器の実行**)、B班(委任_04B: `er003`のlevel化+`er128`のマーク/reconsume/G1)。GPG委任_05Cは完了済みでworktree分離は不要。
- **配線(C/D/E)の前提条件**: 既存の確定済みX/Y/Z run全件(AI島含む)で解決器をオフライン実行(API 0)し、誤STOP 0を確認する(Opus条件2)。結果が出るまでC/D/Eの結合commitはしない(契約stubでの先行は可)。
- AI島のassemble停止(M3 Style Gate)の解消は別Agent担当。解消までは複製run+fixtureでC班を完了する。

## 2. 班別所有・順序
| 班 | 範囲 | 所有 | 依存 |
|---|---|---|---|
| A | 共通描画+照合+G3拡張+test+オフライン実証 | CONTRACT_03 §9のA行 | なし |
| B | Std Part 1 level化(M6全関数+golden)、Std検査、record側(継承/導出ヘルパ、署名、G1不変条件、`reconsume`、`which="highlight"`分岐) | 同B行 | なし |
| C | X配線、標準page builder(`check_page`+G3+Part 2 4者一致)、`display_spec`検出STOP共通module、`audio_review_player` CSS、AI島再ビルド、`er019`のS一覧(R4) | 同C行 | A・B(契約先行→結合)・オフライン実証 |
| D | Y配線、vocab対象levelのPart 1ちょうど1個のValidator化 | 同D行 | 同上 |
| E | Z配線、`has_vocab_on_page`に積極検出 | 同E行 | 同上 |
| **M** | **マーク発行の最後の1commit**(`new_review`の`std_part1`付与と`display_spec`導出。M14) | B班が実施 | A〜E完了+Validator全揃い |
| F | evidence 6経路+実ブラウザ(375/390px・DPR2/3)+Closeout素材 | 出力のみ | M完了後 |
- 順序: A‖B → オフライン実証 → C‖D‖E → M(1commit) → F → Fable独立受入。マーク発行をA〜Eより前にcommitしてはならない(危険な中間状態の回避、M14)。

## 3. 契約
`CONTRACT_03.md`が正本(型・関数・原因コード・HTML属性・G1不変条件・継承規則・遅延import・所有表)。

## 4. 統合手順
1. `er128_kp_confirmed_content_01.py`はBのみ編集。A提供の`er128_kp_highlight_01`は遅延importで呼ぶ。
2. C/D/Eは各自のrunner/builderのみ。共通ファイルはA/Bへ依頼。
3. 各班commit前: 関連test PASS、既存回帰、Secret grep 0、`git status`で他Agent差分を除外、pathspec付きcommit。

## 5. テスト計画(API 0)
- Adv回帰: Prompt・sha・signature・保存JSON・HTMLのバイト同一(golden)。a2のPrompt・sha(`_A2`)・signatureもgolden。
- 既定動作: マーク/`display_spec`無し→全builder出力が従来とバイト同一(6経路)。付与は`new_review`1箇所のみ(Grep+test)。環境変数/設定dictで迂回してON/OFFできない。ただし**既存kill switch(`EIGO_KP_CONFIRMED_PROTECTION=0`)**ではG3ハイライト検査がスキップ+disabled markerとなる(M10)。表示有効化はflag非経由。
- 照合: `carried over`/`taken a detour`/`looked at separately`/`erased`、`first_of_N`、曲線引用符とのnorm比較(M2)、`text_sha256`不一致(M1)、単調整列と短文の誤ヒット防止(M4)、番号順sort+`HL_OCCURRENCE_RELOCATED`(AI島Std③`Strategy`、M3)、範囲内0件(③訳のみ/①②ISSUE)、LR対応(R5)、包含(向き問わず)・③同士交差NOTICE・①②交差ISSUE(R1)。
- 不変性/表示: 装飾剥がし=元台本、public `⏸`0、dev `⏸`はhighlight外、`check_page` PASS、`data-hl`単位のG3(Zクリップ分割)、③`title`なし、凡例/訳リストに禁止語なし、Std Headに`(A2)`なし。
- Std Part 1: M6全関数のlevel通し、Validator(vocab対象levelでPart 1ちょうど1個、X/Y/Z)、確定保持(G4)、マーク無し旧reviewは従来。
- マーク: `display_spec`継承(revise/adopt-existing/自動更新でも保持)、`std_part1`署名(存在時のみ)、G1不変条件。
- reconsume: confirmation_id/origin保持、review_lock下更新+`validate_selection`、冪等、hash chain、QA NG→`reconfirm_required`、署名変化でZ/Y/XがAPI 0再バインド・音声sha不変(M9)。
- 回帰: `er128_*_test`/`er119_*_test`/`er120_*_test`/`er121_*_test`/`er063_*`/`er019_*`/`er_user_listening_page_*`系を全件。

## 6. 受入条件14との対応
IMPL_PLAN_02 §6の表を継承する(担当班のみ上表に合わせ読み替え:「F」はM完了後)。#14の旧経路Grepには、R4の完了基準(Part 1系関数内の`"b1b"`リテラルが既定引数以外で0件)を追加する。

## 7. 費用・evidence(R7、N2)
- COST_02 §2(b)を削除(N2)。Std Part 1約¥0.16/記事セット、②のみなら約¥0.08。
- evidenceはマーク付きの新規確定(`--actor evidence`)または複製runでのreconsume。各Familyで③を含める。GPG05CのY run dirとは共用しない。
- 追加見込み: reconsumeの確定Redundancy QA(LLM、少額)。合計は7-7の300円以下想定(承認済みScope内)。

## 8. 報告9項目の雛形
IMPL_PLAN_02 §7を継承し、3項目めにM7の解釈(Std Part 1=①+②とその根拠)、M3の規則(表示範囲=Full Story本文、範囲外出現の再配置)、解説言語(作業仮定A、ユーザー確認中、Bの差分は付録X1)を明記する。

## 9. 判断候補
- 解説言語(ユーザー確認中): 作業仮定A。Bなら付録X1の差分がユーザー承認事項(Fableが確認中のため新規の判断候補ではない)。
- M3規則・M7解釈: 分類B(Fable採用、ユーザー報告に明記)。他に新たなユーザー判断なし。
