# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from Snekmer.SnekmerImpl import Snekmer
from Snekmer.SnekmerServer import MethodContext
from Snekmer.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class SnekmerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('Snekmer'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'Snekmer',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = Snekmer(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_SnekmerSearch_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    # 66073/19/1 is Shewanella_oneidensis_MR-1
    # 66073/2/1 is Escherichia_coli_K-12_MG1655
    def test_run_Snekmer_search(self):
        ref = "66073/19/1"
        ret = self.serviceImpl.run_Snekmer_search(
            self.ctx,
            {
             'workspace_name': self.wsName,
             'object_ref': ref,
             'k': 12,
             'alphabet': "hydro",
             'min_rep_thresh': 1,
             'processes': 4
             }
        )
        # print(result)
