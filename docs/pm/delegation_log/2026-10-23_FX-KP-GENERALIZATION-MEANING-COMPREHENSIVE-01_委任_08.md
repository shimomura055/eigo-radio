FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_08-STD-G2-G3-CONFIRMATION-TRIAL-AND-RECORD-FIX-20261023

# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_08: (1)Opus盲検評価(OPUS_REVIEW_04)の反映・記録修正、(2)Std確認Trial(G0/G2/G3×2rep、新規通常KP約40+難例20、luna、≤30円)、(3)Std改善のみのX/Z配線設計更新(A-1同梱、Adv Prompt不変)、(4)ユーザー採否提案資料の準備。Production変更0、DEV er112のみ。

## 0. 先に読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(固定ヘッダ、line 2、KP行)、`.claude/agents/sonnet-worker.md`、`docs/pm/RESULT_PACKET_KPGM7.md`、`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{TRIAL_RESULT_02,DESIGN_04,WIRING_DESIGN_02,OPUS_REVIEW_03}.md`、`TRIAL_02/{GOLD_LABELS_DRAFT_01,REPRESENTATIVE_01,BUDGET_LOG_01}.md`、`er112_kp_gm_trial_02.py`/`er112_kp_gm_kpset_02.py`、ユーザー原文 `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_03.md`、`er003_key_words_gloss_alignment.py:300-330,575-612`(承認済みgloss規則「目的語・補語・修飾語を含む全語反映」とmapping検査)。

