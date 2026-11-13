import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

spec=importlib.util.spec_from_file_location('quorum_test_app',Path(__file__).resolve().parents[1]/'aggregator/aggregator.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REAL_CLIENT=httpx.AsyncClient

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.key=Path(self.tmp.name)/'key';self.key.write_text('test-key')
        self.available=m.definitions()
        self.calls=[]
        self.backend_status=200
        self.output='A concise technical answer.'
        def backend(request):
            if request.url.path=='/v1/models':
                return httpx.Response(200,json={'data':[{'id':m.server_id(e),'loaded':True} for e in self.available]})
            payload=json.loads(request.content);self.calls.append(payload)
            if payload.get('stream'):
                return httpx.Response(self.backend_status,content=b'data: {"choices":[{"delta":{"content":"1"}}]}\n\ndata: [DONE]\n\n')
            return httpx.Response(self.backend_status,json={'choices':[{'message':{'content':self.output},'finish_reason':'stop'}]})
        self.transport=httpx.MockTransport(backend)
        self.p1=patch.object(m,'KEY_FILE',self.key);self.p1.start()
        self.p2=patch.object(m.httpx,'AsyncClient',lambda **kw:REAL_CLIENT(transport=self.transport,**kw));self.p2.start()
        self.client=TestClient(m.app)
    def tearDown(self):
        self.client.close();self.p2.stop();self.p1.stop();self.tmp.cleanup()
    def chat(self,text,model='quorum',**kwargs):
        return self.client.post('/v1/chat/completions',headers={'Authorization':'Bearer test-key'},json={'model':model,'messages':[{'role':'user','content':text}],**kwargs})
    def test_simple_question_only_one_model_call(self):
        r=self.chat('Combien fait 2/2 ?',max_tokens=8)
        self.assertEqual(r.status_code,200);self.assertEqual(len(self.calls),1)
        self.assertEqual(r.json()['x_quorum']['mode'],'direct')
        self.assertEqual(self.calls[0]['max_tokens'],8)
    def test_technical_three_reviews_and_one_synthesis(self):
        r=self.chat('Comment corriger un bug Python ?',max_tokens=120)
        self.assertEqual(r.status_code,200);self.assertEqual(len(self.calls),4)
        self.assertEqual(r.json()['x_quorum']['candidates'],3)
        self.assertIn('Python',self.calls[0]['messages'][0]['content'])
        self.assertIn('DRAFT REVIEWS',self.calls[-1]['messages'][0]['content'])
    def test_24_experts_do_not_overflow_letter_labels(self):
        r=self.chat('Review the architecture',model='quorum-deep')
        self.assertEqual(r.status_code,200);self.assertEqual(len(self.calls),25)
        self.assertEqual(r.json()['x_quorum']['candidates'],24)
        self.assertIn('expert-23',self.calls[-1]['messages'][0]['content'])
    def test_stream_is_direct_for_arithmetic(self):
        r=self.chat('2/2',stream=True)
        self.assertEqual(r.status_code,200);self.assertIn('[DONE]',r.text)
        self.assertEqual(len(self.calls),1);self.assertEqual(r.headers['x-quorum-mode'],'direct')
    def test_stream_retains_backend_failure_status(self):
        self.backend_status=503
        r=self.chat('2/2',stream=True)
        self.assertEqual(r.status_code,503)
    def test_tools_do_not_fan_out(self):
        r=self.chat('Debug Python',tools=[{'type':'function','function':{'name':'read_file'}}])
        self.assertEqual(r.status_code,200);self.assertEqual(len(self.calls),1)
        self.assertIn('tools',self.calls[0])
    def test_no_loaded_models_not_ready(self):
        self.available=[]
        self.assertEqual(self.chat('2/2').status_code,503)
        self.assertEqual(self.client.get('/health').json()['status'],'degraded')
    def test_authentication_is_required_even_when_key_missing(self):
        self.key.unlink()
        self.assertEqual(self.chat('2/2').status_code,503)
    def test_expert_catalog_includes_roles_and_placement(self):
        r=self.client.get('/experts',headers={'Authorization':'Bearer test-key'})
        self.assertEqual(len(r.json()['experts']),24)
        self.assertTrue(all(e['loaded'] and e['role'] and 'gpu' in e for e in r.json()['experts']))
    def test_long_review_fails_before_generation(self):
        r=self.chat('Python '+('x'*11000))
        self.assertEqual(r.status_code,413);self.assertEqual(len(self.calls),0)
    def test_invalid_messages_rejected(self):
        r=self.client.post('/v1/chat/completions',headers={'Authorization':'Bearer test-key'},json={'model':'quorum','messages':['bad']})
        self.assertEqual(r.status_code,400)
    def test_nemotron_defaults_to_final_answers_without_thinking(self):
        r=self.chat('What is 2+2?',model='expert-8')
        self.assertEqual(r.status_code,200)
        self.assertIs(self.calls[0]['enable_thinking'],False)
    def test_nemotron_respects_explicit_thinking(self):
        r=self.chat('What is 2+2?',model='expert-8',enable_thinking=True)
        self.assertEqual(r.status_code,200)
        self.assertIs(self.calls[0]['enable_thinking'],True)
    def test_technical_panel_varies_model_families(self):
        panel=m.pick_panel('Python bug',self.available)
        self.assertEqual(len({e['family'] for e in panel}),3)
    def test_roles_do_not_mutate_original_messages(self):
        original=[{'role':'system','content':'Answer in French'},{'role':'user','content':'Python'}]
        enriched=m.role_messages(original,'security')
        self.assertEqual(original[0]['content'],'Answer in French')
        self.assertIn('security',enriched[0]['content'])

if __name__=='__main__':unittest.main()
