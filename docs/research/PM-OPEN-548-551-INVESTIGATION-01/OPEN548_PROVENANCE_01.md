# OPEN-548 猿の手 seed provenance不一致 調査(read-only、API 0、JPY0)

管理ID: PM-OPEN-548-551-INVESTIGATION-01 委任_01 / 2026-10-26。到達=INVESTIGATED(是正案付き)。

## 結論(先頭)
- 不一致は**意図された変更の帰結**であり、不具合ではない。10-25にユーザー承認(案A)で5作品のSeedへ`source_essentials.narration_voice`が追記され、Seed凍結(sha固定)のfail-closedが設計どおり作動した。
- **猿の手だけではない**: 告げ口心臓を除く承認済み4作品(猿の手/賢者の贈り物/開いた窓/二十年後)の既存run(`run_sf_prod_01`)がすべて旧seedにpinされたまま。同じ停止が出る(下表)。
- 公開物は不変(既存本文・音声・KPは旧seed生成)。実害なし。
- 推奨=**案3(現状維持)**。猿の手の本文再生成が要る時点で案1(新run、告げ口心臓`run_sf_prod_02`と同じ前例)。案2は不採用(下記)。

## (a) 事実
| 項目 | 値 |
|---|---|
| 現行seed.json | sha`8f76316068e7…` mtime 2026-10-25 10:15:52 JST、11148 B |
| 旧(seed_STALE_20261025.json) | sha`8f1128b925c8…` 10959 B(SEED_PROVENANCE.json notes: 「旧sha 8f1128b925c8」) |
| 差分 | `source_essentials`末尾に`"narration_voice": "The story is told in the third person by an outside narrator in a quiet, restrained voice; the fear comes from sounds, silence and what the characters say and do."`の**1キー追加のみ**(`diff <(json.tool 旧) <(json.tool 新)`) |
| 更新を行った委任 | FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_04、commit`53ce7b397`(2026-10-25 10:35 JST「案A Production配線…+5作品Seed補完」) |
| ユーザー指示(逐語) | `docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER_02.md` §1「Seedの『作品の本質』に `narration_voice` を追加する。」、§3「既存Seedへの必要な情報補完と、Production経路の整合を確認してください。/今回の配線を理由に、既存の完成記事をすべて再生成する必要はありません。」(対象に『猿の手』を列挙) |
| 影響性 | メタのみではない。`er062_family_z_writer_01.py:388-419`で`narration_voice`はR0/R1/R2/Std調整のPromptへ入り、`essentials_sha256`(provenance記録、`:735-737`付近)も変わる=**新規に本文を作るとき**に効く。既存本文は変えない |
| git追跡 | seed 4ファイルとも追跡済み(`git ls-files`)。履歴33565584a(作品登録)→53ce7b397(narration_voice) |

## (b) 既存run・公開物との関係
- 猿の手の既存5run(`run_fzcw_e1_01/_02`・`run_kpbf_ev_01`・`run_kpgm35_01`・`run_sf_prod_01`)のprovenance`seed_sha256`はすべて`8f1128b925c8`(grep確認)。公開済みの本文・KP・音声は旧seedで生成された事実=意図どおり(USER_02 §3で再生成不要と指示)。
- 同じ構造が4作品に存在(`writer/provenance.json`のseed_sha256と現seed.jsonのsha先頭12桁):
  | 作品 | 既存run pin | 現seed.json | 状態 |
  |---|---|---|---|
  | the_monkeys_paw | 8f1128b925c8(全5run) | 8f76316068e7 | 不一致 |
  | the_gift_of_the_magi | 6bbd6867aecb(sf_prod_01) | 1a5dfeb65331 | 不一致 |
  | the_open_window | 69f3e63cfd4f(sf_prod_01他) / 9abe50b85551(旧e2e/pntrial/mock) | 5a6192c40af7 | 不一致 |
  | after_twenty_years | 7d3268ccabad(sf_prod_01) | 405e035dc02a | 不一致 |
  | the_tell_tale_heart | run_sf_prod_01=cf850588ebb2 / **run_sf_prod_02=355a317a9b18** | 355a317a9b18 | 新runで一致(前例) |
  | melos | f4a85f5ceb9a(全run) | f4a85f5ceb9a | 一致(Seed不変) |

