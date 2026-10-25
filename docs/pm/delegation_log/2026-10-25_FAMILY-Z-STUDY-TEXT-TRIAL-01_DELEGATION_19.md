FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_19(API 0・小タスク): Part 2 Trial-08 のFable独立評価を成果物へ転記し、Statusを確定反映する。Production file変更禁止。

## 転記するFable独立評価(2026-10-25、そのまま `docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/PART2_TRIAL08_RESULTS_01.md` §4「Fable独立評価」へ記入。文言は整えてよいが判断内容は変えない)
- 総合: **VALIDATED(限定)**。目的(倒置偏りの低減と学習価値の維持・向上の判断材料)は達成。倒置を一律除外せず、他に適格候補のない作品(賢者の贈り物・告げ口心臓r2)では倒置を残しており、方式はユーザー仕様どおりに動作。
- 作品別: 開いた窓=同等(長い動名詞句主語は論説・ニュースにも転用できる型で、場所句倒置と価値は同程度。文が短く基礎項目との境界に近い点はSonnet所見に同意)/猿の手=同等〜やや良い(「Then came a soft knock.」は学習価値が小さく、置き換え自体は妥当。ただし選ばれた`Wish him alive again!`は命令文の断片で、同型の平叙文`I wish Herbert alive again.`(P22)の方が教材として自然。Tier内の順位が段落番号順(Trial-07規則維持)のためで、方式の欠陥ではなく順位規則の改善候補)/告げ口心臓=明確に改善(主語と動詞の間に挿入句が入る文の読み方は再利用性が高い)/賢者の贈り物=倒置残存は妥当(P22は目的格関係詞省略も含み価値が高い。P4の分詞後置修飾はLOW判定でも致命的な見落としではない)/イグ・退屈・二十年後=変更なしで妥当/走れメロス=Trial-07の事前登録(許容集合∅)を継承し合否に含めない扱いは正しい。
- リスク(方式固有ではなくTrial-07適格条件に内在): 学習価値HIGH判定の標本ばらつきにより、低価値な非倒置(Like A, B型・同格)が倒置に優先される標本が存在(旧賢者r3・猿r2)。正式採用時は、Tier内順位(平叙文・完全文を優先、段落番号順は最後)と、HIGH判定の安定化(判定2回一致等)を配線設計で検討する価値がある=仕様候補(ユーザー判断)。
- 量産単価影響ほぼ0(約0.41円/set不変)。実費3.58円。
- Production採用・配線は未承認(Status=VALIDATED(限定)、APPROVED_FOR_PRODUCTIONではない)。

## 反映
1. 上記を `PART2_TRIAL08_RESULTS_01.md` §4 と §7(Status=VALIDATED(限定)・Fable確定)に反映。§8のユーザー判断候補はそのまま。
2. `ADOPTION_NOTE_08.md` 末尾にStatus行(VALIDATED(限定)、Fable受入2026-10-25 委任_19、Production未配線)。
3. `OPEN_ITEMS.md` OPEN-497 行の Trial-08 記述を Status=VALIDATED(限定) に更新(直前再Read・最小Edit・バックアップ・`git diff --stat`。並行agentが編集中)。
4. `docs/pm/ACTIVE_TASK.md` 更新(gitignore)。
5. 委任文逐語: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_19.md`(N=566前後±8、冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_19」で照合。`--index -1`不可)。
6. Git: `git add -A/-u/-f`、amend/rebase/force push/stash/clean/reset/checkout -f/`git checkout -- <file>`禁止。対象pathのみ `git commit --only -- <paths>`→`git push origin HEAD:main`。non-fast-forwardなら `git fetch`→`git merge --no-edit origin/main`(競合は両方残す)→push。secret grep 0件。
報告: 変更ファイル・commit hash・raw URL(RESULTS_01)。