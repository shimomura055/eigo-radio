FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_09-FABLE-BLIND-RESULT-RECORD-AND-UDR-20261023

# 記録のみ(API 0・コード変更0)。Fable盲検判定の保存、OPEN-474のStatus更新、UDR登録、Git。

## 0. 読むもの
`docs/pm/ACTIVE_TASK.md`(line 2 Git注意、KP行)、`docs/pm/RESULT_PACKET_KPGM8.md`、`er112_output/kp_gm_trial_03/fable_blind_std_03.md`、`fable_blind_std_03_key.json`、`docs/pm/USER_DECISION_REGISTER_01.md`(最新番号の確認。前回はUDR #170=Family Y)。

## 1. Fable盲検判定(key開封前に判定、開封後に帰属。これを逐語で `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_03/FABLE_BLIND_RESULT_03.md` に保存)
判定基準: GOLD_LABELS_FINAL_01(難例)、本文用法とフレーズ全体の意味(通常)。PASS以外のセルのみ列挙(他は全てPASS)。
FAIL:
- #1 apply one's findings F「人の研究結果を当てはめる」= G3/rep1(itsは自分の。所有者誤り)
- #5 draw a line D「はっきりと線を引く」= G2/rep2(字義)
- #15 reach for someone's wallet D「人の財布に手を伸ばす」= G0/rep1、E「誰かの財布に手を伸ばす」= G3/rep1(盗む読み)
- #23 an unseen clock B・D「目に見えない時計」= G0/rep1・G0/rep2(字義)
- #50 settle at F「～で落ち着く」= G0/rep2(市場用語「取引を終える」が落ちる。△〜FAILの境界、FAIL寄り)
△(薄い・含意欠落、誤りではない):
- #2 brace yourself for A「～に備える」= G3/rep2
- #13 on the throne E「トップの座にいて」= G3/rep2
- #15 reach for someone's wallet A「人が支払いを覚悟する」= G2/rep2(動作が消え意訳)
- #44 price tag E「値札に表示された価格」= G2/rep1
- #54 standard deviation A= G2/rep2、E= G3/rep2、F= G3/rep1(「標準偏差」の定訳でなく説明文)
集計(各arm 120出力): FAIL G0=3(+境界1)、G2=1、G3=2。△ G0=0、G2=3、G3=4。KP単位でFAILを含むKP: G0=3 KP(reach、unseen clock、settle at)、G2=1 KP(draw a line)、G3=2 KP(apply、reach)。
draw a line(Trial_02+03合算、5出力ずつ): 字義 G0 2/5、G2 1/5、G3 0/5。本Trialでは G0 2/2 慣用義。
Fable結論: (1)誤り率は全armとも1〜3%で同等域、G2/G3が現行を系統的に上回るとは言えない(Trial_02のG3優位は小標本・確率的)。(2)現行G0の誤りは「比喩表現の字義訳」型に偏る(unseen clock、線を引く、人の財布)。G2/G3は字義訳を減らすが、所有者誤り・薄化・用語の説明文化という別の劣化を出す。(3)ユーザー要求「慣用表現の中心義を安定生成」はPrompt文言の変更だけでは到達しない(確率的失敗が残る)。安定化には、Std glossの用法(字義/比喩)をAdv説明(E0は難例59/60で用法正解)と突き合わせ、不一致時にStdだけ再生成する「用法整合チェック」のような工程の追加が必要で、これは新工程=ユーザー判断事項。(4)Adv説明Promptは現行維持で十分(Opus盲検・Trial_03 E0引き継ぎ0件・矛盾0件)。(5)A-1(一般化)は採用済みで配線待ち。

## 2. 更新
- OPEN-474: Status=`USER_DECISION_REQUIRED(UDR #<次番号>)`。要約: Trial_01〜03・Opus条件A・Opus盲検・Fable盲検の結論(上記)、選択肢(a)G3採用+A-1配線 (b)G0維持+A-1のみ配線 (c)用法整合チェック工程の設計・Opus条件A・Trial(上限50円)を承認し、(a)or(b)と並行、累計費用(Trial_01 69.0円+probe約1.4円+Trial_02 68.98円+Trial_03 30.12円=約169.5円、出典各BUDGET_LOG/paid_calls)、Production変更0。
- `docs/pm/USER_DECISION_REGISTER_01.md` に UDR #<次番号> を追加(件名: Key Phrase Std意味生成の採否と安定化工程の設計承認。選択肢(a)(b)(c)、Fable推奨=(a)+(c)[理由: (a)はユーザー指摘の字義化を減らし費用差+0.03円/call・規則変更不要、(c)が「安定」到達の唯一の見込み]、判断待ち)。
- ACTIVE_TASK KP行: Status=`USER_DECISION_REQUIRED(UDR #<次番号>)`、Trial_03 30.12円(上限30円を0.12円超過=Judge並列発行時のcap検査遅れ、記録済み)。
- DECISION_LOG: Fable判断1エントリ(Adv現行維持・Std採否はユーザー・盲検結果path)。
- 委任文逐語保存 `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_09.md`(抽出toolが無い場合は本委任文を手で逐語保存し、その旨末尾に注記)。
- Git: secret scan(`Glob **/secret_scan*`、無ければcached差分のkey/tokenパターンGrep 0件)→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。
## 3. 禁止
Production/er112コード変更0。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・一時index禁止。他agentの行(ACTIVE_TASK)を編集しない。完了したら使用したUDR番号・commit hash・pathのみ報告。

(注: 抽出toolが無いため、本委任文をSonnetが手で逐語保存した。先頭のsystem-reminder類は除く。)
