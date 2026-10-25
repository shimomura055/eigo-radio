FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_05(Fable受入前の確認、read-only中心、API 0、Production変更0、公開ファイル変更は原則なし)。あなたはsonnet-worker。

## 背景
委任_04(RESULT_PACKET_FZSE4.md、commits 53ce7b397/5f3e7dc15/d9ab57b9e)で案A配線と『告げ口心臓』run_sf_prod_02の再生成・公開差替えが完了し、Status候補=WIRED_PENDING_FABLE。Fable受入の前に次の3点を確認してほしい。

## 確認1(最重要): 公開Standardページの本文
`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/COMPARISON_03.md` 130行目に「Standard: 英文セル10件中 一人称(I/my/me)を含む=0件、聞き手(you)を含む=0件」とある。一方`run_sf_prod_02/writer/std.md`は明確に一人称(I=33, you=6)。原因を特定する:
- `user_test/family_z_tell_tale_heart_01/standard.html`(ローカル)と公開URL https://shimomura055.github.io/eigo-radio/user_test/family_z_tell_tale_heart_01/standard.html の両方を取得し、英文本文セル(本文パート。Preview/Comment/KP/In One Lineと区別)を抽出して、`run_sf_prod_02/writer/std.md`(またはstd_adjust後の最終Std本文)と段落単位で一致するか確認(語数・一人称/you件数・冒頭「You think I am mad」・結末「I killed him!」)。
- `audio_standard/`のmp3(ローカル)がrun_sf_prod_02のStd音声(assembly出力)とsha256一致するか、公開URLから取得したmp3ともsha一致するか(委任_04は55本一致と報告。Std分が含まれているかを明示)。
- index.htmlのStd/Adv切替リンクが正しいページを指すか。
- 結論: (a)COMPARISON_03のセル抽出の不具合(HTML構造差)で、公開Stdは正しい / (b)公開Stdが旧本文または別本文 / (c)その他。(b)なら**公開ファイルは触らず**即報告(Fable判断)。(a)ならCOMPARISON_03の該当節を正しい数値に修正(docsのみ)。

## 確認2: Std guardrail WARN `STD_AVG_SENT_LEN_NOT_SHORTER`(Std 8.39 vs Adv 5.55)
- 既存のStandard(A2)仕様(CURRENT_SPECのA2/Std guardrail節をGrep)で、このWARNの定義・failure閾値・過去作品での発生有無を確認。
- 新Std本文の平均文長・語彙水準(既存のA2検査指標があればその値)と、旧run_sf_prod_01 Stdの同指標を並べて提示。Fableがユーザーへ「Stdが十分平易か」を説明できる材料にする。判断・修正はしない。

## 確認3: 回帰testの他agent起因分類の再現
- 委任_04の`REGRESSION_01.md`で「他agent起因」とされたunittest failed 3/errors 1(er053/er095 isolation、er064、er003_test_bad)と pytest 11件(er103/er104/er109)について、**clean worktree**(`git worktree add <scratchpad>/wt_fzse5 HEAD`、終了後`git worktree remove`)で該当testのみ再実行し、PASS/FAILを表にする。clean worktreeでPASSなら「未commit DEVファイル起因」で確定、FAILなら原因(HEADに含まれるどのcommitか)を特定して報告(修正はしない)。
- 無料処理は`py`、必要なら`.venv\Scripts\python.exe`(API呼出なし)。他agentのprocessを終了しない。

## 記録
- 結果を`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/ACCEPTANCE_CHECK_01.md`に記録、`docs/pm/RESULT_PACKET_FZSE5.md`に報告、`docs/pm/ACTIVE_TASK.md`自行。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 532 --out docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_DELEGATION_05.md`(冒頭「FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_05」で照合、不一致なら±5)。
- Git: docs(ACCEPTANCE_CHECK_01、COMPARISON_03修正、delegation_log)のみ対象pathをadd→`git commit --only`→`git push origin HEAD:main`。`-A/-u/-f/-N`禁止。worktreeは必ず除去。

## 報告
(1)確認1の結論(a/b/c)と根拠(段落一致表、sha一致) (2)確認2の数値と既存仕様上の位置づけ (3)確認3の表 (4)変更ファイル・commit (5)「判定整合: 重大NG= / 主因= / 是正対象= / STOP理由= / 提示=」1行。