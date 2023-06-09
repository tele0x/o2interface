# Copyright (C) 2021 Wind River Systems, Inc.
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

from flask import request
from flask_restx import Resource, reqparse

from o2common.service.messagebus import MessageBus
from o2common.views.pagination_route import link_header, PAGE_PARAM
from o2common.views.route_exception import NotFoundException, \
    BadRequestException
from o2ims.domain import ocloud
from o2ims.views import ocloud_view
from o2ims.views.api_ns import api_ims_inventory as api_ims_inventory_v1
from o2ims.views.ocloud_dto import OcloudDTO, ResourceTypeDTO,\
    ResourcePoolDTO, ResourceDTO, DeploymentManagerDTO, SubscriptionDTO, \
    InventoryApiV1DTO

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def configure_api_route():
    # Set global bus for resource
    global bus
    bus = MessageBus.get_instance()


# ----------  API versions ---------- #
@api_ims_inventory_v1.route("/v1/api_versions")
class VersionRouter(Resource):
    model = InventoryApiV1DTO.api_version_info_get

    @api_ims_inventory_v1.doc('Get Inventory API version')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self):
        return {
            'uriPrefix': request.base_url.rsplit('/', 1)[0],
            'apiVersions': [{
                'version': '1.0.0',
                # 'isDeprecated': 'False',
                # 'retirementDate': ''
            }]
        }


# ----------  OClouds ---------- #
@api_ims_inventory_v1.route(*["/v1", "/v1/"])
@api_ims_inventory_v1.response(404, 'oCloud not found')
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class OcloudsListRouter(Resource):
    """Ocloud get endpoint
    O2 interface ocloud endpoint
    """

    ocloud_get = OcloudDTO.ocloud

    @api_ims_inventory_v1.doc('Get Ocloud Information')
    @api_ims_inventory_v1.marshal_with(ocloud_get)
    def get(self):
        res = ocloud_view.oclouds(bus.uow)
        if len(res) > 0:
            return res[0]
        raise NotFoundException("oCloud doesn't exist")


# ----------  ResourceTypes ---------- #
@api_ims_inventory_v1.route("/v1/resourceTypes")
@api_ims_inventory_v1.param(PAGE_PARAM,
                            'Page number of the results to fetch.' +
                            ' Default: 1',
                            _in='query', default=1)
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
@api_ims_inventory_v1.param(
    'filter',
    'Filter of the query.',
    _in='query')
class ResourceTypesListRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api_ims_inventory_v1.doc('Get Resource Type List')
    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = ocloud_view.resource_types(bus.uow, **kwargs)
        return link_header(request.full_path, ret)


@api_ims_inventory_v1.route("/v1/resourceTypes/<resourceTypeID>")
@api_ims_inventory_v1.param('resourceTypeID', 'ID of the resource type')
@api_ims_inventory_v1.response(404, 'Resource type not found')
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class ResourceTypeGetRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api_ims_inventory_v1.doc('Get Resource Type Information')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, resourceTypeID):
        result = ocloud_view.resource_type_one(resourceTypeID, bus.uow)
        if not result:
            raise NotFoundException("Resource type {} doesn't exist".format(
                resourceTypeID))
        return result


# ----------  ResourcePools ---------- #
@api_ims_inventory_v1.route("/v1/resourcePools")
@api_ims_inventory_v1.param(PAGE_PARAM,
                            'Page number of the results to fetch.' +
                            ' Default: 1',
                            _in='query', default=1)
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
@api_ims_inventory_v1.param(
    'filter',
    'Filter of the query.',
    _in='query')
class ResourcePoolsListRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api_ims_inventory_v1.doc('Get Resource Pool List')
    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = ocloud_view.resource_pools(bus.uow, **kwargs)
        return link_header(request.full_path, ret)


@api_ims_inventory_v1.route("/v1/resourcePools/<resourcePoolID>")
@api_ims_inventory_v1.param('resourcePoolID', 'ID of the resource pool')
@api_ims_inventory_v1.response(404, 'Resource pool not found')
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class ResourcePoolGetRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api_ims_inventory_v1.doc('Get Resource Pool Information')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, resourcePoolID):
        result = ocloud_view.resource_pool_one(resourcePoolID, bus.uow)
        if result is not None:
            return result
        raise NotFoundException("Resource pool {} doesn't exist".format(
            resourcePoolID))


