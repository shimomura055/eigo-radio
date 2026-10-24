# 委任文(Fable→sonnet-worker)
管理ID: PM-FABLE-EVAL-RECORD-2026-10-25 委任_01(2件のTrialのFable独立評価とUDR登録、API 0・コード変更0・Production変更0)

## A. FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01(OPEN-508)
`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/FABLE_EVAL_01.md` に以下を保存:
```
# FABLE_EVAL_01 — FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 Fable独立評価(2026-10-25、委任_02成果、API 0)
- 根本原因: R1/R2 Prompt固定文言 "in third person"(er062_family_z_writer_01.py:141)。1a対照実験で現行文言2/2反転・置換2/2維持=再現確認。副因=key_roles描画「名前を使わず役割で呼ぶ」が一人称作品で語り手を外から呼ばせた。構造根因=Seedの語り口がR0にしか渡らず、essentialsに語り口欄がなかった。
- 案A(narration_voice欄+Narration行+REVISE置換、Validator/追加LLM 0): 1b 2/2でAdv一人称維持(一人称語42/43、you 5/4)、Std人称一致、essentials欠落0。Fableが比較原稿(COMPARISON_01.md)を直接確認: 聞き手への語りかけ・自己陶酔・老人の恐怖を聞く心理・心臓音・自白・因果が保持され、現行Adv(三人称)との差は明確。テンポ維持(414語/文長6.3)。1c音声Gate PASS・HR Lock 0。Phase 2(賢者/開いた窓/猿の手)で人称不変・語り手介入誘発なし・語数文長±25%内・副作用なし。
- 事前基準未達=段落数2件(1b 17 vs 19〜25、猿の手40 vs 32)。完成版自体が工程間で±10揺れるためノイズ内とFable判断(基準は不変)。
- 費用108.81円/150円。量産増分=追加LLM 0、検出不能。
- Status(Fable): VALIDATED(Trial範囲、案A)。Production採用は含まない。
- 推奨: J1=案A採用、J2=採用後『告げ口心臓』Std/Adv正式再生成・差替え(現行公開版はAdv三人称NG・Std/Adv人称不一致)。採用時はOpus条件C→配線。
```
- `docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR 2件: (1)件名=Family Z 語り口保持 案AのProduction採用、選択肢(a)案A採用[推奨]/(b)文言置換のみ/(c)不採用、分類D、非blocking。(2)件名=『告げ口心臓』正式再生成・公開差替え(採用後、約40円)、選択肢(a)Std/Advとも再生成・差替え[推奨]/(b)Advのみ/(c)保留、分類D、非blocking。
- OPEN-508 Status=`VALIDATED(Fable 2026-10-25)_PENDING_USER_ADOPTION`、OPEN-503に「Trial VALIDATED、再生成はUDR待ち」を追記。`DECISION_LOG.md` 1件。

## B. FX-CORE-NUMERIC-RETENTION-TRIAL-01(OPEN-507)
`docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/FABLE_EVAL_01.md` に以下を保存:
```
# FABLE_EVAL_01 — FX-CORE-NUMERIC-RETENTION-TRIAL-01 Fable独立評価(2026-10-25、委任_01〜03成果、API 0)
- 根本原因: 数値脱落はR0(Writer初稿)の1段のみ(15 run/63中核数値の実測、R1/R2/英訳で脱落・追加0)。R0 Prompt「見方を一つ選び必要な事実だけ」+【中核数値】が重要度順でない許可リスト(3〜6個)。副因=範囲値「〜」が承認済み3規則間で衝突し、R1/R2が波ダッシュへ書き戻して記号QA STOP(Production既存欠陥→OPEN-509)。
- 方式(O3+O-1'+O-2'+保持Gate+新規数値検出+出力側範囲正規化、追加LLM 0): 月=v2 2/2で42〜46m全段保持・750m/周辺/新規数値0・期間情報(後期・開始時期未確定・総量でない)正確(Fableがv2s1本文を直接確認: 自然で読み物として成立、不要な数値なし)。コーヒー(比較が答え)=必要数2/2保持、O-2'が必要数を下げず。イグ・ノーベル=B3 Storylineに数値が入らずE=∅ 4/4、必要数『3倍超』がR0〜Adv全段で欠落(現行公開版には有り)→方式の適用範囲は「数値が問いの答えである記事型」に限られる。
- 「約4億年」の数値自体は標本により掲載/不掲載(v2s1は数値なしで前提・期間を言葉で正確に説明)。数値必須かはユーザー定義事項。
- 費用: 案件累計285.68円/300円(Phase 1 120.12[上限0.12円超過、再発防止=launch前残額比較]、1b 63.99、2 101.57)。量産増分=追加LLM 0、再実行0/8、点推定0円・保守的上限6〜7円/記事。
- Status(Fable): USER_DECISION_REQUIRED(数値が答えの記事型ではVALIDATED_LIMITED相当。Family X全体の目的[見出し数値型を含む]には未達。追加Trialは案件300円超のため事前承認要)。
- 推奨: 追加予算約80円でR5(B3のJSONに「読者が聞くべき答えの数値≤2」欄を追加、Storyline非依存)をイグ・ノーベル+月回帰で検証。限定採用(数値が答えの型のみ)は次善。
```
- `docs/pm/USER_DECISION_REGISTER_01.md` に新規UDR 1件: 件名=中核数値保持Trialの次工程(適用範囲とR5追加Trial)。選択肢(a)追加予算約80円でR5をイグ・ノーベル型+月回帰で検証[推奨]/(b)数値が答えの記事型に限定して採用判断へ(J1 B3追記v2・O-2'・保持Gate・新規数値検出)/(c)中止。付随確認=「約4億年前から」は数値として必須か(前提・期間の正確な説明で足りるか)/イグ・ノーベル『3倍超』のような見出し数値を「不可欠な数値」とみなすか(J5)。分類D、非blocking。OPEN-509(範囲値波ダッシュProduction欠陥)はUDR候補として件名のみ登録(修正はユーザー承認待ち)。
- OPEN-507 Status=`USER_DECISION_REQUIRED(Fable 2026-10-25、数値が答えの型=VALIDATED_LIMITED相当)`、OPEN-505(月の数値脱落)に接続追記。`DECISION_LOG.md` 1件。

## C. 共通
- `docs/pm/ACTIVE_TASK.md` 固定ヘッダ: 本日の各管理ID行(FX-PARAGRAPH-CHUNK/FX-CORE-NUMERIC/FZ-SOURCE-ESSENCE/FAMILY-Z-STUDY-TEXT)のStatusを最新(UDR番号付き)に更新、UDR-blocking=なし、当日費用=2026-10-25 各Trial実費合計(13.89+285.68+108.81+6.28=414.66円+本日他の小額)/1,000 を記載。他agentは現在実行中なし。
- SSOT編集前にscratchpadへバックアップ、編集後 `git diff --stat -- <file>` 確認(OPEN_ITEMS.mdはCRLF/LF混在、USER_DECISION_REGISTERはCRLF化事故の前例あり)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 510 --out docs/pm/delegation_log/2026-10-25_PM-FABLE-EVAL-RECORD-2026-10-25_DELEGATION_01.md`。冒頭が「管理ID: PM-FABLE-EVAL-RECORD-2026-10-25 委任_01」と一致するか確認、不一致なら index 508〜513 を順に試す(`--index -1`不可)。
- Git: `git status` → 対象pathのみ `git add`(禁止: `-A/-u/-f/-N`、amend、rebase、force push、stash、clean、reset --hard、checkout -f/`git checkout -- <file>`) → `git diff --cached --name-status`(意図外D/Aなし・secret 0件・Production file差分0) → `git commit --only -- <path…>` → `git push origin HEAD:main`。
- 報告 `docs/pm/RESULT_PACKET_PMFE1.md`: UDR番号、変更ファイル、commit hash、`check_delegation_prompt.py`結果、問題点。raw URL(FABLE_EVAL_01 2件)。