# er033_output/family_x_02_listening_01/

管理ID: TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(Fableからの修正1回目)

`player.html`は、既存の生成スクリプト
`er019_family_x_audio_production_runner_01.py::build_player_html()`
(`--stage player`)をそのまま実行して得られた出力のコピー(内部証跡用)。
生成元・生成コマンドは以下のとおり。コード変更は行っていない。

- 生成元out_dir(オリジナル、正本): `er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp/player.html`
- 生成コマンド(逐語): `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug "family_x_b3_diversity_trial_01/hormuz" --run run_02 --level both --stage player --out-dir <上記out_dir> --tts-backend speech_metadata_flash_lite --budget-jpy 30`
- `player.html`内の`<audio src="file:///C:/...">`はローカル絶対パス。
  `docs/pm/PM_GOVERNANCE.md`9-5により、ユーザー向け試聴リンクとしては
  使用禁止(内部証跡パスとしてのみ記録可)。ユーザー試聴を依頼する場合は
  別途GitHub Pages配布経路への変換が必要(本タスクのスコープ外、未実施)。

## Assembly結果(参照)

- B1B(Advanced): `.../b1b/assembled/Family_X_Audio_B1_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav`(292.03秒)
- A2(Standard): `.../a2/assembled/Family_X_Audio_A2_FAMILY_X_B3_DIVERSITY_TRIAL_01_HORMUZ.wav`(331.781秒)

詳細は`TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02_REPORT.md`
§7を参照。
