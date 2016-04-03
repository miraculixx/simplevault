import argparse
import sys


def makevault(site=None, location='~/.vault', s3bucket='', s3path='vault', 
              files=None, key=None):
    from simplevault import SimpleVault
    vault = SimpleVault(s3_bucket=s3bucket, s3_path=s3path,
                        location=location, key=key)
    crypt = vault.make(site, include=files, upload=True)
    print "Ok, created %s and uploaded to s3://%s/%s" % (crypt, s3bucket, s3path)
    print "export S3_VAULT_KEY=%s" % vault.key
    
def unvault(site=None, location='~/.vault', s3bucket='', s3path='vault', 
            files=None, key=None):
    from simplevault import SimpleVault
    vault = SimpleVault(s3_bucket=s3bucket, s3_path=s3path,
                        location=location, key=key)
    files = vault.unvault(site, download=True)
    print "Extracted %s" % files
    
def console_mkvault():
    if not len(sys.argv) == 4:
        print "mkvault name location bucket/path"
        exit(1)
    bucket, path = sys.argv[3].split('/', 1)
    main('--write',
         '--name=%s' % sys.argv[1], 
         '--location=%s' % sys.argv[2],
         '--s3bucket=%s' % bucket,
         '--path=%s' % path)
    
def console_unvault():
    if not len(sys.argv) == 4:
        print "unvault name bucket/path location"
        exit(1)
    bucket, path = sys.argv[2].split('/', 1)
    main('--extract',
         '--name=%s' % sys.argv[1],
         '--s3bucket=%s' % bucket, 
         '--path=%s' % path,
         '--location=%s' % sys.argv[3],)
    
def console_simplevault():
    main(*sys.argv[1:])
    
def main(*realargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', "--write", action='store_true', 
                        help="write vault file")
    parser.add_argument('-x', "--extract", action='store_true', 
                        help="extract files")
    parser.add_argument('-b', "--s3bucket", action='store', 
                        help="s3 bucket")
    parser.add_argument('-p', "--path", action='store', default=None,
                        help="path (s3 path or local path if -N)")
    parser.add_argument('-l', "--location", action='store', 
                        help="location", required=True)
    parser.add_argument('-n', "--name", action='store', 
                        help="vault name", required=True)
    parser.add_argument('-N', "--noremote", action='store_true', default=False, 
                        help="don't use s3, locally only")
    parser.add_argument('-k', "--key", action='store', 
                        help="key to encrypt/decrypt. defaults to S3_VAULT_KEY")
    parser.add_argument('-i', "--include", action='store', 
                        help="file pattern for files to include (encryption)")
    args = parser.parse_args(realargs)

    if args.write:
        from simplevault import SimpleVault
        vault = SimpleVault(s3_bucket=args.s3bucket, s3_path=args.path,
                            location=args.location, key=args.key)
        crypt = vault.make(args.name, include=args.include, 
                           upload=not args.noremote)
        if not args.noremote:
            print "[INFO]  created %s and uploaded to s3://%s/%s" % (crypt, 
                                                                 args.s3bucket, 
                                                                 args.path)
        else:
            print "[INFO] created %s and stored in %s" % (crypt, args.path)
        print "[WARN] Extract using export S3_VAULT_KEY=%s" % vault.key
    elif args.extract:
        from simplevault import SimpleVault
        vault = SimpleVault(s3_bucket=args.s3bucket, s3_path=args.path,
                            location=args.location, key=args.key)
        files = vault.unvault(args.name, target=args.location or args.path, 
                              download=not args.noremote)
        print "Extracted %s" % files
    else:
        print "[ERROR] Either --write or --extract must be used"


if __name__ == '__main__':
    main(*sys.argv[1:])