Simple file based vault system 
-------------------------------
store and deploy secrets, secured.
    
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

```
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
```
