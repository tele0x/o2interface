# Copyright (C) 2021-2022 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys
from urllib.parse import urlparse

from o2common import config
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


_DEFAULT_DCMANAGER_URL = "http://192.168.204.1:8119/v1.0"
_DEFAULT_STX_URL = "http://192.168.204.1:5000/v3"


def get_config_path():
    path = os.environ.get("O2APP_CONFIG", "/configs/o2app.conf")
    return path


def get_smo_ca_config_path():
    path = os.environ.get("SMO_CA_CONFIG", "/configs/smoca.crt")
    return path


def get_postgres_uri():
    # host = os.environ.get("DB_HOST", "localhost")
    # port = 54321 if host == "localhost" else 5432
    host = "localhost"
    port = 5432
    password = os.environ.get("DB_PASSWORD", "o2ims123")
    user, db_name = "o2ims", "o2ims"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    # host_interal = os.environ.get("API_HOST", "localhost")
    host_interal = "localhost"
    host_external = os.environ.get("API_HOST_EXTERNAL_FLOATING")
    if config.conf.OCLOUD.API_HOST_EXTERNAL_FLOATING is not None and \
            config.conf.OCLOUD.API_HOST_EXTERNAL_FLOATING != '':
        host_external = config.conf.OCLOUD.API_HOST_EXTERNAL_FLOATING
    host = host_interal if host_external is None or host_external == '' \
        else host_external

    port_internal = 5005 if host == "localhost" else 80
    port_external = 30205
    port = port_internal if host_external is None or host_external == '' \
        else port_external
    return f"https://{host}:{port}"


def get_root_api_base():
    return "/"


def get_o2ims_api_base():
    return get_root_api_base() + 'o2ims-infrastructureInventory'


def get_o2ims_monitoring_api_v1():
    return '/v1'


def get_o2ims_inventory_api_v1():
    return '/v1'


def get_o2ims_monitoring_api_base():
    return get_root_api_base() + 'o2ims-infrastructureMonitoring'


def get_o2dms_api_base():
    return get_root_api_base() + "o2dms/v1"


def get_redis_host_and_port():
    # host = os.environ.get("REDIS_HOST", "localhost")
    # port = 63791 if host == "localhost" else 6379
    host = "localhost"
    port = 6379
    return dict(host=host, port=port)


def get_smo_o2endpoint():
    smo_o2endpoint = os.environ.get(
        "SMO_O2_ENDPOINT", "http://localhost/smo_sim")
    return smo_o2endpoint


def get_stx_client_args():
    client_args = dict(
        auth_url=os.environ.get('OS_AUTH_URL', _DEFAULT_STX_URL),
        username=os.environ.get('OS_USERNAME', "admin"),
        api_key=os.environ.get('OS_PASSWORD', "fakepasswd1"),
        project_name=os.environ.get('OS_PROJECT_NAME', "admin"),
    )
    if config.conf.OCLOUD.OS_AUTH_URL is not None and \
            config.conf.OCLOUD.OS_AUTH_URL != '':
        client_args['auth_url'] = config.conf.OCLOUD.OS_AUTH_URL
    if config.conf.OCLOUD.OS_USERNAME is not None and \
            config.conf.OCLOUD.OS_USERNAME != '':
        client_args['username'] = config.conf.OCLOUD.OS_USERNAME
    if config.conf.OCLOUD.OS_PASSWORD is not None and \
            config.conf.OCLOUD.OS_PASSWORD != '':
        client_args['api_key'] = config.conf.OCLOUD.OS_PASSWORD
    if config.conf.OCLOUD.OS_PROJECT_NAME is not None and \
            config.conf.OCLOUD.OS_PROJECT_NAME != '':
        client_args['project_name'] = config.conf.OCLOUD.OS_PROJECT_NAME
    return client_args


