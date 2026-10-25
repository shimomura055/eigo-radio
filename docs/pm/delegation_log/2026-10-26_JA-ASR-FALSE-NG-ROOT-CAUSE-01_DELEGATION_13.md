# 委任_13｜JA-ASR-FALSE-NG-ROOT-CAUSE-01 便乗PASS是正E4と、E3副作用の整合化E4-Nの設計・API 0評価・適用計画(Production適用はしない)

## 背景(Fableから)
- 委任_12(commit `7953f5969`、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN333_{DESIGN_02,EVAL_02,APPLY_RESULT_01,PREREGISTERED_02}.md`、`docs/pm/RESULT_PACKET_JAASR12.md`)でE3(P-1なし、値ガード多層防御つき)をProduction適用済み(`er011_ja_asr_variant_layer_01.py` 定数 `CANDIDATE_E_FULL_DIFF_CHECK`/`CANDIDATE_E_VALUE_GUARD_CHECK`)。
- 残り2点をFableが次のように判断した:
  1. **E4(便乗PASS)**: 承認済み安全条件「entity_like/濁点差はCascade(Azure再確認)へ」をCandidate Eが迂回している不具合。合成負例87%(96/110)が現行PASS、実データでも『走れメロス→走レメラス』型が通る。Opus(条件C、`OPUS_REVIEW_01_OPEN333.md` 論点5/R-4)は「E3と同程度に優先度の高い不具合」。→ **適用方向で設計を確定する**(本委任で設計・評価・適用計画まで。適用はOpusの短い確認後に別委任)。
  2. **E4-N(E3の副作用の整合化)**: E3適用後、数値entryで糊付け残余が正常な等価表記(ヴェ↔ベ、muse→ミューズ 等)の場合に、非数値entryならCascade行きのところ即NG(再生成)になる不整合(Opus論点2-3、委任_12 §3「合成25件中24件が再生成」、実データ0件)。→ 承認済み仕様(非数値entryと同じCascade扱い)へ揃える案を設計・評価する。**PASSを広げる変更は不可**(拒否→Cascadeへの振替のみ。Cascade側はAzureの正規判定)。
- 参照: `OPUS_REVIEW_01_OPEN333.md`(論点2・5・6)、`proto_open333_fix_05.py`(E3v3+E4)、`eval_open333_api0_0{4,5}.py`、`eval_open333_prod_parity_01.py`、Production `er011_ja_asr_variant_layer_01.py`・`er007_ja_asr_validator_01.py`・`er007_ja_secondary_asr_01.py`(644)・`er078_asr_unified_judge_01.py`(Cascade/P3の入口)・`er078_asr_value_guard_01.py`。
- 並行agent: KP HR 委任_05(er119/er120/er019/er026/er062・OPEN-518/519/484)、Family Y(er121・OPEN-520)。触らない。本委任の所有: `docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/` 新規ファイル、OPEN-333行の最小追記のみ。**Productionファイルは編集しない**。

## やること(API 0・実費0円)
1. **Cascade振替の実現可否**: Candidate Eの分岐(`return None`→TRUE_CONTENT_MISMATCH)から、「entity_like/濁点差/等価表記候補」をCascade(Azure再確認)へ渡す既存経路が存在するか(er007の `cascade`/`entity_like` 判定、er078のP3入口)を読み、E4/E4-Nが**既存のCascade分類に差分を戻すだけ**で実現できるか、新しい分岐が要るかを設計(`OPEN333_E4_DESIGN_01.md`)。新しい受理クラスは作らない。Cascadeへ回した後の判定は既存のまま。
2. **事前登録**(`OPEN333_E4_PREREGISTERED_01.md`): 基準=非PASS→PASS 0(PASS集合は広がらない。Cascade行き件数は別集計)、固有名詞負例(合成110+実データ)のPASS 0、正常等価表記のCascade行き率、ひらがなのみ濁点差の負例(未検証だったもの)を追加、E3適用後HEADとの差分種別(PASS→Cascade/拒否→Cascade/不変)を全件。
3. **評価**: `proto_open333_fix_06.py`(E3v3+E4+E4-N)と `proto_open333_fix_05.py`(E3v3+E4)を、実データ1,327行+Secondary対+sweep全部+E4負例/cost/ctrlで、現行HEAD(E3適用済み)と比較(`eval_open333_api0_06.py` → `OPEN333_E4_EVAL_01.md`+json、2回実行で決定性)。Cascade結果はAPI 0ではstubになるため、「Cascade行き」件数と、その中で保存Secondary転写がある行については保存転写で判定した結果を併記。
4. **QCD**: Cascade増分(件数×約0.267円)、再生成減(E4-Nで救われる数値entryの等価表記)、品質(固有名詞読み違いの遮断)。E4のみ/E4+E4-Nの2案で表にする。
5. **適用計画**(`OPEN333_E4_APPLY_PLAN_01.md`): 変更箇所(行数)、rollback定数名(既定ON、env/flag不可)、fail-closed、M-6同様の監視field、proto↔Production一致(全キー)、回帰、保存転写注入による発火確認、SSOT。Opus短縮レビュー向けの論点(`OPUS_REVIEW_REQUEST_02_OPEN333_E4.md`、3〜5論点)。
6. OPEN-333行に1文追記。Git: 対象pathのみ `git commit --only` → `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。secret grep 0件。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_13.md`(直近既知index=607。608以降を試し、先頭行が「# 委任_13｜JA-ASR-FALSE-NG-ROOT-CAUSE-01」のものだけ採用)。

## 報告(`docs/pm/RESULT_PACKET_JAASR13.md`+最終報告)
1. Cascade振替の設計(既存経路の再利用か新分岐か) 2. 評価表(HEAD vs E4 vs E4+E4-N: 非PASS→PASS/PASS→Cascade/拒否→Cascade/固有名詞負例PASS/等価表記Cascade率) 3. QCD 2案 4. 適用計画の要点とOpus論点 5. commit sha・raw URL 6. RESULT_PACKET 4行+判定整合行 7. 推奨(E4のみ/E4+E4-N/見送り)と理由。事実と推測を分ける。