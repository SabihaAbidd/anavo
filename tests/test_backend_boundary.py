"""Prove backend imports and required test discovery work when Streamlit is unavailable."""
import subprocess
import sys
import unittest
from pathlib import Path


class BackendBoundaryTests(unittest.TestCase):
    def test_runtime_and_test_discovery_without_streamlit(self):
        code=r'''
import importlib.abc,importlib.util,sys,unittest
class NoStreamlit(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0]=='streamlit':
            raise ImportError('Streamlit intentionally unavailable during backend isolation test')
sys.meta_path.insert(0,NoStreamlit())
from backend.schemas import ScenarioInput,OptimizeRequest
from backend.service import optimize
from src.scenarios import presets
from src.evaluation import environment_versions
result=optimize(OptimizeRequest(scenario=ScenarioInput.from_domain(presets()['Evening backup'])))
assert result.result.allocation.objective_value==24
assert 'streamlit' not in environment_versions()
if importlib.util.find_spec('fastapi'):
    from backend.main import app
suite=unittest.defaultTestLoader.discover('tests',top_level_dir='.')
def ids(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite): yield from ids(item)
        else: yield item.id()
names=list(ids(suite))
assert names
assert not any('DashboardTests' in name or 'legacy_demo' in name or '_FailedTest' in name for name in names),names
assert not any(name=='streamlit' or name.startswith('streamlit.') for name in sys.modules)
print('Backend/classical service and required test discovery passed with Streamlit imports blocked')
'''
        result=subprocess.run([sys.executable,"-c",code],cwd=Path(__file__).resolve().parent.parent,
                              capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__=="__main__": unittest.main()
