# PATH_CHECK_01 Family Z KP経路確認(FAMILY-Z-KP-STRATEGY-L-DECISION-CLOSEOUT-01、読取のみ)

| 経路 | 実装箇所 | Strategy L固定か | DB Hybrid/M2分岐 |
|---|---|---|---|
| 初回選定 | `er026_family_z_fiction_production_runner_01.py` L1173 `kp_fn = hooks.get("kp_fn") or w62.run_kp_with_outer_retry` → `er062_family_z_writer_01.py` L971 `run_kp_with_outer_retry` L977 `select_fn = select_fn or sc.run_key_phrase_selection`(`kp_backend`引数を渡さない) | はい。`er003_v1_n3_01_scaffold_generate.py` L295 `kp_backend`既定`"strategy_l"`、L325のみ`"db_hybrid"`で分岐 | なし(er062/er063/er026 Z runnerに`db_hybrid`/`m2`/`kp_backend`の記述ゼロ。grep確認) |
| 外側retry(OPEN-310暫定) | 同`run_kp_with_outer_retry`ループ(`Z_KP_OUTER_RETRY_MAX`、canonicalization INVALID時) | 同じ`select_fn`を再呼出=Strategy L | なし。`outer_retry_log.json`のscope=「Z限定・暫定」 |
| Redundancy再選定 | 同関数内`red_max`(共有`KEY_PHRASE_REDUNDANCY_RETRY_MAX`) | 同上 | なし |
| fallback | Z側にKP fallback機構なし(`m2_fallback`はer030/Family X側のみ。er063の`m2_fallback_events=[]`契約=委任_03、KP非関与) | n/a | なし |
| regeneration | `--stage kp`等も同じ`kp_fn`経由 | はい | なし |
| `family_z` NotImplementedError | `er030_key_phrase_db_hybrid_source_reference_contract_01.py` L28/L67 `SUPPORTED_FAMILY_PROFILES = ("family_x",)`、`family_z`は`NotImplementedError` | 残存(Zから誤って呼ばれない) | - |

## diff確認
- `git log -- er062/er063/er026 Z runner/er030 selector/m2_supply`: XZW関連は`d365e1fb`(委任_02)のみ。`git show --stat d365e1fb`のうちZ側は`er063_family_z_audio_01.py`のみ(N01 narrator style配線、+81/-7)。`er062_family_z_writer_01.py`・`er026_family_z_fiction_production_runner_01.py`はd365e1fbで無変更。委任_03(adfae809/c13d0126)はZ KP経路に触れていない。作業ツリーのこれら4ファイルに未commit差分なし。
- er063の`kp`記述はTTS clip(kp_en/kp_ja/kp_expl_en)のみで、KP選定には無関係。

## er073(Trial)のProduction誤参照
`grep -rn "er073_" --include=*.py`: ヒットは`er073_family_z_kp_db_hybrid_m2p0_migration_01_{diff,run,test_01}.py`の3ファイル(自身)のみ。Production moduleからの参照なし。Trial runnerはProduction `run_kp_with_outer_retry`を呼ぶ側(逆向き)で、Productionは参照しない。

## Family X M2P0配線への影響
Z側コード変更ゼロ。er030 regression 108件PASS(下記)。
