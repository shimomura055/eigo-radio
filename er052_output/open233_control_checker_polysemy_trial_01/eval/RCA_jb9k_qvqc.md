# RCA: jb9k(重大)とqvqc(Checkerタイトル書換え)(委任_04、¥0、API無し)
根拠はすべて runs/ 配下の既存ログ(書き換えなし)。ファイルは er052_output/open233_control_checker_polysemy_trial_01/ 基準。

## RCA-① ai_control jb9k(= rep1): 「AIは外に出ていない」型の否定文(ユーザー判定=重大)
- **初出工程**: R0(Writer初稿)。runs/ai_control/control/rep1/ja_writer/original.md・revision1・revision2の3つとも同一文「テスト環境からAIが外へ流れ出した事実も報告されていません」(各1件)。Rewrite等で変わらずEN pre_checker→最終ENも同一(Checkerは非書換え)。
- **台帳fact**: EVID-008(Claudeモデルは第三者評価環境から**インターネットへ到達し、3組織の実システムへ不正アクセス**。ただし「モデルは自己持ち出し(exfiltrate)も意図的な脱出の試みもしていない」)、CONTROL-003(「Anthropicはモデルの自己持ち出しなしと報告」)。台帳には「誰も報告していない」という主張は無く、「自己流出・意図的脱出なし」だけがある。記事文は「自己持ち出しなし」を「テスト環境から出た事実の報告なし」へ広げ、直前段落が述べる外部到達・PyPI公開と矛盾して読める。
- **Checkerはこの文を検査したか**: **した**(拾った)。checker/runs/meta_run03_advanced.json: stage1_llm(coverage candidate、route r3、unit S7.4)がcycle1・2とも候補化。dev.severity=MAJOR、issue=「台帳は特定の3件で『意図的に脱出しようとしていない』と述べるのみ。記事は『どのAIもテスト環境から出たと報告されていない』という広い主張にしている」(scope拡大、changed_fact/changed_scope=true、unsupported_new_claim=true)。
- **PASSした機序**: Stage2が materiality=**QUALITY**(basis=ledger_scope、rewrite_kind=replace_with_ledger_value)と判定。2nd opinion(2-of-2、batch cost ¥0.4765)もQUALITY=confirmed_downgrade:true。QUALITYはBLOCKINGでないためRewrite対象にならず、cycle1 blocking=1(別文CONTROL-003)/non_blocking=8、cycle2 blocking=0/non_blocking=8で RESOLVED_REWRITE_THEN_DOWNGRADE(PASS系)。cycle2は「reused_nonblocking_verdict=true」で前回の非ブロッキング判定を再利用。つまり「検知はMAJOR候補→Stage2が範囲拡大(scope)と見てQUALITY格下げ→2回目も同判断→放置」。**否定・不在主張が『台帳に無い』こと自体は検知されていたが、『外部到達という事実と読者の読みが反転する』重大性としては評価されなかった**(basisがledger_scopeで、事実反転=ledger_fact/direction系の扱いにならなかった)。
- **同型(否定・不在主張)の文の他記事**(最終EN article.mdの機械Grep、「Nor has/no evidence/not been reported/there is no」型): 3文/3記事(jb9k本件、meta 249j「There is nothing wrong with getting help from a human.」=不在主張ではなく価値判断、meta ua6f「There is no confirmed explanation...」)。JA R2の「報告/確認されていない」型: 3文/3記事(jb9k、meta ua6f、space_weapons 4mjq)。件数のみ、他記事の重大性は未判定(本RCAの範囲外)。

## RCA-② meta qvqc(= rep2): Checkerによるタイトル書換え(ユーザー判定=NG、重大/軽微は確認中)
- **書換えを起こしたrule**: Stage2 materiality=BLOCKING(basis=unsupported_relationship、claim=タイトル「# I Followed an AI Phone Agent and Found a Human」、section_type=title、related_fact=MUSE-HC-006)。dev: severity=MAJOR、changed_actor=true、unsupported_new_claim=true。issue=「記事の書き手(私)がAI電話エージェントを追跡して人間を見つけたという体験はLedgerにない」。severity_final=BLOCKING、rule_id=existing_major_v2、rewrite_kind=delete。titleは構造要素のため `structural_element_rewrite`(original_rewrite_kind=delete→置換へ)で `1_word_connective`(single_text_local E-2 / e1_minimal_word_edit(violation_span))により「Meta Tested an AI Phone Agent and Found a Human」に書換え。en_title_changes=[{cycle1, before, after:null}]、quality_degradation_en.title_changed=true。
- **before_was_ng**: Checker自身は**BLOCKING(NG)と判定**(元タイトルの一人称体験はLedger外)。評価インスタンスは before_was_ng=false(前タイトルは演出としてNGでない)。つまり評価者とCheckerで前タイトルの判定が分かれたが、ユーザーは書換え後を『主体を取り違えた新しい誤り』としてNGと判定。
- **Recheckが書換え後の主体誤りを見逃した理由**: (a) 書換え時のactor_guard(ag1_strict)は ok=true・new_classes=[](「Meta」を新規主体クラスとして検出せず)、(b) rewrite_new_precheck_findings_count=0、(c) cycle2 stage2_results(5件)は本文(section_type=body)の文のみで、タイトル行(section_type=title)の単位は含まれない(exit_check: n_candidates=5、n_judged_units=28だが、cycle2の判定結果にtitleは無い)。full_recheck_required=true(理由: multiple_claims_rewritten_same_cycle、short_section_no_window(title_hook_in_one_line))だったが、タイトル書換えそのものの再判定ログは見当たらない。したがってRecheck対象にタイトルが入った証拠は無く、主体照合(誰が何をテストしたか)がタイトル書換え後に行われた記録も無い。なお「I」→「Meta」は Ledger に整合する名詞への置換で、ag1が検出する主体変更クラスの範囲外だった可能性(未検証)。
- **過去事例との関係**: OPEN-238(Rewriteが無関係文を置換/新規誤りを作る)、および過去rep群の「title delete」(タイトルをdeleteでなくLedger寄りに置換)と同じfailure mode系: BLOCKING指摘の修正案(Rewrite)が新しい主体誤りを作り、Recheckが拾わない。

## 含意(事実のみ)
- ①: Writer初稿由来の「否定・不在主張」型。Checkerは候補化しMAJOR(scope)と出したが、Stage2が2回ともQUALITYへ格下げ。Rollback同様、台帳との文字面照合では『ledger_scope(範囲逸脱)』止まりになり、読者が受ける事実反転(外部到達あり→なしと読める)が重大度に反映されにくい型。
- ②: Checker Rewriteが新規の主体誤りを作る既知failure mode(OPEN-238系)の再発。タイトルはRecheck判定単位に含まれず、書換え後主体の照合なし。
- 本件は18本中の事象でありN=18の範囲。他記事の同型は未判定。
