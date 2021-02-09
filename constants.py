AWS_INSTANCE_TYPES = [
    't3.micro',
    't3.small',
    'c5.large']

# --------------------------------------------------------------------
AZURE_INSTANCE_TYPES = [
    'B1s',
    'B1ms',
    'B2ms',
    'D4s_v3']
# --------------------------------------------------------------------
GCP_INSTANCE_TYPES = [
    'e2-small',
    'e2-medium',
    'e2-standard-2'
]

# --------------------------------------------------------------------
PROVIDERS = [
    'aws',
    'azure',
    'gcp']

# --------------------------------------------------------------------
SLES_VERSIONS = [
    'sles-12-sp1',
    'sles-12-sp2',
    'sles-12-sp3',
    'sles-12-sp4',
    'sles-12-sp5',
    'sles-15',
    'sles-15-sp1',
    'sles-15-sp2'
]

# --------------------------------------------------------------------
SLES_SAP_VERSIONS = [
    'sles-sap-12-sp1',
    'sles-sap-12-sp2',
    'sles-sap-12-sp3',
    'sles-sap-12-sp4',
    'sles-sap-12-sp5',
    'sles-sap-15',
    'sles-sap-15-sp1',
    'sles-sap-15-sp2'
]

# --------------------------------------------------------------------
OS_TYPES = [
    'sles',
    'sles-sap'
]

# --------------------------------------------------------------------
TF_TEMPLATE_LOCATION = "tf_templates"
TF_APPLY_LOCATION = "tf_apply"

# --------------------------------------------------------------------
PRIVATE_VPC_CIDR_1 = "192.168.0.0/16"
PRIVATE_SUBNET_CIDR_1 = "192.168.111.0/24"

# --------------------------------------------------------------------
CACHE_INVALIDATE_DAYS = 7

# --------------------------------------------------------------------
AZURE_AUTH_LOCATION = "/mercury/data/public-cloud/keys/azure/credentials.json"
REGION_CACHE_FILENAME = ".cache/.region-cache-"
ZONE_CACHE_FILENAME = ".cache/.zone-cache-"

# --------------------------------------------------------------------
# Colors
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
