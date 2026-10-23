# ROOT_CAUSE_02: 『開いた窓』原作結末欠落の根本原因(Opusレビュー反映版)

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_02 / 2026-10-23 / 設計のみ・API 0・JPY 0
位置づけ: ROOT_CAUSE_01.md(工程別追跡表・承認履歴・既存QA表)は履歴として有効。本書はOpusレビュー(OPUS_REVIEW_01.md、条件付きGO)に基づく**改訂点**(OF-FZSF-M01・S01・S02)を反映した現行版。01の表(§1工程別追跡・§3承認履歴・§4既存QA)は変更なしで参照する。

## 0. 結論(改訂)
- 最初に失われた工程=Advanced R0(`the_open_window/run_e2e_01/writer/r0.md`)。Std/AdvはR0を共有するため同じ欠落を継承(独立に2度消えたのではない)。
- 原因: **生成工程の指示体系が語り手の最終文を落とす方向に誘導していた(主因・確度高、定量化は不可)**。LLMの自主的な結末形の選択は副因。取得データの欠落は否定(`seed/primary_text_excerpt.md:59`に最終文あり)。
  - 改訂(S02): 01の「主因約80%/副因約20%」は根拠のない数値だったため撤回する。反事実は未検証であり、確度は「高い(文言と観測が整合)」にとどめ数値化しない。
- **追加の原因(工程上の欠陥・M01)**: 欠落は生成後に**検出されていた**(10-21 text stageの所見(a)「原作最終文が両版に無い」、`E2E_PLAN_01.md`§10-A、`docs/pm/RESULT_PACKET_OW2.md:5`、OPEN-428)にもかかわらず、**処置されずTTS・組立へ進み成果物が出荷された**。これが成果物に欠落が残った直接原因である。「検査が無かった」のではなく「**検出した所見を処置する規則が無かった**」(CP観点4の文言`E2E_PLAN_01.md:47`が欠落を合格側に読める書き方だったことに加え、所見(a)をTTS前に解消する処置規則が存在しなかった)。再発防止は生成側(Seed・Prompt)と、CPの処置規則の両方で必要(DESIGN_02 §6-3)。

## 1. 誘因(Prompt・構成指示側)— 01の2点に3点を追加(S01)
01で特定済み: (1) Seed `conversion_plan`(`seed.json:18`)の結末定義(犬の嘘)+「最後の行の後に説明を足すな」、(2) 編集方針ブロック(`er062_family_z_writer_01.py:106-109`)から結末維持条項が消失(2026-10-12以降)、(3) R0フレーミング「NOT a summary to reproduce」等。
Opusレビューで追加された誘因:
| # | 誘因 | 場所 | 作用 |
|---|---|---|---|
| 4 | `R0_BLOCK_COMMON`の「Prefer concrete events over abstract or literary implication」 | `er062_family_z_writer_01.py:88` | 語り手のメタな最終文(総括・意味づけ)は「literary implication」側に分類され、避ける対象に見える |
| 5 | `seed_elements[5]`の書き方 | `seed.json:9` | 歌詞・白いコートは本文由来の具体物なのに、オチだけが「the closing line says that…」という**本文外からの説明**で書かれる。R0冒頭の「NOT a summary to reproduce」と組み合わさり、再現対象から外れやすい |
| 6 | 名前の硬い制約が三重 | R0 L94「Only the main character … may be given a personal name」/ `seed.json:18`「Framton Nuttel as the only person with a personal name」/ R1・R2 `REVISE_USER_TMPL` L142「only {main_character} may have a personal name」 | オチの主語(her=Vera)が名前を持てず、台詞(少女の発話)で閉じる選択を後押しした可能性(推測)。R0でVeraが残ってもR1/R2が消す構造でもある |
いずれも「判断を誘導した構造」であり、LLMの気まぐれではない。

## 2. 工程上の欠陥(M01)の詳細
| 時点 | 事実 | 欠陥 |
|---|---|---|
| 2026-10-21 text stage | 所見(a)「原作最終文が両版に無い」が記録された(Fable CP対象と明記) | CP判定の中身が記録されていない(未確認) |
| 同 | CP観点4「結末の前に嘘だと分かる説明や示唆がない」(`E2E_PLAN_01.md:47`)が合格側に読める | 観点が「先回りの示唆が無い」しか見ず、「種明かし自体が在る」を要求していなかった |
| 同 | 所見を受けて**TTSへ進んだ** | 所見の処置(TTS前の修正)を義務づける規則が無かった |
対策=DESIGN_02 §6: (i) essentialsの各項目を本文の逐語引用付きで確認(観点4型の曖昧さの排除)、(ii) **essentials未充足はCP不合格とし、TTS前に修正する**処置規則、(iii) 規則はFable(AI)による既存CPの細分化であり、自動判定・retry・API・新工程ではない(M07)。

## 3. 反事実Trialの扱い(改訂)
- 旧ブロック(f955847db)復活の選択肢は無いため、旧ブロック条件の単独反証Trialは**行わない**(Opus指摘)。01のn=3×3条件・約20円の因果反証は**取り下げ**。
- 代替: 修正版BのTrial(DESIGN_02 §9、U1)に「Seed修正のみ」アームを1本入れる。これで「Prompt原則変更が本当に必要か」(Seed修正だけで結末が残るか)の材料が同時に得られる。設計移行はTrialと並行で可。

## 4. 次の一手(FableのQDC記録用)
- 原因仮説: 指示体系の誘導(誘因1〜6)+検出所見の未処置(M01)。根拠観測値: `seed.json:9,15,18`、`er062_family_z_writer_01.py:88,94,106-109,142`、`E2E_PLAN_01.md:47`、`r0.md`末尾。
- 前回との差分: 確度の数値を撤回、誘因3点追加、工程欠陥を原因に追加、反証Trialを修正版Bの検証に吸収。
- 次の一手(改善見込み 高): U1(Offline Trial承認)→Trial(約40円)→VALIDATED→(別途ユーザー判断)Production採用。