## (c) 停止条件と正規の解消手段
- 停止箇所: `er062_family_z_writer_01.py:630-638`(`Provenance.__init__`: 既存`writer/provenance.json`の`seed_sha256`≠現seed shaで`FamilyZProvenanceMismatchStop`)。runnerは`er026_family_z_fiction_production_runner_01.py:1307-1311 _prov(ctx)`経由で、`stage_plan/support/kp`(`:1431,1450,2008`)と`run_writer_chain`(writer/std_adjust)が通る。`stage_tts/provision_shell/gate/assemble/pages/page_verify`は`_prov`を通らない。
- 実測停止: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/evidence_runs/z_launch1.log`:3 `provenance=8f1128b9… 現在=8f763160…`、API前停止・費用0。
- **再pinの正規手順はrunnerに無い**(`seed_sha|repin`のGrepで該当なし)。`--regenerate-stage`はProvenance生成より後なので、不一致runでは使えない。`seed_dir`は`{E2E_RUN_ROOT}/{slug}/seed`固定(`:1261`)でrun単位の旧seed指定もできない。
- 正規の解消=**新run dir**(新Provenanceが現seed shaで作られる)でwriterから再生成。告げ口心臓`run_sf_prod_02`が前例(同じ10-25のseed更新後に新runで一致)。

## (d) 是正案
| 案 | 内容 | 費用 | 品質 | 公開物 | 分類 | 評価 |
|---|---|---|---|---|---|---|
| 1 | 新run(`run_sf_prod_02`)を新seedでwriterから再生成 | 有料。writer 4段は旧run実績で約19.4円(R0 2.48+R1 4.37+R2 4.38+Std 8.14、`run_sf_prod_01/writer/provenance.json`)+plan/support/KP/TTS等(告げ口心臓の概算全体は約40円、USER_02) | 新本文(narration_voice反映)のためCP/品質検査/再試聴が必要 | 差替えならD(公開物差替え=ユーザー承認+最終試聴) | D(実行する場合) | 猿の手の再生成が必要になった時の正規手段 |
| 2 | 旧seed参照の再pin/provenance明示指定 | API 0 | 旧本文を保つが、(i)provenanceの`seed_sha256`手書き換えはSeed凍結のGate回避で禁止、(ii)runnerへ「旧seed指定」経路を新設するのは新機能(Production挙動の追加)でB(自己解決)ではない、(iii)`essentials_sha256`が旧値と新値で違い、resume判定(`er062:781`付近)と整合しない | 不変 | 不採用 | 推奨しない |
| 3 | 猿の手は新規KP生成を行わない(現状維持) | 0 | 変化なし | 不変 | 実害なし | **推奨** |

## 分類確定案(Fable判定用)
- OPEN-548: 「不具合候補(要照合)」→**意図どおりの仕様作動(実害なし)**。10-25案A承認(USER_02 §1・§3)で説明済みの帰結。
- ただし**運用上の見落とし**が1点: 10-25の配線は「既存run(猿の手を含む4作品)がrunner経由で再開不能になる」ことを明示していない。影響は`plan/support/kp/writer/std_adjust`の再実行のみ。TTS以降の段(Z完成段)は使える。
- 扱い=「記録のみ。猿の手/賢者/開いた窓/二十年後のKP再選定・writer再生成が必要になった時点で案1を委任(D)」。KP-GATE-DROP-BACKFILLの猿の手runtime証拠はreplay(R5a/R5b)で取得済みで、fresh runは必須でない(EVIDENCE_01 §6)。
