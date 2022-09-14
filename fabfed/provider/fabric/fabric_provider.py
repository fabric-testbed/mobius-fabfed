#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 RENCI NRIG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author Komal Thareja (kthare10@renci.org)
import logging

from fabfed.provider.api.api_client import Provider
from fabfed.util.config import Config


class FabricProvider(Provider):
    def __init__(self, *, type, name, logger: logging.Logger, config: dict):
        super().__init__(type=type, name=name, logger=logger, config=config)

    def setup_environment(self):
        import os

        os.environ['FABRIC_CREDMGR_HOST'] = self.config.get(Config.FABRIC_CM_HOST)
        os.environ['FABRIC_ORCHESTRATOR_HOST'] = self.config.get(Config.FABRIC_OC_HOST)
        os.environ['FABRIC_TOKEN_LOCATION'] = self.config.get(Config.FABRIC_TOKEN_LOCATION)
        os.environ['FABRIC_PROJECT_ID'] = self.config.get(Config.FABRIC_PROJECT_ID)

        os.environ['FABRIC_BASTION_HOST'] = self.config.get(Config.FABRIC_BASTION_HOST)
        os.environ['FABRIC_BASTION_USERNAME'] = self.config.get(Config.FABRIC_BASTION_USER_NAME)
        os.environ['FABRIC_BASTION_KEY_LOCATION'] = self.config.get(Config.FABRIC_BASTION_KEY_LOCATION)

        os.environ['FABRIC_SLICE_PRIVATE_KEY_FILE'] = self.config.get(Config.RUNTIME_SLICE_PRIVATE_KEY_LOCATION)
        os.environ['FABRIC_SLICE_PUBLIC_KEY_FILE'] = self.config.get(Config.RUNTIME_SLICE_PUBLIC_KEY_LOCATION)

    def init_slice(self, *, slice_config: dict, slice_name: str):
        self.logger.debug(f"initializing  slice {slice_name}: slice_attributes={slice_config}")

        if slice_name in self.slices:
            raise Exception("provider cannot have more than one slice with same name")

        from fabfed.provider.fabric.fabric_slice import FabricSlice

        label = slice_config.get(Config.LABEL)
        fabric_slice = FabricSlice(label=label, name=slice_name, logger=self.logger)
        self.slices[slice_name] = fabric_slice
        fabric_slice.set_resource_listener(self)

    def add_resource(self, *, resource: dict, slice_name: str):
        self.logger.info(f"Adding {resource['name_prefix']} to {slice_name}")
        self.logger.debug(f"Adding {resource} to {slice_name}")

        if resource.get(Config.RES_COUNT, 1) < 1:
            self.logger.debug(f"will not add {resource['name_prefix']} to {slice_name}: Count is zero")
            return

        fabric_slice = self.slices[slice_name]
        fabric_slice.add_resource(resource=resource)
