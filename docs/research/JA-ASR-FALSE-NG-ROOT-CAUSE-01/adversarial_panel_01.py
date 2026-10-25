import sys; sys.path.insert(0,'.'); sys.path.insert(0,'docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01')
import er007_ja_asr_validator_01 as javal; javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED=False
import er007_ja_secondary_asr_01 as sec
import proto_reading_compare_01 as P
pairs=[('月のしわ、8,900本超','月の死は八千九百本超','POS'),('月のしわ、8,900本超','月の詩は8900本超','POS'),('売上は1,200円です','売上は1200円です','POS'),
('月のしわは多い','月のしは多い','POS(同音)'),
('月のしわ、8,900本超','月の死、8900本超','NEG(わ脱落)'),('月のしわ、8,900本超','月の詩は8800本超','NEG(値違い)'),('月のしわ、8,900本超','月の詩は8000900本超','NEG(値garble)'),
('三日間の猶予','三日目の猶予','NEG(間→目)'),('学校へ行く','学校に行く','NEG(へ→に)'),('彼女は来ない','彼女は来る','NEG(否定)'),('会議は十分で終わる','会議は10分で終わる','AMBIG'),
('犬は走る','犬は歩く','NEG(別語)'),('私は本を読んだ','私は本を読む','NEG(時制)'),('今日は晴れ','今日は雨','NEG'),('私は行く','私わ行く','POS?(ASR不出)'),('1,2,3個','123個','NEG(列挙)'),('月のしわ','月の','NEG(脱落)')]
for c,a,l in pairs:
    base=javal.classify_ja_asr_match(c,a,allow_reading_resolver=False)
    e=sec._numeric_value_equivalence(c,a,base) if not base.should_pass else None
    prod=base.should_pass or e is not None
    ok,why=P.design_a(c,a)
    print(f"{l:12s} prod={'PASS' if prod else 'NG  '}({base.classification}) designA={'PASS' if ok else 'NG  '}({why}) | {c} | {a}")