def get_stx_access_info(region_name="RegionOne", subcloud_hostname: str = "",
                        sub_is_https: bool = False):
    # authurl = os.environ.get("STX_AUTH_URL", "http://192.168.204.1:5000/v3")
    # username = os.environ.get("STX_USERNAME", "admin")
    # pswd = os.environ.get("STX_PASSWORD", "passwd1")
    # stx_access_info = (authurl, username, pswd)
    try:
        # client_args = dict(
        #     auth_url=os.environ.get('OS_AUTH_URL', _DEFAULT_STX_URL),
        #     username=os.environ.get('OS_USERNAME', "admin"),
        #     api_key=os.environ.get('OS_PASSWORD', "fakepasswd1"),
        #     project_name=os.environ.get('OS_PROJECT_NAME', "admin"),
        # )
        client_args = get_stx_client_args()
    except KeyError:
        logger.error('Please source your RC file before execution, '
                     'e.g.: `source ~/downloads/admin-rc.sh`')
        sys.exit(1)

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_{key}'.format(key=key)] = val
    if "" != subcloud_hostname:
        orig_auth_url = urlparse(_DEFAULT_STX_URL)
        new_auth_url = orig_auth_url._replace(
            netloc=orig_auth_url.netloc.replace(
                orig_auth_url.hostname, subcloud_hostname))
        # new_auth_url = new_auth_url._replace(
        #     netloc=new_auth_url.netloc.replace(str(new_auth_url.port),
        # "18002"))
        if sub_is_https:
            new_auth_url = new_auth_url._replace(
                scheme=new_auth_url.scheme.
                replace(new_auth_url.scheme, 'https'))
            os_client_args['insecure'] = True
        os_client_args['os_auth_url'] = new_auth_url.geturl()
        os_client_args['os_endpoint_type'] = 'public'
    # os_client_args['system_url'] = os_client_args['os_auth_url']
    os_client_args['os_password'] = os_client_args.pop('os_api_key')
    os_client_args['os_region_name'] = region_name
    os_client_args['api_version'] = 1
    # os_client_args['user_domain_name'] = 'Default'
    # os_client_args['project_domain_name'] = 'Default'
    return os_client_args


def get_dc_access_info():
    try:
        # client_args = dict(
        #     auth_url=os.environ.get('OS_AUTH_URL', _DEFAULT_STX_URL),
        #     username=os.environ.get('OS_USERNAME', "admin"),
        #     api_key=os.environ.get('OS_PASSWORD', "fakepasswd1"),
        #     project_name=os.environ.get('OS_PROJECT_NAME', "admin"),
        # )
        client_args = get_stx_client_args()
    except KeyError:
        logger.error('Please source your RC file before execution, '
                     'e.g.: `source ~/downloads/admin-rc.sh`')
        sys.exit(1)

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_{key}'.format(key=key)] = val
    auth_url = urlparse(os_client_args.pop('os_auth_url'))
    dcmanager_url = urlparse(_DEFAULT_DCMANAGER_URL)
    dcmanager_url = dcmanager_url._replace(netloc=dcmanager_url.netloc.replace(
        dcmanager_url.hostname, auth_url.hostname))

    os_client_args['dcmanager_url'] = dcmanager_url.geturl()
    os_client_args['auth_url'] = auth_url.geturl()
    os_client_args['username'] = os_client_args.pop('os_username')
    os_client_args['api_key'] = os_client_args.pop('os_api_key')
    os_client_args['project_name'] = os_client_args.pop('os_project_name')
    os_client_args['user_domain_name'] = 'Default'
    os_client_args['project_domain_name'] = 'Default'

    return os_client_args


def get_fm_access_info(subcloud_hostname: str = "",
                       sub_is_https: bool = False):
    try:
        # client_args = dict(
        #     auth_url=os.environ.get('OS_AUTH_URL', _DEFAULT_STX_URL),
        #     username=os.environ.get('OS_USERNAME', "admin"),
        #     api_key=os.environ.get('OS_PASSWORD', "fakepasswd1"),
        #     project_name=os.environ.get('OS_PROJECT_NAME', "admin"),
        # )
        client_args = get_stx_client_args()
    except KeyError:
        logger.error('Please source your RC file before execution, '
                     'e.g.: `source ~/downloads/admin-rc.sh`')
        sys.exit(1)

    os_client_args = {}
    for key, val in client_args.items():
        os_client_args['os_{key}'.format(key=key)] = val

    auth_url = urlparse(os_client_args.pop('os_auth_url'))
    os_client_args['auth_url'] = auth_url.geturl()

    if "" != subcloud_hostname:
        orig_auth_url = urlparse(_DEFAULT_STX_URL)
        new_auth_url = orig_auth_url._replace(
            netloc=orig_auth_url.netloc.replace(
                orig_auth_url.hostname, subcloud_hostname))
        if sub_is_https:
            new_auth_url = new_auth_url._replace(
                scheme=new_auth_url.scheme.
                replace(new_auth_url.scheme, 'https'))
        os_client_args['auth_url'] = new_auth_url.geturl()
        os_client_args['endpoint_type'] = 'publicURL'

    os_client_args['insecure'] = True

    os_client_args['username'] = os_client_args.pop('os_username')
    os_client_args['password'] = os_client_args.pop('os_api_key')
    os_client_args['project_name'] = os_client_args.pop('os_project_name')
    os_client_args['user_domain_name'] = 'Default'
    os_client_args['project_domain_name'] = 'Default'

    return os_client_args


