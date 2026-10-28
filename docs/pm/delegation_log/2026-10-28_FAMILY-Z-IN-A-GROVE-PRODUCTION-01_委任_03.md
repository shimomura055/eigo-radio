# FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_03(本文逐語、2026-10-28)

管理ID FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_03「Fable CP結果の反映(Std 1文の是正)+KP/文法Human Review用V3選定フォームの公開(Std/Adv)」。前提=委任_02、run `er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/`、kp段rc=4 KP_REVIEW_PENDING、累計¥22.00/Cap¥70、`_run.sh`helper)、Seed `er026_seeds/in_a_grove/seed.json`(conversion_plan: 性暴力は非グラフィックの1句「he took her by force」程度)。前例=FZ-TELL-TALE-HEART-RESELECT-REMAKE-01 委任_01(V3フォームへのデータ接続・公開手順)、FORM_DATA_01.md/DATA_CONTRACT_01.md、OPERATIONS_01.md。並行worker: Family Y 委任_03(SSOT・ACTIVE_TASK編集中=直前再Read・最小Edit)。本委任ではSSOT編集なし(ACTIVE_TASKの本案件行のみ可)。
開始時と有料前に stop_scope_check_01.py(--managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --out .../stop_check_03.json)(rc=3で停止)。費用上限: 本委任¥10(run累計Cap¥70内)。RESTART_STORM回避(同一run起動間隔150秒以上)。

## Fable CP結果(委任_02本文の照合)
- Adv(r2.md)/Std(std.md): 7証言が原作順、3当事者の矛盾(多襄丸=決闘で刺した/真砂=自分が刺した/武弘=自害+見えない手)・結末(見えない手→闇へ沈む)・評決なし=CP重大欠落0。Preview(Std日本語)は先取りなし。Comment 3の「亡くなったタケヒロの話では…」は話者の存在への言及に留まり内容の先取りなし=許容。
- 是正1件(Seed conversion_planからの逸脱、軽微・本文品質): Std std.md:11「She fought with her dagger, but I forced her to have sex with me.」はStandard(A2)学習者向けとして明示的すぎ、Seed指示(非グラフィックの1句)に反する。Advと同じ「She fought with her dagger, but I took her by force.」へ承認済み機構で是正する。優先順: (a)CP処置規則の決定論パッチ(apply_cp_deletion_patchが置換に対応していれば使用し記録)→(b)対応していなければ既存のLocal Rewrite経路(er020系、台帳記録付き)でこの1文のみ→(c)いずれも不可ならstd_adjust段のみ再実行(¥3〜4、他文が変わるため再CP必要)。採った方法・前後sha・記録先を明記。新Validator・新Gate・Prompt変更は禁止。
- 是正後、Stdの本文に依存する既生成物(plan/support/kp候補[sha c9124ec57bc3a2fa/941647eb453de90d等]・study_text)の整合を確認し、Std側のplan,support,kpを必要な範囲で再実行(ユーザー選定前に候補が本文と一致している状態にする。再実行前にer119のreview状態をOPERATIONS_01の手順で扱い、矛盾させない)。Adv側は再実行しない。

## 選定フォーム
- Std/AdvのKP候補(最大7、日本語訳+AI選定理由)+KW候補+文法Top1/Top2(文法名+解説全文、原則1件選択・0件可・2件禁止)を、公開済みV3フォーム(user_test/selection_form_v3/)へ前例どおりデータ接続し、user_test/family_z_in_a_grove_01_form/等の前例命名でGitHub Pagesへ公開。候補ID・候補集合sha・本文sha(照合コード)を保持。Std/Advの選定URLと、review_request.mdの内容要約(KP候補一覧・文法候補と解説)をhand-backに逐語で載せる。Fable注記用に、委任_02で指摘のあった候補(Std KP「sink into darkness=命が尽きる」の訳、Std文法Top1/Top2が同じ「同格句」)を明記。
- 選定確定・kp再開は行わない(ユーザー選定後にFableが委任_04で指示)。

## 成果物・Git
CP_RESULT_01.md、docs/pm/RESULT_PACKET_FZIG3.md(≤15行、4行+判定整合行)、本ファイル、ACTIVE_TASK本案件行を「KP/文法ユーザー選定待ち(フォームURL)」に更新。Git: 自分のファイルのみ明示add→commit→git push origin HEAD:main(FFのみ)。git add -A禁止。hand-back: 是正方法と前後、再実行stage・費用、Std/Adv選定URL、候補一覧(逐語)、累計費用、commit sha、判断候補。
