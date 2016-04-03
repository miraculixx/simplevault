'''
Created on 7 Jan 2016

@author: patrick
'''
import os
import unittest

from simplevault.vault import SimpleVault


TEST_PATH = '/tmp/simplevault/testing/'
S3_MOCK_PATH = '/tmp/simplevault/testing/'


class SimpleVaultMockS3(SimpleVault):

    """ mock s3 upload and download """
    def upload(self, source, bucket, path):
        s3path = os.path.join(S3_MOCK_PATH, bucket)
        s3file = os.path.join(s3path, path)
        if not os.path.exists(s3path):
            os.makedirs(os.path.dirname(s3file))
        with open(source) as s, open(s3file, 'w') as f:
            data = s.read()
            f.write(data)

    def download(self, bucket, path, localfile):
        s3file = os.path.join(S3_MOCK_PATH, bucket, path)
        with open(s3file) as s, open(localfile) as f:
            data = s.read()
            f.write(data)


class Test(unittest.TestCase):

    def setUp(self):
        self.make_test_files()
        os.environ['S3_VAULT_KEY'] = 'somekey'
        os.environ['S3_VAULT_BUCKET'] = 's3mock'
        self.s3bucket = 's3mock'

    def get_simplevault(self, *args, **kwargs):
        kwargs = kwargs or self.get_vault_kwargs()
        return SimpleVaultMockS3(**kwargs)

    def test_make_vault(self):
        vault = self.get_simplevault()
        vault.make('testvault', TEST_PATH, upload=True)
        s3_vault = os.environ.get('S3_VAULT_PATH', 'vault')
        s3_file = os.path.join(S3_MOCK_PATH, self.s3bucket, s3_vault, 'testvault.crypt')
        self.assertTrue(os.path.exists(s3_file))

    def make_test_files(self):
        if os.path.exists(TEST_PATH):
            os.removedirs(TEST_PATH)
        os.makedirs(TEST_PATH)
        test_file = os.path.join(TEST_PATH, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('the secret is secret')

    def get_vault_kwargs(self):
        return {
            'key': 'somekey',
            'location': TEST_PATH,
            's3_path': 'vault',
            's3_useragent': 'someuseragent',
        }


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
