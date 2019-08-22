import base64
import secrets
import xml.etree.ElementTree as ET

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# HLS_AES_128_SYSTEM_ID is not an official system ID
HLS_AES_128_SYSTEM_ID = "81376844-f976-481e-a84e-cc25d39b0b33"
HLS_SAMPLE_AES_SYSTEM_ID = "94ce86fb-07ff-4f43-adb8-93d2fa968ca2"

# settings for HLS
HLS_AES_128_KEY_FORMAT = ""  # 'identity'
HLS_AES_128_KEY_FORMAT_VERSIONS = ""  # '1'
HLS_SAMPLE_AES_KEY_FORMAT = "com.apple.streamingkeydelivery"
HLS_SAMPLE_AES_KEY_FORMAT_VERSIONS = "1"

# globals for encrypted document responses
DOCUMENT_KEY_SIZE = 32
HMAC_KEY_SIZE = 64
RANDOM_IV_SIZE = 16


class ServerResponseBuilder:
    def __init__(self, request_body, cache, generator):
        self.error_message = ""
        self.cache = cache
        self.generator = generator
        self.root = ET.fromstring(request_body)
        self.document_key = None
        self.hmac_key = None
        self.public_key = None
        self.use_playready_content_key = False
        ET.register_namespace("cpix", "urn:dashif:org:cpix")
        ET.register_namespace("pskc", "urn:ietf:params:xml:ns:keyprov:pskc")
        ET.register_namespace("speke", "urn:aws:amazon:com:speke")
        ET.register_namespace("ds", "http://www.w3.org/2000/09/xmldsig#")
        ET.register_namespace("enc", "http://www.w3.org/2001/04/xmlenc#")

    def get_response(self):
        self.fill_request()
        return ET.tostring(self.root).decode(), {"Content-Type": "text/xml"}

    def fill_request(self):
        """
        Fill the XML document with data about the requested keys.
        """
        content_id = self.root.get("id")
        # self.use_playready_content_key = False
        system_ids = {}
        # check whether to perform CPIX 2.0 document encryption
        encrypted_response_recipients = self.root.findall(
            "./{urn:dashif:org:cpix}DeliveryDataList/{urn:dashif:org:cpix}DeliveryData"
        )
        if encrypted_response_recipients:
            # print("ENCRYPTED-RESPONSE")
            # generate a random document key and HMAC key ?
            self.document_key = secrets.token_bytes(DOCUMENT_KEY_SIZE)
            self.hmac_key = secrets.token_bytes(HMAC_KEY_SIZE)
            backend = default_backend()
            for delivery_data in encrypted_response_recipients:
                delivery_key = delivery_data.find("./{urn:dashif:org:cpix}DeliveryKey")
                x509data = delivery_key.find(
                    "./{http://www.w3.org/2000/09/xmldsig#}X509Data"
                )
                x509cert = x509data.find(
                    "./{http://www.w3.org/2000/09/xmldsig#}X509Certificate"
                )
                cert = x509.load_der_x509_certificate(
                    base64.b64decode(x509cert.text), backend
                )
                public_key = cert.public_key()
                self.public_key = x509cert.text
                asym_padder = asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None,
                )
                # encrypt the document and HMAC keys using the x509 public key
                encoded_document_key = public_key.encrypt(
                    self.document_key, asym_padder
                )
                encoded_hmac_key = public_key.encrypt(self.hmac_key, asym_padder)
                document_key_leaf = ET.SubElement(
                    delivery_data, "{urn:dashif:org:cpix}DocumentKey"
                )
                document_key_leaf.set(
                    "Algorithm", "http://www.w3.org/2001/04/xmlenc#aes256-cbc"
                )
                data_leaf = ET.SubElement(
                    document_key_leaf, "{urn:dashif:org:cpix}Data"
                )
                secret_leaf = ET.SubElement(
                    data_leaf, "{urn:ietf:params:xml:ns:keyprov:pskc}Secret"
                )
                self.insert_encrypted_value(
                    secret_leaf,
                    "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p",
                    base64.b64encode(encoded_document_key).decode("utf-8"),
                )
                mac_method = ET.SubElement(
                    delivery_data, "{urn:dashif:org:cpix}MACMethod"
                )
                mac_method.set(
                    "Algorithm", "http://www.w3.org/2001/04/xmldsig-more#hmac-sha512"
                )
                mac_method_key = ET.SubElement(
                    mac_method, "{urn:dashif:org:cpix}Key"
                )
                self.insert_encrypted_value(
                    mac_method_key,
                    "http://www.w3.org/2001/04/xmlenc#rsa-oaep-mgf1p",
                    base64.b64encode(encoded_hmac_key).decode("utf-8"),
                )

        for drm_system in self.root.findall(
                "./{urn:dashif:org:cpix}DRMSystemList/{urn:dashif:org:cpix}DRMSystem"
        ):
            kid = drm_system.get("kid")
            system_id = drm_system.get("systemId")
            system_ids[system_id] = kid
            # print("SYSTEM-ID {}".format(system_id.lower()))
            self.fixup_document(drm_system, system_id, content_id, kid)

        for content_key in self.root.findall(
                "./{urn:dashif:org:cpix}ContentKeyList/{urn:dashif:org:cpix}ContentKey"
        ):
            kid = content_key.get("kid")
            init_vector = content_key.get("explicitIV")
            data = ET.SubElement(content_key, "{urn:dashif:org:cpix}Data")
            secret = ET.SubElement(
                data, "{urn:ietf:params:xml:ns:keyprov:pskc}Secret"
            )
            # HLS SAMPLE AES Only
            if (
                    init_vector is None
                    and system_ids.get(HLS_SAMPLE_AES_SYSTEM_ID, False) == kid
            ):
                content_key.set(
                    "explicitIV",
                    base64.b64encode(self.generator.key(content_id, kid)).decode(
                        "utf-8"
                    ),
                )
            key_bytes = self.generator.key(content_id, kid)
            self.cache.store(content_id, kid, key_bytes)
            if encrypted_response_recipients:
                padder = padding.PKCS7(algorithms.AES.block_size).padder()
                padded_data = padder.update(key_bytes) + padder.finalize()
                random_iv = secrets.token_bytes(RANDOM_IV_SIZE)
                cipher = Cipher(
                    algorithms.AES(self.document_key),
                    modes.CBC(random_iv),
                    backend=backend,
                )
                encryptor = cipher.encryptor()
                encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
                cipher_data = random_iv + encrypted_data
                encrypted_string = base64.b64encode(cipher_data).decode("utf-8")
                self.insert_encrypted_value(
                    secret,
                    "http://www.w3.org/2001/04/xmlenc#aes256-cbc",
                    encrypted_string,
                )
            else:
                plain_value = ET.SubElement(
                    secret, "{urn:ietf:params:xml:ns:keyprov:pskc}PlainValue"
                )
                plain_value.text = base64.b64encode(key_bytes).decode("utf-8")

    def fixup_document(self, drm_system, system_id, content_id, kid):
        if system_id.lower() == HLS_AES_128_SYSTEM_ID.lower():
            ext_x_key = self.cache.url(content_id, kid)
            drm_system.find("{urn:dashif:org:cpix}URIExtXKey").text = base64.b64encode(
                ext_x_key.encode("utf-8")
            ).decode("utf-8")
            drm_system.find(
                "{urn:aws:amazon:com:speke}KeyFormat"
            ).text = base64.b64encode(HLS_AES_128_KEY_FORMAT.encode("utf-8")).decode(
                "utf-8"
            )
            drm_system.find(
                "{urn:aws:amazon:com:speke}KeyFormatVersions"
            ).text = base64.b64encode(
                HLS_AES_128_KEY_FORMAT_VERSIONS.encode("utf-8")
            ).decode(
                "utf-8"
            )
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}ProtectionHeader")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}PSSH")
        elif system_id.lower() == HLS_SAMPLE_AES_SYSTEM_ID.lower():
            ext_x_key = self.cache.url(content_id, kid)
            drm_system.find("{urn:dashif:org:cpix}URIExtXKey").text = base64.b64encode(
                ext_x_key.encode("utf-8")
            ).decode("utf-8")
            drm_system.find(
                "{urn:aws:amazon:com:speke}KeyFormat"
            ).text = base64.b64encode(HLS_SAMPLE_AES_KEY_FORMAT.encode("utf-8")).decode(
                "utf-8"
            )
            drm_system.find(
                "{urn:aws:amazon:com:speke}KeyFormatVersions"
            ).text = base64.b64encode(
                HLS_SAMPLE_AES_KEY_FORMAT_VERSIONS.encode("utf-8")
            ).decode(
                "utf-8"
            )
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}ContentProtectionData")
            self.safe_remove(drm_system, "{urn:aws:amazon:com:speke}ProtectionHeader")
            self.safe_remove(drm_system, "{urn:dashif:org:cpix}PSSH")
        else:
            raise Exception("Invalid system ID {}".format(system_id))

    def insert_encrypted_value(self, element, encryption_algorithm, encrypted_string):
        encrypted_value = ET.SubElement(
            element, "{urn:ietf:params:xml:ns:keyprov:pskc}EncryptedValue"
        )
        encryption_method = ET.SubElement(
            encrypted_value, "{http://www.w3.org/2001/04/xmlenc#}EncryptionMethod"
        )
        encryption_method.set("Algorithm", encryption_algorithm)
        cipher_data = ET.SubElement(
            encrypted_value, "{http://www.w3.org/2001/04/xmlenc#}CipherData"
        )
        cipher_value = ET.SubElement(
            cipher_data, "{http://www.w3.org/2001/04/xmlenc#}CipherValue"
        )
        cipher_value.text = encrypted_string
        # calculate and set MAC using HMAC-SHA512 over data in CipherValue
        if not self.hmac_key:
            raise Exception("Missing HMAC key")
        value_mac = ET.SubElement(
            element, "{urn:ietf:params:xml:ns:keyprov:pskc}ValueMAC"
        )
        hmac_instance = hmac.HMAC(
            self.hmac_key, hashes.SHA512(), backend=default_backend()
        )
        hmac_instance.update(base64.b64decode(encrypted_string))
        value_mac.text = base64.b64encode(hmac_instance.finalize()).decode("utf-8")

    def safe_remove(self, element, match):
        if element.find(match):
            element.remove(match)
