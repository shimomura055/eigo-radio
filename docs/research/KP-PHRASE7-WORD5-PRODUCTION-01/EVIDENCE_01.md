# EVIDENCE_01: KP 7+5分離抽出のProduction配線 6経路runtime evidence(KP-PHRASE7-WORD5-PRODUCTION-01 委任_02、2026-10-27)
到達Status=**IMPLEMENTED + EVIDENCE_COLLECTED**(PRODUCTION_WIRED判定はFable)。生データ=`evidence_01.json`(`tools/collect_evidence_75.py`が実runの`kp_candidates.json`・usage logから集計、読取りのみ)。費用=`COST_01.md`。
実行: 各経路のKP stageのみを、入力のみコピーした新規run dir`run_kp75_ev_01`で実API実行(公開・進行中runは無触、`--regenerate-stage kp`不使用)。X=`er019 runner --scaffold-only kp`、Y=`er121 runner --stages kp`、Z=`er026 runner --stage kp`。全4プロセス正常終了(rc=4=HR待ち=想定通り)。TTS_EXECUTION_MODE=STANDARD。使用モデル=`gpt-6-luna`(現行Production KP line。最新世代の開発評価ルール25節は本番ライン選定対象外=モデル非変更)。

## 1. 6経路 結果表(Std=a2 / Adv=b1b)
Std/Advは同一記事・同一run内の2 level(a2=Std、b1b=Adv)。Xは2記事(UK列車・AI島)、Y=再配達、Z=走れメロス → 8 doc(=X2記事×2 level + Y2 + Z2)=**6経路(X/Y/Z×Std/Adv)をすべて通過**。
| 経路 | level | 件数 phrase+word | origin call1/call2/backfill | P7返却件数 | call1_attempts | outer | 補完 | drop | 判定 |
|---|---|---|---|---|---|---|---|---|---|
| X UK | Std a2 | 3+5=8 | 3/5/0 | 3 | 1 | 1 | 未発火(E=0) | 0 | PASS |
| X UK | Adv b1b | 7+5=12 | 7/5/0 | 7 | 2 | 1 | 未発火 | 0 | PASS(上限12到達) |
| X AI島 | Std a2 | 5+5=10 | 5/5/0 | 5 | 1 | 1 | 未発火 | 0 | PASS |
| X AI島 | Adv b1b | 5+5=10 | 5/5/0 | 5 | 1 | 1 | 未発火 | 0 | PASS |
| Y 再配達 | Std a2 | 5+3=8 | 5/2/1 | 5 | 2 | 1 | **単語補完OK**(cmu 1件E→+1) | cmu 1 | PASS |
| Y 再配達 | Adv b1b | 6+4=10 | 6/3/1 | 6 | 2 | 1 | **単語補完OK**(cmu 1件E→+1) | cmu 1 | PASS |
| Z メロス | Std a2 | 4+4=8 | 4/4/0 | 4 | 1 | 1 | 未発火 | 0 | PASS |
| Z メロス | Adv b1b | 4+5=9 | 4/5/0 | 4 | 1 | 1 | 未発火 | 0 | PASS |
判定基準(DESIGN_02 §6): 全8docで(1)フレーズ<=7・単語<=5・合計<=12、(2)単語がフレーズに含まれない(選定表層形・used_form token一致の両方で0件)、(3)prompt_ids=`kp_prompt_p7`/`kp_prompt_w5p`・sha=P7`2e930193…`/W5'`12d33708…`・model=`gpt-6-luna`、(4)P7が1語を返した件数=0、(5)`overflow_kind`=0・`not_single_word`=0・`duplicate_of_top3`=0、(6)理由40字超=0件(最長34字)、(7)AUTO選定は無変更(auto_select=先頭3/Adv vocab5のまま=D2。`auto_eligible`は11/12(X UK Adv)以外は全候補)。
- **フレーズ補完**: 全runでEにphraseが無く未発火=**real未観測**(unit/golden_03/E2E testで確認済み。natural firingは今回起きず、replayは追加費用に見合う独立知見が無く未実施=必要十分で停止)。単語補完は自然発火2件で、`prompts.phrase.status=SKIPPED`・`prompts.word`(W5' sha)=OK・quota_word=1・added1件を実run確認(M-1/M-3/M-7の実観測)。
- **再開(resume)**: X UK runを同一コマンドで1回再実行 → rc=4、raw_usage_log 13行→13行(API 0)、a2/b1bの`kp_candidates.json` sha256不変(`evidence_runs/resume_before.txt`/`resume_after.txt`)。

## 2. 観測(R-1/R-4/R-6)
- **R-1(語形違いの含有、used_formレベル)**: 単語⊂フレーズ=**0件/8doc**(選定表層形・used_form token一致の両方)。W5'の「KP含有語は除外」の指示と`duplicate_of_top3`は今回すべて機能(発生頻度は低いが0件は実測)。母数8docでの観測であり、語形違い(price/prices等)の取りこぼしがゼロである保証ではない(既知の限界として維持)。
- **R-6**: `duplicate_of_top3`のE算入=0件(単語補完の2件はいずれも`cmu`=発音辞書未登録語`redelivery`/`redeliveries`)。含有語漏れによる単語補完は観測されず。
- **R-4**: `call1_attempts`=1(5doc)/2(3doc: X UK Adv、Y Std、Y Adv)。2は機械診断noteによる全件再選定(件数不足ではなく不適合item由来、承認済みcall1のattempt loop)。`outer_attempts`=全8docで1。
- **P7の返却件数は3〜7件(平均約5)**: 「最大7」仕様どおり少数精選もあり得る。7件到達=X UK Adv 1docのみ。Std(a2)は合計8〜10件で、旧3+5の8件と同数以上。
- **品質上の観察(記録のみ・不具合判定はしない)**: X UK Adv「forced to log in | 無理やり聞かされる」はglossが句と対応しない(gloss整合は既存の`kp_gloss_alignment`段の責務で本件の変更範囲外)。`Strategy`/`Silence`の語頭大文字は従来から。新規の規則追加はしない。

## 3. 実候補の例(実run、full一覧は`evidence_01.json`)
- X UK Adv(12件): draw a line(はっきり区別する)/a blanket ban on sound(音を全面的に禁止すること)/written permission(書面での許可)/reach for one's wallet(自分の財布に手を伸ばす)/up to(最大で)… + 単語 masterpiece(傑作)/automatically(自動的に)/nationwide(全国規模の)/exception(例外)/urging(強く勧める)
- X AI島 Std(10件): make a difference(影響を与える)/carry over(持ち越す)/take a detour(寄り道をする)/card to play(使える手)/worth paying attention to(注目する価値がある) + 単語 separately/obstacle/feature/Strategy/setup
- Y Adv(10件): sit right with someone/can't be helped(仕方がない)/take the trouble/end up receiving/on top of/head off + 単語 beforehand(事前に)/repeatedly(何度も)/errand(ちょっとした用事)+補完 encourage(促す)
- Z Adv(9件): sentence someone to death(人に死刑を言い渡す)/pull someone under/hold out one's hands/earn such trust + 単語 abandon(見捨てる)/execution(処刑)/seize(捕らえる)/stain/obey

## 4. 未達・限界(隠さず記録)
(a) フレーズ補完のreal発火は未観測、(b) 4プロセス並列実行のため所要時間は直接比較できない(COST_01.md)、(c) R-1は8docの観測でゼロ、(d) AUTO選定/形側はD2・委任_03どおり未変更。
