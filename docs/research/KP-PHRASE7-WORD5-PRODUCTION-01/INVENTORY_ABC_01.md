# INVENTORY_ABC_01: 関連仕様の棚卸し(A/B/C)
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27 / read-only・API 0。根拠: ユーザー原文`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_USER.md`(以下「原文」)§5の分類定義。
Grep範囲: `KP_CANDIDATE_MAX|Prompt 2-V|7＋5|7+5|OPEN-534|単語枠|P7|W5`(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/コード/docs/research)。

## 0. 前提の確定(原文の承認範囲)
- 承認(APPROVED_FOR_PRODUCTION): KP最大7+KW最大5の分離抽出、KW優先順位5条件(順序固定)、補足規則(**KP含有語はKW候補から除外**=従前7+5 Trialからの承認済み変更)、出力規則、Gate除外補完・KP救済・HR・フォームとの整合(原文§1〜§4)。
- **非承認(一括採用ではない)**: 原文§1「以前のTrialで得られたすべての改善案を一括採用するものではありません」。
- **判断済みで再質問しない**: Trial-01/02の「有用候補の閾値(Y/B)」「min基準」「易語混入(基本寄り語41%)」「猿の手Adv偏り・再現性」「7+3か7+5か」「追加Trial」(原文§2「易語許容・追加Trial理由にしない」§7「追加Trialや品質基準変更を目的化しない」、`Charter 1`)。= **判断不要**。
- Trial-02 STATUS_02 §4/§5の4つの「判断候補」(採否・閾値・Gate含有語食い違い・OPEN-534)は**原文で全て解決済み**(1=7+5採用、2=閾値不要、3=`含有語は除外`で解消[後述A-3]、4=採用で閉じる)。

