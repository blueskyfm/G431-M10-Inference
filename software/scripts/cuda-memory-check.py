import ctypes as C
import json
cuda=C.CDLL('libcuda.so.1')
def check(name,*args):
 r=getattr(cuda,name)(*args)
 if r:raise RuntimeError(f'{name}: CUDA error {r}')
check('cuInit',0)
n=C.c_int();check('cuDeviceGetCount',C.byref(n));print('CUDA devices:',n.value,flush=True)
size=1024*1024
src=(C.c_ubyte*size).from_buffer_copy(bytes(range(256))*(size//256))
dst=(C.c_ubyte*size)()
for idx in range(n.value):
 dev=C.c_int();ctx=C.c_void_p();mem=C.c_uint64();name=C.create_string_buffer(100)
 check('cuDeviceGet',C.byref(dev),idx);check('cuDeviceGetName',name,100,dev)
 check('cuCtxCreate_v2',C.byref(ctx),0,dev)
 try:
  check('cuMemAlloc_v2',C.byref(mem),C.c_size_t(size))
  try:
   check('cuMemcpyHtoD_v2',mem,C.cast(src,C.c_void_p),C.c_size_t(size))
   check('cuMemcpyDtoH_v2',C.cast(dst,C.c_void_p),mem,C.c_size_t(size))
   assert bytes(dst)==bytes(src),f'data mismatch GPU {idx}'
  finally:check('cuMemFree_v2',mem)
 finally:check('cuCtxDestroy_v2',ctx)
 print(json.dumps({'gpu':idx,'name':name.value.decode(),'copy_round_trip_bytes':size,'result':'PASS'}),flush=True)
