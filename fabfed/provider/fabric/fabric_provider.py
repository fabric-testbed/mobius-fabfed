import logging

from fabfed.provider.api.provider import Provider
from ...util.constants import Constants
from .fabric_constants import *


class FabricProvider(Provider):
    def __init__(self, *, type, label, name, logger: logging.Logger, config: dict):
        super().__init__(type=type, label=label, name=name, logger=logger, config=config)
        self.slice = None

    def setup_environment(self):
        config = self.config
        credential_file = config.get(Constants.CREDENTIAL_FILE, None)

        if credential_file:
            from fabfed.util import utils

            profile = config.get(Constants.PROFILE)
            config = utils.load_yaml_from_file(credential_file)
            self.config = config = config[profile]

        import os

        os.environ['FABRIC_CREDMGR_HOST'] = config.get(FABRIC_CM_HOST, DEFAULT_CM_HOST)
        os.environ['FABRIC_ORCHESTRATOR_HOST'] = config.get(FABRIC_OC_HOST, DEFAULT_OC_HOST)
        os.environ['FABRIC_TOKEN_LOCATION'] = config.get(FABRIC_TOKEN_LOCATION)
        os.environ['FABRIC_PROJECT_ID'] = config.get(FABRIC_PROJECT_ID)

        os.environ['FABRIC_BASTION_HOST'] = config.get(FABRIC_BASTION_HOST, DEFAULT_BASTION_HOST)
        os.environ['FABRIC_BASTION_USERNAME'] = config.get(FABRIC_BASTION_USER_NAME)
        os.environ['FABRIC_BASTION_KEY_LOCATION'] = config.get(FABRIC_BASTION_KEY_LOCATION)

        os.environ['FABRIC_SLICE_PRIVATE_KEY_FILE'] = config.get(FABRIC_SLICE_PRIVATE_KEY_LOCATION)
        os.environ['FABRIC_SLICE_PUBLIC_KEY_FILE'] = config.get(FABRIC_SLICE_PUBLIC_KEY_LOCATION)

    def _init_slice(self):
        if not self.slice:
            self.logger.info(f"Initializing  slice {self.name}")

            from fabfed.provider.fabric.fabric_slice import FabricSlice

            temp = FabricSlice(provider=self, logger=self.logger)
            temp.init()
            self.slice = temp

    def do_add_resource(self, *, resource: dict):
        self._init_slice()
        self.slice.add_resource(resource=resource)

    def do_create_resource(self, *, resource: dict):
        self._init_slice()
        self.slice.create_resource(resource=resource)

    def do_delete_resource(self, *, resource: dict):
        self._init_slice()
        self.slice.delete_resource(resource=resource)