# ----------  Resources ---------- #
@api_ims_inventory_v1.route("/v1/resourcePools/<resourcePoolID>/resources")
@api_ims_inventory_v1.param('resourcePoolID', 'ID of the resource pool')
@api_ims_inventory_v1.response(404, 'Resource pool not found')
# @api_ims_inventory_v1.param('sort', 'sort by column name',
#                             _in='query')
# @api_ims_inventory_v1.param('per_page', 'The number of results per page ' +
#                             '(max 100). Default: 30',
#                             _in='query', default=30)
@api_ims_inventory_v1.param(PAGE_PARAM,
                            'Page number of the results to fetch.' +
                            ' Default: 1',
                            _in='query', default=1)
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
@api_ims_inventory_v1.param(
    'filter',
    'Filter of the query.',
    _in='query')
class ResourcesListRouter(Resource):

    model = ResourceDTO.resource_list

    @api_ims_inventory_v1.doc('Get Resource List')
    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self, resourcePoolID):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        # if args.per_page is not None:
        #     kwargs['per_page'] = args.per_page
        #     base_url = base_url + 'per_page=' + args.per_page + '&'
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''
        ret = ocloud_view.resources(resourcePoolID, bus.uow, **kwargs)
        if ret is None:
            raise NotFoundException("Resources under {} doesn't exist".format(
                resourcePoolID))
        return link_header(request.full_path, ret)


@api_ims_inventory_v1.route(
    "/v1/resourcePools/<resourcePoolID>/resources/<resourceID>")
@api_ims_inventory_v1.param('resourcePoolID', 'ID of the resource pool')
@api_ims_inventory_v1.param('resourceID', 'ID of the resource')
@api_ims_inventory_v1.response(404, 'Resource not found')
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class ResourceGetRouter(Resource):

    # dto = ResourceDTO()
    # model = dto.get_resource_get()
    model = ResourceDTO.recursive_resource_mapping()

    @api_ims_inventory_v1.doc('Get Resource Information')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, resourcePoolID, resourceID):
        result = ocloud_view.resource_one(resourceID, bus.uow, resourcePoolID)
        if result is None:
            raise NotFoundException("Resource {} doesn't exist".format(
                resourceID))
        return result


# ----------  DeploymentManagers ---------- #
@api_ims_inventory_v1.route("/v1/deploymentManagers")
@api_ims_inventory_v1.param(PAGE_PARAM,
                            'Page number of the results to fetch.' +
                            ' Default: 1',
                            _in='query', default=1)
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
@api_ims_inventory_v1.param(
    'filter',
    'Filter of the query.',
    _in='query')
class DeploymentManagersListRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_list

    @api_ims_inventory_v1.doc('Get Deployment Manager List')
    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = ocloud_view.deployment_managers(bus.uow, **kwargs)
        return link_header(request.full_path, ret)


@api_ims_inventory_v1.route("/v1/deploymentManagers/<deploymentManagerID>")
@api_ims_inventory_v1.param('deploymentManagerID',
                            'ID of the deployment manager')
@api_ims_inventory_v1.param(
    'profile', 'DMS profile: value supports "native_k8sapi"',
    _in='query')
@api_ims_inventory_v1.response(404, 'Deployment manager not found')
@api_ims_inventory_v1.param(
    'all_fields',
    'Set any value for show all fields. This value will cover "fields" ' +
    'and "all_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'fields',
    'Set fields to show, split by comma, "/" for parent and children.' +
    ' Like "name,parent/children". This value will cover "exculde_fields".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_fields',
    'Set fields to exclude showing, split by comma, "/" for parent and ' +
    'children. Like "name,parent/children". This value will cover ' +
    '"exclude_default".',
    _in='query')
@api_ims_inventory_v1.param(
    'exclude_default',
    'Exclude showing all default fields, Set "true" to enable.',
    _in='query')
class DeploymentManagerGetRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api_ims_inventory_v1.doc('Get Deployment Manager Information')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, deploymentManagerID):
        parser = reqparse.RequestParser()
        parser.add_argument('profile', location='args')
        args = parser.parse_args()
        profile = (
            args.profile if args.profile is not None and args.profile != ''
            else ocloud.DeploymentManagerProfileDefault)
        result = ocloud_view.deployment_manager_one(
            deploymentManagerID, bus.uow, profile)
        if result is not None and result != "":
            return result
        elif result == "":
            raise NotFoundException(
                "Profile {} doesn't support".format(
                    args.profile))

        raise NotFoundException("Deployment manager {} doesn't exist".format(
            deploymentManagerID))


