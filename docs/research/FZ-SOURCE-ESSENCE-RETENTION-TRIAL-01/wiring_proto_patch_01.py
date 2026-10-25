import re,sys,io
src=open('er062_family_z_writer_01.py',encoding='utf-8').read()
def sub(old,new,cnt=1):
    global src
    assert src.count(old)==cnt,(old,src.count(old))
    src=src.replace(old,new)
# 1 Narration line const + render
sub('_REVISE_TAIL = " Output the title and the story only."',
'''_REVISE_TAIL = " Output the title and the story only."
_REVISE_THIRD = "in third person, "
_REVISE_NARR = "in the narration described in the Must-keep section below, "
_NARR_LINE = ("- Narration: {voice} Keep this narration throughout: the same person, point of view and narrator's stance "
              "(including how the narrator speaks to the listener); wording, length and sentence structure may change. "
              "The role descriptions of people below do not change who is telling the story.")''')
sub('''         "These are the points that make this story work. Keep their meaning (your own words are fine); everything not listed here may be shortened or reshaped."]
''','''         "These are the points that make this story work. Keep their meaning (your own words are fine); everything not listed here may be shortened or reshaped."]
    L.append(_NARR_LINE.format(voice=ess["narration_voice"].strip()))
''')
# 2 revise
sub('''        assert _REVISE_TAIL in tmpl
''','''        assert _REVISE_THIRD in tmpl
        tmpl = tmpl.replace(_REVISE_THIRD, _REVISE_NARR, 1)
        assert _REVISE_TAIL in tmpl
''')
# 3 Essentials ctor guard
sub('''        self.ess = ess
        self.keep_names''','''        nv = ess.get("narration_voice")
        if not (isinstance(nv, str) and nv.strip()):
            raise FamilyZSeedEssentialsStop("FAMILY_Z_SEED_ESSENTIALS_INVALID: narration_voice(必須)")
        self.ess = ess
        self.keep_names''')
open(sys.argv[1],'w',encoding='utf-8').write(src)
