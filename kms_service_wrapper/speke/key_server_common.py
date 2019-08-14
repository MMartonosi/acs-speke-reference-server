class KeyCache:
    """
    This class is responsible for storing keys in the key cache (S3) and
    returning a URL that can return a specific key from the cache.
    """

    def __init__(self, keystore_bucket, client_url_prefix):
        self.keystore_bucket = keystore_bucket
        self.client_url_prefix = client_url_prefix

    def store(self, content_id, key_id, key_value):
        """
        Store a key into the cache (S3) using the content_id
        as a folder and key_id as the file
        """
        key = "{cid}/{kid}".format(cid=content_id, kid=key_id)
        s3_client = boto3.client('s3')
        # store the key file with public-read permissions
        # public bucket policy not required
        s3_client.put_object(Bucket=self.keystore_bucket, Key=key, Body=key_value)

    def url(self, content_id, key_id):
        """
        Return a URL that can be used to retrieve the
        specified key_id related to content_id
        """
        return "{}/{}/{}".format(self.client_url_prefix, content_id, key_id)