# ----------  Subscriptions ---------- #
@api_ims_inventory_v1.route("/v1/subscriptions")
class SubscriptionsListRouter(Resource):

    model = SubscriptionDTO.subscription_get
    expect = SubscriptionDTO.subscription_create

    @api_ims_inventory_v1.doc('Get Subscription List')
    @api_ims_inventory_v1.marshal_list_with(model)
    @api_ims_inventory_v1.param(
        PAGE_PARAM,
        'Page number of the results to fetch. Default: 1',
        _in='query', default=1)
    @api_ims_inventory_v1.param(
        'all_fields',
        'Set any value for show all fields. This value will cover "fields" ' +
        'and "all_fields".',
        _in='query')
    @api_ims_inventory_v1.param(
        'fields',
        'Set fields to show, split by comma, "/" for parent and children.' +
        ' Like "name,parent/children". This value will cover' +
        ' "exculde_fields".',
        _in='query')
    @api_ims_inventory_v1.param(
        'exclude_fields',
        'Set fields to exclude showing, split by comma, "/" for parent and ' +
        'children. Like "name,parent/children". This value will cover ' +
        '"exclude_default".',
        _in='query')
    @api_ims_inventory_v1.param(
        'exclude_default',
        'Exclude showing all default fields, Set "true" to enable.',
        _in='query')
    @api_ims_inventory_v1.param(
        'filter',
        'Filter of the query.',
        _in='query')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(PAGE_PARAM, location='args')
        parser.add_argument('filter', location='args')
        args = parser.parse_args()
        kwargs = {}
        if args.nextpage_opaque_marker is not None:
            kwargs['page'] = args.nextpage_opaque_marker
        kwargs['filter'] = args.filter if args.filter is not None else ''

        ret = ocloud_view.subscriptions(bus.uow, **kwargs)
        return link_header(request.full_path, ret)

    @api_ims_inventory_v1.doc('Create a Subscription')
    @api_ims_inventory_v1.expect(expect)
    @api_ims_inventory_v1.marshal_with(
        model, code=201,
        mask='{subscriptionId,callback,consumerSubscriptionId,filter}')
    def post(self):
        data = api_ims_inventory_v1.payload
        callback = data.get('callback', None)
        if not callback:
            raise BadRequestException('The callback parameter is required')

        result = ocloud_view.subscription_create(data, bus.uow)
        return result, 201


@api_ims_inventory_v1.route("/v1/subscriptions/<subscriptionID>")
@api_ims_inventory_v1.param('subscriptionID', 'ID of the subscription')
@api_ims_inventory_v1.response(404, 'Subscription not found')
class SubscriptionGetDelRouter(Resource):

    model = SubscriptionDTO.subscription_get

    @api_ims_inventory_v1.doc('Get Subscription Information')
    @api_ims_inventory_v1.marshal_with(model)
    @api_ims_inventory_v1.param(
        'all_fields',
        'Set any value for show all fields. This value will cover "fields" ' +
        'and "all_fields".',
        _in='query')
    @api_ims_inventory_v1.param(
        'fields',
        'Set fields to show, split by comma, "/" for parent and children.' +
        ' Like "name,parent/children". This value will cover' +
        ' "exculde_fields".',
        _in='query')
    @api_ims_inventory_v1.param(
        'exclude_fields',
        'Set fields to exclude showing, split by comma, "/" for parent and ' +
        'children. Like "name,parent/children". This value will cover ' +
        '"exclude_default".',
        _in='query')
    @api_ims_inventory_v1.param(
        'exclude_default',
        'Exclude showing all default fields, Set "true" to enable.',
        _in='query')
    def get(self, subscriptionID):
        result = ocloud_view.subscription_one(
            subscriptionID, bus.uow)
        if result is not None:
            return result
        raise NotFoundException("Subscription {} doesn't exist".format(
            subscriptionID))

    @api_ims_inventory_v1.doc('Delete a Subscription')
    @api_ims_inventory_v1.response(200, 'Subscription deleted')
    def delete(self, subscriptionID):
        result = ocloud_view.subscription_delete(subscriptionID, bus.uow)
        return result, 200
