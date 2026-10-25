# 委任文(Fable→sonnet-worker)
管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_09(Trial-04: Opus条件A必須修正M1・M2+推奨R1〜R5の反映→事前登録基準commit→有料生成[3作品×N=2、α主+β比較、Step A追加標本]→評価→Fable評価用整理。上限20円)
前提: 委任_08(DESIGN_04.md、PROMPT_04.md、run_trial_04.py、commit 88104d77a)。**Fable判断: Opusレビューは設計骨格を妥当とし軽微な必須修正2件。設計と実質一致・新仕様採用なし・予算内→修正反映後に有料生成へ進んでよい(Fable Go)。Production採用は含まない。**

## 0. 最初に
- `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/OPUS_REVIEW_02.md` に§1のOpusレビュー全文を保存(先頭に「Fable転記、2026-10-25、条件A」)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 513 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_09.md`。冒頭が「管理ID: FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_09」と一致するか確認、不一致なら index 511〜516 を順に試す(`--index -1`不可)。

## 1. Opusレビュー全文(逐語)
```
## 判定: 必須修正あり(軽微)
2点(M1・M2)を直せば、有料Trial-04(約3.5〜5.1円)へ進んでよいと考えます。設計の骨格(P1を本文背景なしの別LLMにする/Step AとStep Bの分離/03dのPart 3/4ブロックを流用/Validatorを新設しない)は妥当で、見直しは不要です。修正はPhase 0の範囲内で終わる大きさなので、同じ内容での再レビューは要らないと判断します。

## 必須修正
**M1. Step Aが返す英文を本文の文字列に確実に一致させる(固定処理で)**
- 根拠: `assemble_user`はStep Aの`sentence`をそのまま「対象となる本文英文」として表示し、Step Bもそれを逐語引用の元にします。
- ところが`parse_stepa`は逐語一致を確かめていません。本文は曲がったアポストロフィ(’)を使っているため(例: Jim’s、moment’s)、LLMが'に置き換えたり細部を言い換えたりすると、本文と違う英文が「本文英文」として表示されます。
- 評価時の`check_quotes_04`では見つかりますが、その時点でRunは無駄になっています。
- 修正案: `para`で該当段落を特定し、引用符やアポストロフィの違いを揃えたうえで文単位に照合し、表示とStep B入力には本文側の文字列を差し替えて使う。見つからなければ現行どおり例外で停止する。
- 位置づけ: 構造上の保証であり、Checkerの新設ではありません。`run_trial_03`の`assert s in text`と同じ種類の処理です。

**M2. 有料生成の前に、事前登録の判定基準を明確にする**
- (i) αとβの「矛盾」の定義を決める。
  - 矛盾とする: 「語義不一致」。本文中の意味を否定する、または別の語義・別の構文だけを解説して本文の語義に触れない場合。
  - 矛盾としない: 「強調点の差」。
  - 例: `at a moment’s notice`のgloss「急なことにも即座に」は即応性に寄っています。αが核の意味として「予告がほとんどない」を説明した場合、これはユーザーが求めている改善そのものなので、矛盾に数えてはいけません。この定義がないと、αが不当に不利になります。
- (ii) 判定ルールが片側しか見ていない。現行の「αで矛盾が1件以上ならβ」は、βの失敗(本文の意味に引きずられる)を考慮していません。
  - 修正案: 「αに語義不一致があり、かつβが同じKPで評価観点①(核の意味から説明しているか)を後退させない場合に限りβ」とする。
  - この例ではβが不利になると予測できます。上のglossがそのまま即応性の方向へ誘導するからです。
- (iii) `bound to the protein`は高リスクと予測される項目として、事前に別扱いを登録する。
  - αでは英語表現しか渡らないため、「be bound to do(きっと〜する)」の語義に流れる可能性が高いです。
  - 原因の多くは、KPが慣用句でなく単語の組み合わせであることです(KPの選定はScope外)。このKPは集計を分けて報告し、αとβの判定を1件だけで左右させない、と先に決めておきます。
