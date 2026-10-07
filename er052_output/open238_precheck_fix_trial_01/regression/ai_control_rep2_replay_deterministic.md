# ai_control p2 rep2 決定論再現(修正後 check_number_mismatch_v2 + 対象文特定、¥0、Stage 2以降のLLM再生は未実施)

入力: er052_output/open233_allfact_note_e2e_02/runs/ai_control/nb/p2/rep2/b1b/article.md と research_ledger/verified_fact_ledger.txt(Regression同一入力)

## 修正前 fires(number_only適用後)

- EVID-006 foreign=[33.3] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet. | method=precheck_number_locate
- CONTROL-004 foreign=[33.3] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet. | method=precheck_number_locate

## 修正後 fires

- (なし) foreign_values=[]、number_mismatchは0件 => Stage 2スキップのBLOCKING化(runner L8784-8800)は起動しない、台帳値置換hintも生成されない

## strict≠looseだった文

- loose=[33.3] strict=[] | The evaluation environment set up by a third party was not properly configured, so it might connect to the internet.

注: 本再現は決定論側(precheck発火の消失)のみ。『third party』文がStage 1〜Rewriteを通って保持されるかはLLM依存で未検証(有料・別承認)。
