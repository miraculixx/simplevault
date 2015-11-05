import os
import shutil
from uuid import uuid4
from zipfile import ZipFile, BadZipfile

import tinys3

from simplevault.aes import AESCipher
from simplevault.util import urlretrieve


AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID') 
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT = os.environ.get('AWS_ENDPOINT', 's3-eu-west-1.amazonaws.com') 

class SimpleVault(object):
    """
    Simple file based vault system - store and deploy secrets, secured.
    
    With a 12-factor system where local storage is not persistent, there are
    no simple solutions to storing secrets, in particular if those secrets
    have to be accessible as actual files (such as certificates and key files). 
    While there are some distributed secret solutions (e.g. vaultproject), they have
    their own complexity that needs to be set up and managed.
    
    SimpleVault provides a straight forward, secure solution. Use it to
    create a secure vault file from a plain files directory, store the vault
    file on S3 and retrieve it back on a deployed instance.
    
    Features: 
    * Encrypts plain file directories into a AES-256 encrypted vault file
    * Decrypts vault files into plain files
    * Stores vault files in a local file directory or on s3
    * s3 files can be downloaded securely with only a download key distributed
      (no AWS keys need to be stored on the server)
    * Basic team support (ok for teams of 2-3 admins) 
    
    Usage:
    
    # local use
    vault = SimpleVault(location='/path/to/vault')  
    crypt = vault.make('myvault', '/path/to/source', upload=False)
    files = vault.unvault('myvault', '/path/to/target', download=False)
    
    # using with S3
    # -- standard aws setup
    $ export AWS_ACCESS_KEY_ID=
    $ export AWS_SECRET_ACCESS_KEY=
    $ export AWS_ENDPOINT=
    # -- SimpleVault settings
    $ export S3_VAULT_KEY=key to use for encryption/decryption
    $ export S3_VAULT_BUCKET=bucket name
    $ export S3_VAULT_PATH=path in bucket
    $ export S3_VAULT_USERAGENT=user agent set on S3 policy
    
    # s3 policy example
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "deny-other-actions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::<bucketname>/vault/*",
            "Condition": {
                "StringEquals": {
                    "aws:UserAgent": "some key value (e.g. uuid4)"
                }
            }
        },
    }    
    """
    def __init__(self, key=None, location=None, 
                 s3_bucket=None, s3_path=None,
                 s3_useragent=None):
        self.key = key or os.environ.get('S3_VAULT_KEY') or self.secret_key()
        self.s3_path = s3_path or os.environ.get('S3_VAULT_PATH')
        self.s3_bucket = s3_bucket or os.environ.get('S3_VAULT_BUCKET')
        self.s3_useragent = s3_useragent or os.environ.get('S3_VAULT_USERAGENT')
        self.location = location
        self.extracted_files = []
        os.makedirs(location) if not os.path.exists(location) else None
        
    def directories(self, name):
        vault_tmp = os.path.expanduser('%s/.vault/%s' % (self.location, name))
        vault_zip = os.path.expanduser('%s/_vault.zip' % vault_tmp)
        vault_crypt = os.path.expanduser('%s/_vault.crypt' % vault_tmp)
        os.makedirs(vault_tmp) if not os.path.exists(vault_tmp) else None
        os.makedirs(vault_tmp) if not os.path.exists(vault_tmp) else None
        return vault_tmp, vault_zip, vault_crypt
    
    def cleanup(self, name):
        # cleanup
        vault_tmp, vault_zip, vault_crypt = self.directories(name)
        os.remove(vault_zip)
        os.remove(vault_crypt)
        os.rmdir(vault_tmp)
        
    def make(self, name=None, src=None, include=None, upload=True):
        """
        Takes a directory, zips all files in it, encrypts the file
        and uploads it to the path (use s3://bucket/path). 
        
        If not provided the key is randomly generated and output as a result. 
        Use this key to decrypt the file.
        
        Uses $SHREBO_VAULTKEY if available.
        """
        assert self.key, "you have to give a key or set in S3_VAULT_KEY"
        assert name, "give a vault name"
        vault_tmp, vault_zip, vault_crypt = self.directories(name)
        try:
            os.remove(vault_zip)
            os.remove(vault_crypt)
        except:
            pass
        # create zip file
        self.zipfiles(src or self.location, vault_zip, 
                      exclude='.vault', 
                      include=include)
        with open(vault_zip) as vz, open(vault_crypt, 'w') as vc:
            zipped = vz.read()
            aes = AESCipher(self.key)
            c = aes.encrypt(zipped)
            vc.write(c)
        if upload:
            assert self.s3_path, "No s3_path specified"
            assert self.s3_bucket, "No s3_bucket specified"
            self.upload(vault_crypt, self.s3_bucket, self.s3_file(name))
        return vault_crypt 
            
    def unvault(self, name, target=None, download=True):
        assert self.key, "you have to give a key or set in $VAULT_KEY"
        assert name, "give a vault name"
        vault_tmp, vault_zip, vault_crypt = self.directories(name)
        if download:
            assert self.s3_path, "No s3_path specified"
            assert self.s3_bucket, "No s3_bucket specified"
            assert self.s3_useragent, "you need to provide $S3_VAULT_USERAGENT"
            self.download(self.s3_bucket, self.s3_file(name), vault_crypt)
            assert os.path.exists(vault_crypt), "Download failed for %s" % self.s3_file(name)
        with open(vault_zip, 'w') as vz, open(vault_crypt) as vc:
            c = vc.read()
            aes = AESCipher(self.key)
            plain = aes.decrypt(c)
            vz.write(plain)
        try:
            zipf = ZipFile(vault_zip)
            zipf.extractall(target or self.location)
        except BadZipfile as e:
            raise BadZipfile('Could not extract %s. Did you set the key?' % vault_crypt)
        members = [os.path.join(target or self.location, member) 
                   for member in zipf.namelist()]
        self.extracted_files.extend(members)
        self.cleanup(name)
        return members
    
    def s3_file(self, name):
        return os.path.join(self.s3_path, '%s.crypt' % name).replace('//', '/')
            
    def upload(self, source, bucket, path):
        connection = tinys3.Connection(AWS_ACCESS_KEY, 
                        AWS_SECRET_ACCESS_KEY,
                        tls=True, endpoint=AWS_ENDPOINT)
        with open(source) as f:
            connection.upload(path, f, bucket=bucket)
         
    def download(self, bucket, path, localfile):
        s3_url = "https://%s/%s/%s" % (AWS_ENDPOINT, bucket, path)
        assert self.s3_useragent, "require $S3_VAULT_USERAGENT"
        urlretrieve(s3_url, localfile, 
                    headers=('User-agent', self.s3_useragent))
        
    def zipfiles(self, source, target, exclude=None, include=None):
        with open(target, 'w') as zipf:
            zipfile = ZipFile(zipf, 'w')
            for dir, dirs, files in os.walk(source):
                if exclude in dir:
                    continue
                for filename in files:
                    if not include or include in filename: 
                        fullpath = os.path.join(dir, filename)
                        member = os.path.join(dir.replace(source, ''), filename)
                        zipfile.write(fullpath, member)
            zipfile.close()
            
    def destroy(self, name):
        """
        destroy all files ever written
        """
        vault_tmp, vault_zip, vault_crypt = self.directories(name)
        os.remove(vault_zip)
        os.remove(vault_crypt)
        for member in self.extracted_files:
            os.remove(member)
        shutil.rmtree(vault_tmp)
        
    def secret_key(self, bytes=16):
        return os.urandom(16).encode('hex')