- (iv) Part 2の合格条件を数値で先に固定する。
  - 6セットすべてで開発者向けの語が0件。
  - 基礎文法だけの選定が0件。
  - 『賢者』は後置修飾(P4)か倒置(P22/P30)を選ぶ。P30を選んだ場合は、説明の中心が倒置で、whoseが従になっていること。
  - イグ・ノーベル賞と開いた窓の「安定」を定義する。0件かどうかの判断が一致し、選定がある場合は同じ文か、両方とも価値基準を満たす文であること。
- これがないと、Trial終了の判断(§7「成立したら終了」)が後付けになります。

## 推奨(任意、強い順)
- **R1. Step Bに渡す文脈を、本文の前後の文に替えるか追加する**: Step Aが書く`context_ja`(LLM生成の1文)の代わりに、または加えて、選定文の前後1文か同じ段落を、本文から逐語でそのまま渡す。理由1: "One was…"のように前の文を参照する文は、訳すのに前の文が必要。理由2: Before(03d)は本文全体を見て表現効果を書いていたので、1文のメモだけでは「意味・ニュアンス・表現効果」で後退するおそれ。理由3: `context_ja`自体に誤りや解釈が入る経路もなくなる。本文背景を遮断するというユーザー要件はPart 1についてのものなので、Step Bに局所的な文脈を渡しても趣旨と矛盾しない。
- **R2. Part 1の解説文をPart 3/4にも入力する**: 処理時間は増えず、費用増は約0.02円。03dではPart 3がPart 1と同じcallで生成されていたので、Part 1の内容を知っていた。渡す方がBeforeの条件に近い。Part 3/4のブロック本文は変えず、入力欄を足すだけ。
- **R3. Step Aの`construct_ja`・`points_ja`・`context_ja`は「文の内容」として書かせる**: Step Bへ開発者向けの情報が漏れる経路として残る3欄。Step A Promptに1行追加「これらはユーザー向け解説の材料なので、文の内容として書き、難易度や誤解しやすさなどの評価語を入れない」。
- **R4. 同じ英文に2つの訳が並ぶのを防ぐ**: 選定文がKPの文と一致した場合は、固定訳を「参考訳」としてStep Bへ渡す。
- **R5. 選定判断の再現性は、Step Aだけを追加で回して確かめる**: 各作品でStep Aだけを+2回(約1.2円)実行し、0件判断と選定文をN=4で観察。βも2回目(r2)を回す(+約0.5円)。

## Trial構成・費用への意見
- 約0.5〜0.76円/記事セットは70円の約1%で見合う。バッチ生成なので45〜70秒はクリティカルパスにならない。並列化設計は適切。Part 3/4をStep Aと同じcallにまとめない判断は妥当。R5とR2を足しても合計約6〜7円で上限20円内。
- N=2: 食い違えば不安定の証拠、一致しても安定とは言えない(弱い傍証)。統計的安定性は主張しない。

## 論点(c)・(d)の確認
- Production `japanese_gloss`は本文で使われている語義を表す設計(`er003_key_words_gloss_alignment.py:149,156`)。項目2の確定値として整合。`meaning_in_text_en`を別LLMに渡さない判断も正しい。
- 配線位置: Part 1はKP確定後、Step A/B・P34は本文最終確定後。本文をregen/Local Rewriteで作り直した場合は学習テキストも作り直し。
- 将来の課題: 項目4の英文日本語訳はProductionに出所がない(今回は03dの値を固定流用)。配線時は生成元を別途設計。

## リスクと対処
- αが「本文に引っ張られる」問題を解消しない可能性: `at a moment’s notice`の即応性偏りはモデルの知識由来かもしれない。αでも再現した場合は、原因が入力切り分けではないと判断し、βやPrompt微調整の反復ではなく設計見直しへ回すよう事前に決めておく。
- parse失敗時に自動再試行しない設計はTrialでは妥当。Productionでは既存retry方針との整合を別途設計。
- Part 3/4ブロック一致のassertは範囲が正しく、03dと一字一句一致の主張は成立。
- Validator新設なし。parseのassertとdry-runの混入確認のみでユーザー方針と矛盾しない。

