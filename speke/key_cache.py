from speke.services.oss import acs_oss_create_secret


class KeyCache:
    def store(self, content_id, key_id, key_value):
        key = f"{content_id}/{key_id}"
        acs_oss_create_secret(key, key_value)

    def url(self, content_id, key_id):
        return f"/{content_id}/{key_id}"
