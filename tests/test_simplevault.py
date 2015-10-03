import os
from subprocess import call
from unittest.case import TestCase
from uuid import uuid4

from simplevault.vault import SimpleVault
from zipfile import BadZipfile


VAULT_PATH='/tmp/simplevault'
VAULT_PATH2 = '%sOther' % VAULT_PATH
        
S3_VAULT_BUCKET = os.environ.get('TEST_S3_VAULT_BUCKET')
S3_VAULT_USERAGENT=os.environ.get('TEST_S3_VAULT_USERAGENT')
S3_VAULT_PATH = 'vault'

class SimpleVaultTests(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        
    def tearDown(self):
        call(('rm -rf %s' % VAULT_PATH).split(' '))
        
    def test_make_unvault(self):
        # create a vault with one file
        plain = "This is a secret"
        key = uuid4().hex
        vault = SimpleVault(key, location=VAULT_PATH)
        secret_file = '%s/secret.txt' % VAULT_PATH
        with open(secret_file, 'w') as f:
            f.write(plain)
        crypt = vault.make('test', VAULT_PATH, upload=False)
        self.assertTrue(os.path.exists(os.path.join(VAULT_PATH, '.vault')))
        self.assertTrue(os.path.exists(crypt))
        # make sure we have an encrypted file
        with open(crypt) as f:
            self.assertNotEqual(f.read(), plain)
        # see if we can unvault
        os.remove(secret_file)
        files = vault.unvault('test', download=False)
        self.assertIn(secret_file, files)
        self.assertTrue(os.path.exists(secret_file))
        with open(secret_file) as f:
            self.assertEqual(plain, f.read())
            
    def test_make_unvault_complex(self):
        # create a vault with one file
        plain = "This is a secret"
        key = uuid4().hex
        vault = SimpleVault(key, location=VAULT_PATH)
        os.makedirs(os.path.join(VAULT_PATH, 'sub'))
        secret_file1 = '%s/secret.txt' % VAULT_PATH
        secret_file2 = '%s/sub/secret.txt' % VAULT_PATH
        secret_files = [secret_file1, secret_file2]
        for fn in secret_files:
            with open(fn, 'w') as f:
                f.write(plain)
        vault.make('test', VAULT_PATH, upload=False)
        self.assertTrue(os.path.exists(os.path.join(VAULT_PATH, '.vault')))
        # see if we can unvault
        for fn in secret_files:
            os.remove(fn)
        files = vault.unvault('test', download=False)
        print files
        for fn in secret_files:
            self.assertIn(fn, files)
            self.assertTrue(os.path.exists(fn))
            with open(fn) as f:
                self.assertEqual(plain, f.read())
    
    def test_make_unvault_s3(self):
        assert S3_VAULT_BUCKET, "export TEST_S3_VAULT_BUCKET=<your bucket>" 
        assert S3_VAULT_USERAGENT, "export TEST_S3_VAULT_USERAGENT=<your useragent>"
        # create a vault with one file
        plain = "This is a secret"
        key = uuid4().hex
        vault = SimpleVault(key, location=VAULT_PATH,
                            s3_bucket=S3_VAULT_BUCKET, 
                            s3_path=S3_VAULT_PATH,
                            s3_useragent=S3_VAULT_USERAGENT)
        secret_file = '%s/secret.txt' % VAULT_PATH
        with open(secret_file, 'w') as f:
            f.write(plain)
        crypt = vault.make('test', VAULT_PATH, upload=True)
        self.assertTrue(os.path.exists(os.path.join(VAULT_PATH, '.vault')))
        self.assertTrue(os.path.exists(crypt))
        # make sure we have an encrypted file
        with open(crypt) as f:
            self.assertNotEqual(f.read(), plain)
        # see if we can unvault
        os.remove(secret_file)
        os.remove(crypt)
        files = vault.unvault('test', download=True)
        self.assertIn(secret_file, files)
        self.assertTrue(os.path.exists(secret_file))
        with open(secret_file) as f:
            self.assertEqual(plain, f.read())
            
    def test_make_unvault_different_path(self):
        # create a vault with one file
        plain = "This is a secret"
        key = uuid4().hex
        vault = SimpleVault(key, location=VAULT_PATH)
        secret_file = '%s/secret.txt' % VAULT_PATH
        secret_file2 = '%s/secret.txt' % VAULT_PATH2
        with open(secret_file, 'w') as f:
            f.write(plain)
        crypt = vault.make('test', VAULT_PATH, upload=False)
        self.assertTrue(os.path.exists(os.path.join(VAULT_PATH, '.vault')))
        self.assertTrue(os.path.exists(crypt))
        # make sure we have an encrypted file
        with open(crypt) as f:
            self.assertNotEqual(f.read(), plain)
        # see if we can unvault
        os.remove(secret_file)
        files = vault.unvault('test', target=VAULT_PATH2, download=False)
        self.assertIn(secret_file, files)
        self.assertTrue(os.path.exists(secret_file2))
        with open(secret_file2) as f:
            self.assertEqual(plain, f.read())
            
    def test_make_unvault_different_path_s3(self):
        assert S3_VAULT_BUCKET, "export TEST_S3_VAULT_BUCKET=<your bucket>" 
        assert S3_VAULT_USERAGENT, "export TEST_S3_VAULT_USERAGENT=<your useragent>"
        # create a vault with one file
        plain = "This is a secret"
        key = uuid4().hex
        vault = SimpleVault(key, location=VAULT_PATH,
                            s3_bucket=S3_VAULT_BUCKET, 
                            s3_path=S3_VAULT_PATH,
                            s3_useragent=S3_VAULT_USERAGENT)
        secret_file = '%s/secret.txt' % VAULT_PATH
        secret_file2 = '%s/secret.txt' % VAULT_PATH2
        with open(secret_file, 'w') as f:
            f.write(plain)
        crypt = vault.make('test', VAULT_PATH, upload=True)
        self.assertTrue(os.path.exists(os.path.join(VAULT_PATH, '.vault')))
        self.assertTrue(os.path.exists(crypt))
        # make sure we have an encrypted file
        with open(crypt) as f:
            self.assertNotEqual(f.read(), plain)
        # see if we can unvault into another local path
        os.remove(secret_file)
        vault = SimpleVault(key, location=VAULT_PATH2,
                            s3_bucket=S3_VAULT_BUCKET, 
                            s3_path=S3_VAULT_PATH,
                            s3_useragent=S3_VAULT_USERAGENT)
        files = vault.unvault('test', target=VAULT_PATH2, download=True)
        self.assertIn(secret_file2, files)
        self.assertTrue(os.path.exists(secret_file2))
        with open(secret_file2) as f:
            self.assertEqual(plain, f.read())
            
    def test_make_unvault_invalidkey(self):
        # create a vault with one file
        plain = "This is a secret"
        key = uuid4().hex
        vault = SimpleVault(key, location=VAULT_PATH)
        secret_file = '%s/secret.txt' % VAULT_PATH
        with open(secret_file, 'w') as f:
            f.write(plain)
        crypt = vault.make('test', VAULT_PATH, upload=False)
        self.assertTrue(os.path.exists(os.path.join(VAULT_PATH, '.vault')))
        self.assertTrue(os.path.exists(crypt))
        # make sure we have an encrypted file
        with open(crypt) as f:
            self.assertNotEqual(f.read(), plain)
        # see if we can unvault with the **wrong key**
        # for simplicity we simply reverse the key string
        vault = SimpleVault(key[-1:], location=VAULT_PATH)
        os.remove(secret_file)
        with self.assertRaises(BadZipfile):
            files = vault.unvault('test', download=False)
        self.assertFalse(os.path.exists(secret_file))
        