## ユーザー判断が必要になりうる論点(今回のTrial実施には不要)
- Production `japanese_gloss`の質(例: `at a moment’s notice`「急なことにも即座に」は核の意味からずれ)。glossの修正はProduction KP工程の変更でユーザー承認が必要。
- Production配線、および項目4(日本語訳)の生成元。
```

## 2. Fable判断(反映指示)
- M1・M2: 必須反映。M2の事前登録は `PREREGISTERED_CRITERIA_04.md` として**生成前にcommit**(矛盾の定義=語義不一致のみ、α→β切替条件は両側条件、`bound to the protein`は別集計、Part 2合格条件を数値で固定、「αでも本文引っ張りが再現したら設計見直しへ回しPrompt微調整を反復しない」を明記)。
- R1〜R5: すべて採用(R1はcontext_jaに加えて前後1文の逐語を渡す。R5はStep A+2回/作品、β r2)。
- 生成構成: 3作品×N=2(α腕フル)+β腕P1×2(r1/r2)+Step A追加×2/作品。見積約6〜7円、上限20円。各launch前にSTOP確認(`tools/stop_scope_check_01.py`)と残額比較。モデル=gpt-6-luna固定。
- 評価: ユーザー原文§6の観点でBefore(03d)と比較、`EVAL_04.md`(開発者向け)。学習者向け完成形は `OUTPUT_04_<work>_r1_USER.md`(Part 1〜4)、開発者向けは `OUTPUT_04_<work>_r1_DEV.md`(Step A JSON・候補・reason_dev・usage)。`COMPARISON_04.md`(3作品のBefore 03d/After 04 r1のPart 1・2を並べる、無編集)。引用逐語照合(`check_quotes_04.py`)。
- 改善が事前登録基準を満たせば追加の磨き込みはしない。満たさない場合は原因を分析し、設計の見直し(入力・責務の再配置)が必要なら実装せずFableへ報告(Prompt微調整の反復禁止)。

## 3. 文書・SSOT・Git・報告
- `BUDGET_LOG_01.md`更新(Trial-04実費、量産費用/記事セットをTrial-03と比較、呼出回数・処理時間)。`ADOPTION_NOTE_04.md`(採用時の配線位置・依存関係[本文regen時の再生成]・項目4日本語訳の生成元課題・gloss品質の論点[ユーザー判断候補])。
- SSOT: OPEN-497 Status更新(`TRIAL04_DONE_PENDING_FABLE_EVAL`等)、`DECISION_LOG.md` 1件、`docs/pm/ACTIVE_TASK.md` 該当行。SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認。`py`使用。
- Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。事前登録は生成前に別commit。
- 報告 `docs/pm/RESULT_PACKET_FZST9.md`: ①M1/M2/R1〜R5反映、②生成記録(call数・実費・時間)、③Part 1評価(α/β、KP別、矛盾の有無、`bound to`別集計)、④Part 2評価(Step A選定の安定性N=4、選定文、Step B品質、開発者語混入0件確認)、⑤Before/After比較と以前の問題(nutrient-rich/give way/at a moment's notice/基礎文法選定/開発者情報混入)の改善具体例、⑥Part 3/4影響、⑦費用・時間・量産単価比較、⑧Status候補(Sonnet所見)、⑨ユーザー判断候補(gloss品質・配線・項目4訳の生成元)、⑩変更ファイル・commit、⑪`check_delegation_prompt.py`結果、⑫問題点。raw URL(COMPARISON_04.md、EVAL_04.md、OUTPUT_04_*_r1_USER.md 3件)。

## 4. 禁止
Production code/Prompt/flag変更、KP追加選定・gloss変更、音声生成、Web検索、出力の編集、Part 3/4ブロック本文の変更、Checker/Validator新設、上限20円超過、`.venv\Scripts\python.exe`以外の使用、自PID以外のprocess終了。Trial成功でもProduction配線へ進まない。