# CHECKLIST_01 (Production Wiring Checklist 1-11、2026-10-13)

判定: **Family X = 配線済み・未完了(PRODUCTION_WIRED と判定しない)**。**Family Z = 配線済み・runtime未確認**。

| # | 項目 | Family X | Family Z |
|---|---|---|---|
| 1 | 正式初回経路 | PASS: selector(Stage1直後)にM2挿入、runner新out_dirは既定n01、Coffeeは明示CLI`--style-profile coffee_n01_r2_p3` | PASS(N01定数差替のみ。M2はZ-1未決で未着手) |
| 2 | retry/fallback/regen整合 | PASS: `PATH_MAP_01.md`+回帰全PASS。Std part2は既存fallback経路が動作(無変更の証跡) | PASS(共有module、回帰PASS) |
| 3 | Trial専用でない | PASS: Production経路のみ。Trial module(er064_*)をimportしない(test) | 同左 |
| 4 | test PASS | PASS: er030 102/er019 357/er063 59/er026 107/er062 64/ほか全PASS。er064の9件失敗は旧Trial固有(EVIDENCE_01 9節) | PASS |
| 5 | Production runtime発火 | **部分**: KP M2は両levelで発火(kp_supply=m2、db_hybrid)。N01はStd 3part+Adv 3partで発火(style sha一致)。**Std KPはcanonicalization INVALIDで完走せず**。runner `--stage assemble`未実施 | **未確認**(Z記事再生成・音声化STOP中) |
| 6 | actual model_id・routing | PASS(X): gpt-6-luna / gemini-3.8-flash-lite-tts / 既存ASR cascade、route記録あり | **未確認** |
| 7 | CURRENT_SPEC | 更新(commit 3): 未達項目を明記 | 同左 |
| 8 | DECISION_LOG | 更新(commit 3) | 同左 |
| 9 | OPEN_ITEMS | 更新(commit 3): OPEN-343以降で未達項目を管理 | 同左 |
| 10 | Git | PASS(commit 3つ以上、明示add、secret scan hits=0、push済み) | 同左 |
| 11 | 承認と実挙動の一致 | **部分**: M2P0の仕様(予算n2+100/guard/U2/U3/(a)(b2)(c)cap3)とN01の逐語使用・6%減速・再検証維持は一致。**Std episodeで承認実挙動を完走確認できていない**(Std KP INVALID、Std part2がN01でないfallback take)。N-1(適用範囲)・N-3は推奨解釈で実装。FULL_STORYがN01に解決されるのは同一関数・同一定数(runtime確認)、defaultのprofile選択はtestと¥0 dry-runで確認 | 未確定(Z-1/N-2未決) |

## Family X が PRODUCTION_WIRED にならない理由(未達)
1. Std KeyPhrase: 既存canonicalizationがINVALID(1レベル1回の再生成上限内で未完走)。M2P0配線後に"based on"型fragmentがRule7で落ちる事象の頻度は未評価(OPEN-310監視、新規OPEN)。
2. Std Full Story part2がN01でない既存Standard fallback takeで合格(M3 Gate BLOCK=人間承認が必要)。
3. runner `--stage assemble`(M3 Gate/Audio Validation Gate込み)経由のend-to-end未完了(Coffee out_dirの構造上、Trial assembler経由の試聴版のみ)。
