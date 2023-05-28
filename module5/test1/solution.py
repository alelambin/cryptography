from Crypto.Hash import SHA256


message = b'Python'
digest = SHA256.new(message)
print(digest.digest())
