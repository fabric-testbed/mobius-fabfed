from fabfed.util.constants import Constants

SENSE_PROFILE_UID = "service_profile_uuid"
SENSE_ALIAS = "alias"
SENSE_EDIT = "options"
SENSE_URI = 'uri'
# SENSE_ID = 'id'
SENSE_PATH = 'path'
SENSE_VLAN_TAG = 'vlan_tag'

SENSE_DTN = 'With Host'
SENSE_DTN_IP = 'IP Address'

SERVICE_INSTANCE_KEYS = ['intents', 'alias', 'referenceUUID', 'state', 'owner', 'lastState', 'timestamp', 'archived']

SENSE_CUSTOMER_ASN = "customer_asn"
SENSE_AMAZON_ASN = "amazon_asn"
SENSE_CUSTOMER_IP = "customer_ip"
SENSE_AMAZON_IP = "amazon_ip"
SENSE_AUTHKEY = "authkey"
SENSE_TO_HOSTED_CONN = "to_hosted_conn"

SENSE_AWS_PEERING_MAPPING = {
    Constants.RES_LOCAL_ASN: SENSE_CUSTOMER_ASN,
    Constants.RES_LOCAL_ADDRESS: SENSE_CUSTOMER_IP,

    Constants.RES_REMOTE_ASN: SENSE_AMAZON_ASN,
    Constants.RES_REMOTE_ADDRESS: SENSE_AMAZON_IP,

    Constants.RES_SECURITY: SENSE_AUTHKEY,

    Constants.RES_ID: SENSE_TO_HOSTED_CONN,
}

# This is what we get from node_details from manifest for AWS ...
# 'Public IP': '18.215.246.8', 'Node Name': 'VM-1',
# 'Key Pair': 'keypair+kp-sense', 'Image': 'image+ami-052efd3df9dad4825'}

# ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20220609
# ami-052efd3df9dad4825
# ami-052efd3df9dad4825
# Canonical, Ubuntu, 22.04 LTS, amd64 jammy image build on 2022-06-09

SENSE_AWS_KEYPAIR = 'Key Pair'
SENSE_AWS_PUBLIC_IP = 'Public IP'
SENSE_AWS_NODE_NAME = 'Node Name'
SENSE_AWS_IMAGE = 'Image'

SENSE_RETRY = 50
