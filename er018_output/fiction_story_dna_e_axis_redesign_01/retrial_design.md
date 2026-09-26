# retrial_design.md

管理ID: FICTION-STORY-DNA-E-AXIS-REDESIGN-01
Status: Trial専用、未承認draft実装。到達上限VALIDATED。

## 目的A: E軸偏り(現実系/非現実系の分散)の観察

**分類基準(明文化、実行前に固定)**:
- 「現実系」= E軸の値が`contemporary everyday reality` /
  `realistic but socially unusual situation` /
  `realistic but emotionally unusual situation`(index0-2)、またはE軸が
  DNAに含まれないRun。
- 「非現実系」= E軸の値が`future` / `reality with one changed rule` /
  `supernatural / fantastical world`(index3-5)。

この基準は「現実の物理法則・技術・制度がそのまま成立する世界か、明示的に
1つ以上のルール/技術/存在が現実と異なる世界か」という一次元の軸で、E軸の
定義文言(委任文の逐語)に沿った素朴な二分である。

**測定対象**:
1. 5 RunでDNAとして引かれたE値そのものの分布(E軸を持つRunのみ、乾式
   dna_log.jsonから集計可能)。
2. 各Runで生成されたCore Provocation候補(15案想定、1-3案×5 Run)が
   実際にどちら寄りの世界観を描いたか(候補文面から目視判定、機械分類は
   しない)。
3. 各Runで生成されたStory本文(5本)が実際にどちら寄りの世界観だったか
   (Story DNAのE軸指定と、実際の物語内容が一致するとは限らないため、
   両方を別々に記録する)。

比較対象: 前回Bias除去Trial(FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01、
旧E軸)の5本におけるE軸分布・Story世界観。

## 目的B: 殺人・死の切り分け

**タグ定義(実行前に固定)**:
- `violence`: `none`(暴力描写なし) / `threat`(暴力の脅威・予告のみ、実行
  されない) / `injury`(負傷・非致死的暴力が実際に描かれる) / `killing`
  (殺人が実行される、または過去に実行されたと明示される)。
- `death_role`: `none`(死が扱われない) / `背景`(死が過去の出来事・設定
  として存在するが、物語の中心的葛藤ではない) / `中心`(死・殺人が物語の
  中心的な謎・葛藤・結末を構成する)。

**タグ付け対象**: Core Provocation候補(1-3案×5 Run、想定最大15案)、
Story本文(5本)。各対象に対し上記2タグを付与し、以下の対応表を作る。

- E値(Run全体、候補ごとではなくRunのDNA)
- E軸の有無(Run2はE軸なし)
- 他軸(特にB=感情トーン)
- `why_interesting`/`reason_for_choice`内の語(tension/danger/kill/death/
  threat等の部分文字列マッチ、大文字小文字無視)の有無

**注意**: 本Trialは相関の記述(観察)のみを行い、「Eが非現実系だから殺人に
偏った」等の**因果を断定しない**(委任文どおり)。サンプル数(候補15・
Story5)は統計的検定に耐える規模ではない。

## 比較対象

前回Bias除去Trial(FICTION-CORE-PROVOCATION-PROMPT-BIAS-RETRIAL-01、旧E軸)
の5本(`er018_output/fiction_core_provocation_prompt_bias_retrial_01/`)を
read-onlyで参照し、violence/death_roleタグを同じ基準で付け直して比較する
(旧Trialのタグ付けは本Trialのviolence_death_tags.mdに追記する形で実施)。
