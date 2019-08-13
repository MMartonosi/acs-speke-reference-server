Service used as to create, store and distribute keys which will be used by rhb?
------------

For keys generation and decrypting this service encapsulated alibaba KMS service to generate data keys and decrypt cipher keys.


To store cipher keys used for content encryption OSS API is used.


To run example demo:
- ``python demo.py encrypt [text]``
- ``python demo.py decrypt [encrypted-text]``
