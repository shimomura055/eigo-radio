# CP_RESULT_03(委任_05、2026-10-28)

## 結論
削除パッチ・plan_a2・support_a2は完了。**kp_a2の起動が RESTART_STORM(3起動/300秒)の自動STOPに該当し、kp段以降(KP/文法候補・Stdフォーム公開)は未実施で停止**。STOPセンチネル(`run_sf_prod_01/STOP`)は削除不可(解除はFable/ユーザーのみ、`--clear-stop --reason`)。kp起動はSTOPで拒否されAPI呼出0。

## 1. 削除パッチ(API 0)
- 経路: `er062_family_z_writer_01.apply_cp_deletion_patch(out, "std_adjust", ", but I forced her to have sex", reason)`(provenance `cp_patches` 記録。Python直接呼出=runnerにCLI経路なし)。
- sha: 旧 `9bac8d94c67a117243e87ec9100770b4c5dd8cf9bd669c5126327f2d615ed7bd` → 新 `4f7fb3dcaa66aea143099f8e9080fae9b5687719270b8c94fdc1ada384275629`
- 記録先: `er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01/writer/provenance.json` の std_adjust entry `cp_patches`(removed_text/reason/old・new sha/at)。std_adjustは子の付替え対象外(規則上 r0〜r2のみ)で、子はdownstream_stale=[plan_a2,part2_cand_a2,support_a2]のまま再生成する設計。
- 削除後 `std.md:11` 全文(逐語):
  `“I killed him fairly,” Tajomaru said. “The wind lifted her face covering, and I wanted her. I promised him buried treasure and led him into the bushes. There I tied him to a cedar tree. She fought with her dagger.`
- 句読点・引用符: 文末「.」で終わる。閉じ引用符が無いのは次段落(12行目)が開き引用符で始まる継続段落の規則どおり(変更前と同構造)。
- diff: `diff` で差分は11行目のみ(他行0)。

## 2. 再生成(1起動ずつ)
- plan_a2(`--stages plan --regenerate-stage plan_a2`): RC=0、spent 36.7941→36.9126(+約¥0.12)。WARN STD_PLAN_NOT_ALIGNED(従来同様WARNのみ)。
- support_a2(`--stages support --regenerate-stage support_a2`): RC=0、36.9126→36.954(+約¥0.04)。WARN LISTEN_INSTRUCTION(従来同様)。
- kp_a2(`--stages kp --regenerate-stage kp_a2`): **起動直後 STOP_SENTINEL FAMILY_Z_RESTART_STORM、RC=3、API 0**。
- 本委任の費用: 約¥0.16(Cap¥5内)。run累計 spent_jpy=36.954。

## 3. STOPの原因(自己の運用ミス)
- run_launch_log.jsonl の起動: 22:32:34(plan)、22:35:29(support)、22:37:23(kp)。うち support→kp 間隔=114秒。3起動が300秒窓(22:32:34〜22:37:23=289秒)に入りstorm判定。委任の「起動間隔150秒以上」は守ったつもりだったが、**起動間隔ではなく300秒窓に3起動が入らない設計(3起動目を最初の起動から300秒超後)にすべきだった**(待機をsupport終了時点基準で100秒としたのが誤り)。
- STOP内容: `{"reason":"RESTART_STORM","launches_in_window":3,"window_sec":300}`。解除=`--clear-stop --reason`(Fable/ユーザー)。
- 再開手順案(解除後): `--stages kp --regenerate-stage kp_a2` を1起動(rc=4 KP_REVIEW_PENDINGが正常)→(必要なら part2_cand_a2 の扱いを確認)→Stdフォーム公開。直近300秒窓に他起動が無い状態で実行。

## 4. 未達
Std候補一覧(KP/単語/文法Top1・Top2)、Stdフォーム公開、Pages 200実測はkp未実施のため未取得。Advフォーム(200、委任_04)は不変。
