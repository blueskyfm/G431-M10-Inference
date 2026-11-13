"""Restore one local GGUF per GPU. Uses existing Studio credentials; never prints them."""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
BASE = os.getenv('QUORUM_STUDIO', 'http://127.0.0.1:8888')
KEY = Path(os.getenv('QUORUM_KEY_FILE', '/home/unsloth/unsloth-m10/credentials/api-key.txt'))
CONFIG = ROOT / 'experts.json'

def api(path, body=None):
    headers = {'Authorization': 'Bearer '+KEY.read_text().strip(), 'Content-Type': 'application/json'}
    data = None if body is None else json.dumps(body).encode()
    with urllib.request.urlopen(urllib.request.Request(BASE+path, data=data, headers=headers), timeout=90) as response:
        return json.load(response)

def loaded():
    return {m['id'] for m in api('/v1/models').get('data', []) if m.get('loaded')}

def main():
    count = len(subprocess.check_output(['nvidia-smi','--query-gpu=index','--format=csv,noheader'], text=True, timeout=30).splitlines())
    config = json.loads(CONFIG.read_text())['experts']
    targets = [e for e in config if e['gpu'] < count]
    if not targets:
        raise RuntimeError('No configured GPUs found')
    for attempt in range(120):
        try:
            ready = loaded()
            break
        except Exception:
            if attempt == 119:
                raise
            time.sleep(5)
    pending = []
    for expert in targets:
        mid = expert.get('server_id', expert['id'])
        alias = Path('/home/unsloth/models/quorum') / (mid+'.gguf')
        model = Path('/home/unsloth/models') / expert['file']
        if not model.is_file():
            print('Waiting for verified model file: '+mid,flush=True)
            pending.append(mid)
            continue
        alias.parent.mkdir(parents=True, exist_ok=True)
        if alias.is_symlink():
            if alias.resolve() != model.resolve():
                raise RuntimeError('Existing alias differs: '+str(alias))
        elif alias.exists():
            raise RuntimeError('Refusing to replace regular file '+str(alias))
        else:
            alias.symlink_to(model)
        if mid in ready:
            print(mid+' already loaded', flush=True)
            continue
        print('Loading '+mid+' on GPU '+str(expert['gpu']), flush=True)
        api('/api/inference/load', {'model_path':str(alias), 'gpu_ids':[expert['gpu']], 'max_seq_length':8192, 'alongside':True, 'n_parallel':1, 'n_batch':256, 'n_ubatch':128, 'speculative_type':'off', 'llama_extra_args':['--threads','2','--threads-batch','2','--poll','0','--poll-batch','0']})
        for attempt in range(120):
            time.sleep(3)
            ready = loaded()
            if mid in ready:
                print(mid+' ready', flush=True)
                break
        else:
            raise RuntimeError('Load did not complete for '+mid)
    ready = loaded()
    missing = [e.get('server_id', e['id']) for e in targets if e.get('server_id', e['id']) not in ready]
    if missing:
        print('Pending experts: '+', '.join(missing),flush=True)
        raise SystemExit(1)
    print('READY '+str(len(targets))+'/'+str(len(targets))+' experts', flush=True)

if __name__ == '__main__':
    main()
