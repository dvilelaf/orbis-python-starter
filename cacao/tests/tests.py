import unittest
from datetime import datetime

from eth_account import Account
from eth_account.messages import encode_defunct
from bip44 import Wallet
from bip44.utils import get_eth_addr

from src.cacao import Cacao
from src.siwe import SiweMessage
from src.verification import EIP191Verifier


class TestCacao(unittest.TestCase):

    def test_conversion_siwe(self):
        siwe_message = SiweMessage(
            {
                "domain": "service.org",
                "address": "0x1b9Aceb609a62bae0c0a9682A9268138Faff4F5f",
                "statement": "I accept the ServiceOrg Terms of Service: https://service.org/tos",
                "uri": "did:key:z6MkrBdNdwUPnXDVD1DCxedzVVBpaGi8aSmoXFAeKNgtAer8",
                "version": "1",
                "nonce": "32891757",
                "issuedAt": "2021-09-30T16:25:24.000Z",
                "chainId": "1",
                "resources": [
                    "fs://Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu",
                    "https://example.com/my-web2-claim.json",
                    "ceramic://k2t6wyfsu4pg040dpjpbla1ybxof65baldb7fvmeam4m3n71q0w1nslz609u2d",
                ]
            }
        )

        cacao_object = Cacao()
        cacao_object.from_siwe_message(siwe_message)
        siwe_message_convert = cacao_object.to_siwe_message()
        self.assertEqual(siwe_message_convert, siwe_message)

    def test_create_and_verify_ethereum(self):
        issued_at = datetime.strptime("2021-10-14T07:18:41Z", "%Y-%m-%dT%H:%M:%SZ")
        mnemonic = "despair voyage estate pizza main slice acquire mesh polar short desk lyrics"
        wallet = Wallet(mnemonic)
        sk, pk = wallet.derive_account("eth", account=0)
        address = get_eth_addr(pk)
        siwe_message = SiweMessage(
            {
                "domain": "service.org",
                "address": address,
                "statement": "I accept the ServiceOrg Terms of Service: https://service.org/tos",
                "uri": "did:key:z6MkrBdNdwUPnXDVD1DCxedzVVBpaGi8aSmoXFAeKNgtAer8",
                "version": "1",
                "nonce": "32891757",
                "issuedAt": issued_at.isoformat(timespec="milliseconds") + "Z",
                "chainId": "1",
                "resources": [
                    "ipfs://Qme7ss3ARVgxv6rXqVPiikMJ8u2NLgmgszg13pYrDKEoiu",
                    "https://example.com/my-web2-claim.json",
                ]
            }
        )
        eth_private_key = wallet.derive_account("eth", account=0)[0]
        message_to_sign = encode_defunct(text=siwe_message.sign_message(eip55=True))
        signed_message = Account.sign_message(message_to_sign, private_key=eth_private_key)
        siwe_message.signature = "0x" + signed_message.signature.hex()
        cacao_object = Cacao()
        cacao_object.from_siwe_message(siwe_message)
        cacao_object.verify(EIP191Verifier(verifier_type="eip191"))