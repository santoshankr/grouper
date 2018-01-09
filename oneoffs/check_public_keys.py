import logging

import sshpubkeys

from grouper.models.public_key import PublicKey
from grouper.oneoff import BaseOneOff
from grouper.plugin import PluginRejectedPublicKey, get_plugins


class CheckPublicKeys(BaseOneOff):
    def run(self, session, dry_run=True):
        for key in session.query(PublicKey):
            pubkey = sshpubkeys.SSHKey(key.public_key, strict=True)

            logging.info("Processing Key (id={})".format(key.id))

            try:
                pubkey.parse()
            except sshpubkeys.InvalidKeyException as e:
                logging.error("Invalid Key (id={}): {}".format(key.id, e.message))
                continue

            try:
                for plugin in get_plugins():
                    plugin.will_add_public_key(pubkey)
            except PluginRejectedPublicKey as e:
                logging.error("Bad Key (id={}): {}".format(key.id, e.message))
                continue
