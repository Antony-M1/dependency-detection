# 🔹 google-auth-httplib2 — Summary
It's a bridge between google-auth and httplib2.

Lets you use google-auth credentials (like service accounts or OAuth2) with libraries that rely on httplib2, such as google-api-python-client.

🔹 How it uses google-auth
It relies on google-auth to handle the actual authentication (tokens, credentials, etc.).

google-auth-httplib2 just helps apply those credentials to HTTP requests made using httplib2.

```
python main.py --package-name google-auth-httplib2 --prime-package google-auth,cachetools,pyasn1,pyasn1_modules,rsa,six
```