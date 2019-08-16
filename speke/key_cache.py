class KeyCache:
    """
    This class is responsible for storing keys in the object storage service (OSS) and
    returning a URL that can return a specific key from the cache.
    """

    def store(self, content_id, key_id, key_value):
        """
        Store a key into the cache (OSS) using the content_id as a folder and
        key_id as the file.
        """
        from services.oss.wrapper import acs_oss_create_secret

        key = f"{content_id}/{key_id}"
        acs_oss_create_secret(key, key_value)

    def url(self, content_id, key_id):
        """
        Return a URL that can be used to retrieve the
        specified key_id related to content_id
        """
        return f"/{content_id}/{key_id}"
