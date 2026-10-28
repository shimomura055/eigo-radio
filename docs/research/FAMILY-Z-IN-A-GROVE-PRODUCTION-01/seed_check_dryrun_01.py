import sys, os, json, shutil, tempfile, hashlib
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_writer_01 as w

KEY = 'in_a_grove'
SRC = 'er026_seeds/in_a_grove'
root = tempfile.mkdtemp()
seed_dir = f'{root}/{KEY}/seed'
os.makedirs(seed_dir)
shutil.copyfile(f'{SRC}/seed.json', f'{seed_dir}/seed.json')
shutil.copyfile(f'{SRC}/story.md', f'{seed_dir}/primary_text_excerpt.md')
files = {n: {'sha256': hashlib.sha256(open(f'{seed_dir}/{n}', 'rb').read()).hexdigest()} for n in ('seed.json', 'primary_text_excerpt.md')}
json.dump({'story_key': KEY, 'files': files}, open(f'{seed_dir}/SEED_PROVENANCE.json', 'w'))
r.E2E_RUN_ROOT = root
ctx = r.E2EContext(story_key=KEY, slug=KEY, run='run_sf_prod_01', mode='dry-run', run_root=root)
assert ctx.seed_dir == seed_dir, ctx.seed_dir
res = r.stage_seed_check(ctx)
print(json.dumps(res, ensure_ascii=False, indent=1))
seed = json.load(open(f'{SRC}/seed.json', encoding='utf-8'))
md = w.build_cp_checklist(seed, KEY, {s: '' for s in w.CHAIN_STAGES})
open(sys.argv[1], 'w', encoding='utf-8').write(md)
print('--- cp checklist chars', len(md))
# fail-closed: remove essentials -> must raise
bad = dict(seed)
bad.pop('source_essentials')
try:
    w.validate_source_essentials(bad, KEY, seed_dir)
    print('FAIL_CLOSED_NOT_RAISED')
except w.FamilyZSeedEssentialsStop as e:
    print('fail-closed OK:', str(e)[:90])
shutil.rmtree(root, ignore_errors=True)
