import base64
import pyaes


class AESCipher: 
    """
    implements an AES encoder that returns a base64 encoded
    ciphertext, and converts from a base64 encoded ciphertext
    back to cleartext.
    
    Use:
      aes = AESCipher(key)
      b64_cipher = aes.encrypt(plaintext)
      cleartext = aes.decrypt(b64_ciphe)
      assert cleartext == plaintext
    """
    def __init__(self, key):
        self.bs = 32
        if len(key) >= 32:
            self.key = key[:32]
        else:
            self.key = self._pad(key) 

    def encrypt(self, plaintext):
        cipher = pyaes.AESModeOfOperationCTR(self.key)
        ciphertext = cipher.encrypt(plaintext)
        return base64.encodestring(ciphertext)

    def decrypt(self, ciphertext):
        cipher = pyaes.AESModeOfOperationCTR(self.key)
        cleartext = cipher.decrypt(base64.decodestring(ciphertext))
        return cleartext

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]
    

if __name__ == '__main__':
    # test pure implementation
    from pyaes import AESModeOfOperationCTR as AES
    aes = AES('This_key_for_demo_purposes_only!')
    plaintext = 'thequickbrownfoxjumpsoverthelazydog'
    cipher = aes.encrypt(plaintext)
    # -- we have to reinitialize the AES to decrypt
    aes = AES('This_key_for_demo_purposes_only!')
    decrypt = aes.decrypt(cipher)
    assert decrypt == plaintext, "expected >%s<==>%s<" % (decrypt, plaintext)
    print "OK pure mode"
    # test wrapper 
    aes = AESCipher('testkey')
    plaintext = 'thequickbrownfoxjumpsoverthelazydog'
    cipher = aes.encrypt(plaintext)
    decrypt = aes.decrypt(cipher)
    assert decrypt == plaintext, "expected >%s<==>%s<" % (decrypt, plaintext)
    print "OK wrapped mode" 