def get_k8s_api_endpoint():
    K8S_KUBECONFIG = os.environ.get("K8S_KUBECONFIG", None)
    K8S_APISERVER = os.environ.get("K8S_APISERVER", None)
    K8S_TOKEN = os.environ.get("K8S_TOKEN", None)
    return K8S_KUBECONFIG, K8S_APISERVER, K8S_TOKEN


def get_helm_cli():
    return '/usr/local/bin/helm'


def get_containers_shared_folder():
    return '/share'


def get_system_controller_as_respool():
    return True


def gen_k8s_config_dict(cluster_api_endpoint, cluster_ca_cert, admin_user,
                        admin_client_cert, admin_client_key):
    # KUBECONFIG environment variable
    # reference:
    # https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/
    data = {
        'apiVersion': 'v1',
        'clusters': [
            {
                'cluster': {
                    'server':
                    cluster_api_endpoint,
                    'certificate-authority-data':
                    cluster_ca_cert,
                },
                'name': 'inf-cluster'
            }],
        'contexts': [
            {
                'context': {
                    'cluster': 'inf-cluster',
                    'user': 'kubernetes-admin'
                },
                'name': 'kubernetes-admin@inf-cluster'
            }
        ],
        'current-context': 'kubernetes-admin@inf-cluster',
        'kind': 'Config',
        'preferences': {},
        'users': [
            {
                'name': admin_user,
                'user': {
                    'client-certificate-data':
                    admin_client_cert,
                    'client-key-data':
                    admin_client_key,
                }
            }]
    }

    return data


def get_helmcli_access():
    host_external = os.environ.get("API_HOST_EXTERNAL_FLOATING")
    if config.conf.OCLOUD.API_HOST_EXTERNAL_FLOATING is not None and \
            config.conf.OCLOUD.API_HOST_EXTERNAL_FLOATING != '':
        host_external = config.conf.OCLOUD.API_HOST_EXTERNAL_FLOATING
    host = "127.0.0.1" if host_external is None or host_external == '' \
        else host_external
    port = "10022" if host_external is None or host_external == '' \
        else "30022"

    helm_host_with_port = host+':'+port
    helm_user = 'helm'
    helm_pass = os.environ.get("HELM_USER_PASSWD")

    return helm_host_with_port, helm_user, helm_pass


def get_alarm_yaml_filename():
    alarm_yaml_name = os.environ.get("ALARM_YAML")
    if alarm_yaml_name is not None and os.path.isfile(alarm_yaml_name):
        return alarm_yaml_name
    return "/configs/alarm.yaml"


def get_events_yaml_filename():
    events_yaml_name = os.environ.get("EVENTS_YAML")
    if events_yaml_name is not None and os.path.isfile(events_yaml_name):
        return events_yaml_name
    return "/configs/events.yaml"


# get k8s host from env:
def get_k8s_host():
    k8s_host = os.environ.get("KUBERNETES_SERVICE_HOST")
    if k8s_host is None:
        raise Exception('Get k8s host failed.')
    return k8s_host


# get k8s host port from env:
def get_k8s_port():
    k8s_port = os.environ.get("KUBERNETES_SERVICE_PORT_HTTPS", '443')
    return k8s_port


# token review url
def get_review_url():
    try:
        api = '/apis/authentication.k8s.io/v1/tokenreviews'
        return "{0}{1}:{2}{3}".format(
            'https://', get_k8s_host(), get_k8s_port(), api)
    except Exception:
        raise Exception('Get k8s review url failed')


# get reviewer token
def get_reviewer_token():
    # token path default is below.
    token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
    with open(token_path, 'r') as f:
        ctt = f.read()
    return ctt


def get_auth_provider():
    return 'k8s'


def get_dms_support_profiles():
    profiles_list = []
    profiles_str = config.conf.API.DMS_SUPPORT_PROFILES
    if profiles_str:
        profiles_strip = profiles_str.strip(' []')
        profiles_str = profiles_strip.replace("'", "").replace(
            '"', "")
        profiles_list = profiles_str.split(',')
    if 'native_k8sapi' not in profiles_list:
        profiles_list.append('native_k8sapi')
    return profiles_list