## A: 今回の承認内容を成立させるために必要な変更(承認範囲内で実装 = 委任_02)
| ID | 内容 | 根拠(原文) | 変更点(ファイル:行は現行) |
|---|---|---|---|
| A-1 | call1をP7(最大7件・順位付け・reason_ja)へ。Prompt 2(3件)を置換 | §2, §3末尾「Key Phrase側もTrialで用いた最大7件・順位付け・本文一致等」 | 新module(P7/W5本文+sha pin)。`er105:456 run_selection_gate`に`prompt_text/max_items/parse_fn`をkeyword-only既定値付きで追加(既定=従来動作)。`_generate_candidates_impl:292,317`の既定select_fnを差し替え |
| A-2 | call2をW5'(Key Word最大5件、5条件+補足+出力規則)へ。Prompt 2-Vを置換 | §3全体 | `er119_kp_candidates_01.py:46 run_vocab_selection`に`prompt_builder/prefix_check/max_items`のkeyword-only引数。`:330`の呼出で既定W5'を渡す |
| A-3 | **W5本文の「含有語を一律除外しない」補足の反転**。現行Trial W5(sha`3502f0ac…`, `er124:115-116`)は「すでに選ばれたフレーズに含まれる単語であっても…一律除外しない」と書くが、原文§3補足は「**除外する**」。Gate`duplicate_of_top3`(`candidates:95-96`)は既に除外しているため、Prompt側を原文に一致させて食い違い(STATUS_02 §5-3)を解消する | §3補足規則(承認済み変更) | 新moduleのW5'で当該1行のみ置換(`DESIGN_01.md` §1に差分全文・sha案`187f1b87…`)。Gateは無変更 |
| A-4 | 候補上限`KP_CANDIDATE_MAX 8->12`と`shortfall`/`shortfall_detail`の定義(フレーズ7/単語5の種類別上限) | §2「合計最大12件」 | `er119_kp_human_review_01.py:52`、`candidates:429,443`。新定数`KP_PHRASE_MAX=7, KP_WORD_MAX=5` |
| A-5 | 補完の**種類別上限**(フレーズ空き=7-現存フレーズ、単語空き=5-現存単語)と種類別Prompt(フレーズ=P7、単語=W5')。現行2-V(混在・最大5)は廃止方向 | §4「フレーズ枠と単語枠の件数を区別し最大7+5を守る」「補完候補にも同一品質条件・Gate」 | `er119_kp_backfill_01.py:124 plan_quota/:19 BACKFILL_MAX_CALL_ITEMS`、`candidates:456 _run_backfill` |
| A-6 | call1のreason_jaを候補に載せる(現行は空文字) | 原文§3出力規則「各候補に日本語の選定理由を1文・40字以内」、§4「AIによる選定理由を確認可能に」 | `candidates:342`(`reason_ja=""`)、`er105:281 build_original_items`のpassthrough |
| A-7 | 外側retry/exclusion noteの件数文言(「無理に3件に揃えず」`er105:394`)をP7/W5件数に一致 | §3「数合わせ禁止」の整合 | `ft.build_exclusion_note`に`limit`引数(既定3=従来) |
| A-8 | 候補docにkindを必須化・prompt provenance(P7/W5 sha、補完のkind別prompt)の記録 | §6-9(Prompt hash記録) | `candidates:425-432`、`backfill record`(additive) |
| A-9 | sha固定test/golden/isolation testの更新(新moduleの隔離、旧sha test据置) | §6-8 | `TEST_PLAN_01.md` |
| A-10 | 配線の到達確認(6経路)とruntime evidence | §6-1,9 | `EVIDENCE_PLAN_01.md`(実装後) |

## B: 過去に正式承認済みだがProduction未配線(または配線途中)の仕様 / 並行実施できる作業
| ID | 内容 | 承認Scope(根拠) | 本件との関係・扱い |
|---|---|---|---|
| B-1 | **OPEN-546 Gate除外候補の補完**(IMPLEMENTED+EVIDENCE_COLLECTED条件付き、PRODUCTION_WIRED未判定) | `2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_USER.md`§3(E件のみ・初回保持・補完1回) | 7+5で計数(種類別上限)とPromptが変わる(A-5)。承認仕様(E件以内・初回保持・Gate再適用・不要な再課金防止)は**無変更で維持**。PRODUCTION_WIRED判定は7+5でのevidence再取得後にFable |
| B-2 | OPEN-549(Y Adv/Z Advの補完自然発動追跡)、OPEN-544(X/Z救済の自然発火追跡)、OPEN-484(Y possessor_roles/A-1のY実走evidence) | 各OPEN(非blocking・追跡) | 新evidence runを追跡の機会にする(同一run内で記録)。**未観測なら未観測と報告**(原文§6末尾) |
| B-3 | **OPEN-545 学習項目選定フォームv3**(IMPLEMENTED・公開・ユーザー実操作確認待ち) | `2026-10-26_LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01_USER.md`§1 | フォームの7/5枠は既に仕様(`export_form_data_01.py:137`)。7+5候補docはそのまま渡せる。`shortfall_detail.cap`の既定8(`:112`)と送信schema v2は並行Agent(委任_02所有)=**委任_03でフォーム側へ引継ぎ**。原文の通りフォームの実操作確認待ちは本件を止めない |
| B-4 | **KP-CONFIRMED-CONTENT-PROTECTION-01**(確定内容[英語・日本語訳・区分・文法解説]の不変性。設計中) | 原文§4最終項「確定した…を後続工程で無断変更しない」 | 7+5は**候補生成より前段**であり確定後の工程に触れない(`finalize_kp:932`/`_final_items:886`は無変更)。境界=「確定前の候補生成」(本件)/「確定後の不変性Gate」(KCP)。resume時の候補doc不変は現行の保存済み候補読戻しで担保(`ensure_kp_review:1303`) |
| B-5 | ①②③(Production slot=`kp`<=3/`vocab`<=5。③本文意味表示に対応slotなし) | フォームv3承認の区分(①<=3, ①+②<=5, ①+②+③<=12) | 本件の範囲外(KCP `CURRENT_FLOW_01 §0`が指摘済み)。**7+5候補が12件を超えないこと**だけ本件で保証 |

## C: Trialのみ完了で正式採用されていない独立仕様(勝手に導入しない)
| ID | 内容 | 扱い |
|---|---|---|
| C-1 | OPEN-547 K1: call1のattempt内全件再選定のitem単位化 | **承認済み仕様(CURRENT_SPEC:2010/2016)の変更=区分D・導入しない(K0維持)**。ただしP7は7件になりattempt全体INVALIDの確率が上がりうる(`er105:511-526`)。判断材料: Trial-02のP7返答6 run/34件でGate不合格item 0件(`runs/*/trial_result.json state.p7_dropped=[]`)=現時点で懸念小。7+5 evidenceで`outer_attempts`/call1再選定率を測り、問題があれば別途提示(今は判断不要) |
| C-2 | Trial-01の「有用閾値Y/B」「猿の手Adv偏り・再現性」「W3/7+3方式」「追加Trial(順序是正の純粋効果の比較)」 | **今回ユーザーが「易語許容・追加Trial不要」としたため判断不要**(原文§2, §7)。台帳にだけ残す |
| C-3 | AUTO(不在宣言時)でのAdv vocab 5件に単語を組み入れる規則 | 現行は`chosen[:5]`(ai_rank順)で、7+5ではフレーズ4,5位が入り単語は入らない(`DESIGN_01 §4-4`)。変更は**新仕様判断**。Fable設計判断事項D2(推奨=現行維持)。ユーザー判断には上げない(フォームで単語を選べるため実害なし) |
| C-4 | 文法Part 2の最大2件・解説全文の事前生成(Productionは最大1件・解説は選定後生成) | OPEN-545の判断候補(既登録)・`DATA_MODEL_01.md:6`。本件の範囲外。再質問しない |
| C-5 | outer retryでcall1結果を再利用してP7再課金を避ける最適化(原則3の原価低減) | 未承認の仕様変更に当たりうる(外側retry条件)。実装せずFableへ提案のみ(`DESIGN_01 §9`)。効果=外側retry発生時のみ約¥0.12/回 |

## D: 新規OPEN候補(11-8分類付き)
| 候補 | 内容 | 分類 |
|---|---|---|
| (OPEN-534更新) | Trial結果の採否は原文でAPPROVED_FOR_PRODUCTION確定。Statusを`APPROVED_FOR_PRODUCTION`+配線着手へ更新 | 修正へ進む(委任_02) |
| (新) KP75-W5-SUPPLEMENT-TEXT-DERIVED | W5'本文の補足1行はユーザー原文の補足規則「KP含有語は除外」から導出(原文の逐語は`KPに含まれる単語は…除外する`)。逐語文の最終確認をFable/Opusで | 修正へ進む(設計レビューで確定) |
| (新) er106 evidence tool | `er106_joint_runtime_evidence_01.py:45`はselection promptの`prompt_sha256==Prompt 2 sha`を期待する。7+5のdocは別sha(P7)になるため旧runの判定専用と明記する更新が必要 | 修正へ進む(委任_02) |
