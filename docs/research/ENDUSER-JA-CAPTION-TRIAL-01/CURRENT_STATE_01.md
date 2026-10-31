# CURRENT_STATE_01 ENDUSER-JA-CAPTION-TRIAL-01(2026-10-31)

- 現行Production: End Userページ asset `enduser_page_assets/rev01-h/`(英日連動ハイライト[rev01-f]+クリック=ハイライトのみ[rev01-h]、OPEN-618/624)。日本語訳は本文側の`.tr`ブロックにあり、点灯(`.jhl.on`)しても再生バー(画面下固定)から離れた位置にあるため、スマホでは画面外になりやすい。
- 連動の仕組み(app.js): `ja_align`から日本語群を`<span class="jhl" data-jg="idx:g">`で包み、`jaLight(sid)`が点灯群`activeG`を更新。群が無い文(`sidToG`未登録)は何も点灯しない=null安全。文間2秒未満で同一群なら`jaHold`で維持。
- Trial対象の既公開dir(rev01-h配線済み): `user_test/family_x_meta_waddle_world_01/enduser`(X)、`family_y_production_surname_choice_01/enduser`(Y)、`family_z_melos_kphr_evidence_r3/enduser`(Z。凍結dir`family_z_in_a_grove_01`ではない)。各Std/Adv。
- 変更しないもの: `enduser_page_assets/rev01-h/*`、`er135_enduser_rules_01.py`、既公開dir。
