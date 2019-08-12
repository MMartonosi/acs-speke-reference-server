from aliyunsdkvod.request.v20170321 import SubmitTranscodeJobsRequest
from aliyunsdkkms.request.v20160120 import GenerateDataKeyRequest
from aliyunsdkcore.http import protocol_type
import json
from aliyunsdkcore.client import AcsClient

def build_encrypt_config(clt):
    try:
        request = GenerateDataKeyRequest.GenerateDataKeyRequest()
        request.set_KeyId('<serviceKey>')
        request.set_KeySpec('AES_128')
        request.set_protocol_type(protocol_type.HTTPS)
        request.set_accept_format('JSON')
        response = json.loads(clt.do_action_with_exception(request))

        decryptKeyUri = 'http://decrypt.demo.com/decrypt?' + 'Ciphertext=' + response[
            'CiphertextBlob']
        return {'DecryptKeyUri': decryptKeyUri, 'KeyServiceType': 'KMS',
                'CipherText': response['CiphertextBlob']}
    except Exception as e:
        print(e)
        return None


request = SubmitTranscodeJobsRequest.SubmitTranscodeJobsRequest()