## 1. Fable判断(Opus盲検評価を照合済み)
- **Fable確定gold(難例20)**: GOLD_LABELS_DRAFT_01を採用し、曖昧3件を確定: draw a line=「一線を引く/区別をはっきりさせる/線引きをする/境界をはっきりさせる」許容、「線を引く/境界線を引く」不可。Carry the Load=字義・比喩とも許容(比喩含意を含む方が上位)。take the wheel=Std「ハンドルを握る」許容、Adv "take control" 許容、Std/Adv矛盾に数えない。→ `TRIAL_02/GOLD_LABELS_FINAL_01.md` として保存(Fable確定2026-10-23と明記)。
- **Adv**: Opus盲検(確定gold)では難例で全armほぼ上限、E1/E1c/E4は新たな誤り(語義併記・weak link誤読・一般化しすぎ)を生む。**Adv Promptは現行E0のまま維持、Std改善のみで対応**と判断(Adv追加Trialは打ち切り。B仕様PROMPT_SHA256変更は不要)。現行の弱点(Std誤りがAdvへ伝染)はStd改善で構造的に解消(G3+E0@G3 矛盾0件)。
- **Std**: G2・G3とも難例の誤り(draw a line字義、reach for someone's wallet「人の財布」=盗む読み)を解消。G3は通常KPで系統的な薄化(5件)、G2は薄化少。→ 採用候補をG2/G3のどちらにするか、薄化率と反復安定性を小規模確認してからユーザー提案する(過剰な磨き込みではなく採否判断に必要十分な確認)。

## 2. 作業
### T-0 記録・予算(API 0)
- 委任文逐語保存(抽出tool、MARKER先頭一致、`..._委任_08.md`)。Opus盲検評価の全文は本委任文には含めないため、Fableが別途要点を下記§5に記す→ `OPUS_REVIEW_04.md` として保存。
- ACTIVE_TASK KP行: 委任_08 Status=`STD_CONFIRMATION_TRIAL_IN_PROGRESS`、上限30円、報告=`docs/pm/RESULT_PACKET_KPGM8.md`。当日累計を`daily_dev_cost_01`で確認(上限1,400円、他予約枠: Family Y 残334.25円、B工程15円)。累計24円到達で見込み再計算、30円超過見込みなら停止前にFableへ。
### T-1 記録修正(API 0)
- OF-KPGM-BE-01: `TRIAL_RESULT_02.md` の「draw a line Adv未達」等、gold確定前Sonnet基準の記述を、確定gold再集計(Opus盲検の集計: Adv難例 E0@G0 59/60, E0@G2 22/22, E0@G3 22/22, E1 58/60, E1c 21/22, E4 21/22、KP単位改善0/悪化0; Std G0 24/26, G2 26/26, G3 25〜26/26; 矛盾 G0+E0@G0 4件, G3+E0@G3 0件, G3+E4 0件)で追記修正(元記述は「gold確定前」と注記して残す)。
- OF-KPGM-BE-06の整合確認: 承認済みgloss規則「目的語・補語・修飾語を含む全語反映」およびmapping検査と、G2/G3出力(例: G3「財布に手を伸ばす」はsomeone'sを訳さない)の関係を分析。(a)規則文は新規生成項目にも適用されるか、(b)G2/G3採用時に規則文・検査の変更が必要か、(c)必要なら最小変更案と「ユーザー判断事項」としての整理。→ `RULE_CONSISTENCY_01.md`。
### T-2 Std確認Trial(≤30円、luna=gpt-6-luna、本番と同model)
- KP集合: **新規**通常KP約40(過去Trial_01/02で未使用の既存X/Z記事KPから、慣用句・句動詞・コロケーション・名詞句を混ぜる。X/Z比を記録)+難例20(確定gold)。
- arm: G0(現行)/G2(用法先決め)/G3(定訳・慣用句優先+自己選択)×**2rep**。新しいPrompt案は追加しない。
- 出力: `er112_output/kp_gm_trial_03/results.jsonl`、**Fable盲検用の1表** `fable_blind_std_03.md`(行=KP、列=A〜F[6出力=3arm×2rep、KPごとに列順をランダム化]、本文文を併記、arm/repの正体は `fable_blind_std_03_key.json` に分離)。Sonnet Judgeは参考値としてのみ別ファイルに出す(gold+薄化例[brace→「～に備える」、keep someone company→「人の相手をする」、a sense of occasion→「特別感」、behind the scenes→「見えないところで」、on the throne→「トップの座にいる」]を基準に、PASS/薄い(△)/FAIL の3値)。最終判定はFable盲検。
- 集計(key開封後、Sonnet参考値ベース): arm別 PASS/△/FAIL、G0対比のKP単位flip、rep間の自己一致率(同armのrep1/rep2が同一判定か)。
- 勝者候補(G2/G3)のgloss rep1で、通常KP40件にE0(現行Adv Prompt、DEV注入)を通し、Std誤りの引き継ぎ・Std/Adv用法矛盾件数を確認(+数円、上限内)。
### T-3 配線設計更新(API 0) → `WIRING_DESIGN_03.md`
- 変更範囲=**Std新規生成Prompt(er003 gloss生成の目標ブロック)のみ**+A-1(canonicalization規則5、Opus条件C must-fix W-01〜04反映済み設計)。Adv Prompt・schema・PROMPT_SHA256は不変。
- X/Z共通: 変更箇所file:line、flag/version、X `phrases_signature`・Z `sig_payload` がStd gloss変更時にAdv説明を再生成するか(gloss条件の有無を確認し、再生成されない経路があれば仕様ID/version追加の最小案)、Store reuse、retry/fallback、既存完成記事の扱い(次回runで再生成)、test計画、撤去対象(Trial-02逐語test等は対象外のはず→確認)、記事B(uk_train_speaker_playback)への反映手順(3 KP選び直しの可能性)。G2/G3どちらを採っても差分が小さいよう両案併記。
### T-4 報告・SSOT・Git
- `TRIAL_RESULT_03.md`(確認Trial結果、ユーザー検証項目1〜6対応、手段/目的の区別)。OPEN-474追記(Adv=現行維持の判断、Std=確認Trial結果、採否はユーザー)。CURRENT_SPEC変更0。
- Git: secret scan(`Glob **/secret_scan*`で実体を探す。無ければ`git diff --cached`をkey/tokenパターンでGrepし0件記録)→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。raw URL添付。
- 報告=`docs/pm/RESULT_PACKET_KPGM8.md`: (1)Fable盲検表のpath (2)Sonnet参考集計 (3)E0引き継ぎ確認 (4)規則整合(BE-06)結論 (5)配線設計要点・記事B手順 (6)費用出典付き・累計 (7)ユーザー採否提案の下書き(G2案/G3案の比較表: 難例改善・薄化率・自己一致率・費用差・規則変更要否)。使用model名・最新か。

## 3. 禁止・制約
Production code/Prompt/flag/閾値/golden変更0(er112とdocsのみ、E0注入はDEV `call_fn` 公開引数のみ)。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。PIDは自分のもののみ(26-6)。個別対策(draw a line few-shot等)禁止。上限30円無断超過禁止。`.venv\Scripts\python.exe`使用。秘密情報出力禁止。
## 4. handback
完了/予算警告/blocker/USER_DECISION_REQUIRED候補 のいずれかで。

## 5. Opus盲検評価(OPUS_REVIEW_04.md へ保存する要点。見出し「Opus任意レビュー(盲検品質評価) Trial_02 2026-10-23、API 0」)
- 結論: Std G3は現行G0より明確に要求品質に近い(難例の誤り2種を解消、難例悪化0)。ただし通常KPで系統的薄化(5件: ～に備える/特別感/人の相手をする/見えないところで/トップの座にいる)。G2は盲検26/26で同等以上かつ薄化少(Sonnet 85%は過小評価、pump one's fist G2「喜んで拳を突き上げる」は問題なし)。採用候補は条件付き(薄化率・G2/G3比較の確認後)。
- Adv: 確定goldで難例は全armほぼ上限(E0@G0 59/60, E0@G2 22/22, E0@G3 22/22, E1 58/60, E1c 21/22, E4 21/22)。KP単位改善0/悪化0。E0@G3=22/22・矛盾0で最も合理的。E1/E1cは語義併記(pull someone under)・weak link慣用義誤読、E4は一般化しすぎ(the moment the market moves→as soon as things start to change)。E4/E1へ変える価値なし。「現行E0+Std改善」を推奨。
- 記事B(draw that line): G0は2/3不合格+矛盾。G3+E0@G3は3/3(区別をはっきりさせる/make a clear difference between two things、境界をはっきりさせる/make clear where a limit or boundary is、一線を引く/set a clear limit between what is acceptable and what is not)、G2+E0@G2も3/3。
- Std/Adv用法矛盾: G0+E0@G0 4件、G3+E0@G3 0件、G3+E4 0件。
- 次の一手: Adv追加Trial打ち切り推奨。Std確認Trialを1回(新通常KP40+難例20、G0/G2/G3×2rep、約25円、判定はgold+薄化例でFable/Opus盲検)。
- 所見: BE-01[必須]TRIAL_RESULT_02:20「Adv未達」はgold確定前基準→再集計修正。BE-02[推奨]G3薄化率確認。BE-03[推奨]G2を比較対象に残す。BE-04[推奨]Advは現行E0+Std改善、E1/E1c/E4不採用。BE-05[推奨]Sonnet Std判定に揺れ(apply one's findings)、根拠はgold+Fable/Opus判定に。BE-06[推奨]「人の/誰かの財布」は承認済みgloss規則「全語反映」から誘発の可能性、G3はsomeone'sを訳さない→規則文・mapping検査との整合確認(原則8)。BE-07[情報]Stdは2rep以上で。BE-08[情報]"make a clear difference"はmake a differenceと混同の恐れ、distinctionが上位。BE-09[情報]盲検は部分的(E0行のgloss_in、初回Grepでdraw a lineのStd arm名が見えた等)。
