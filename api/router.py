from __future__ import unicode_literals, absolute_import

from collections import OrderedDict

from django.urls import NoReverseMatch
from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter


class APIRootView(views.APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True
    api_root_dict = None
    additional_urls = None

    def get(self, request, *args, **kwargs):
        # Return a plain {"name": "hyperlink"} response.
        viewsets = OrderedDict()
        namespace = request.resolver_match.namespace
        for key, url_name in self.api_root_dict.items():
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                viewsets[key] = reverse(
                    url_name,
                    args=args,
                    kwargs=kwargs,
                    request=request,
                    format=kwargs.get('format', None)
                )
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue
        views = OrderedDict()
        for item in self.additional_urls:
            try:
                url_name = item.name
                if namespace:
                    url_name = namespace + ':' + url_name
                url = reverse(
                    url_name,
                    request=request,
                    format=kwargs.get('format', None),
                )
                viewsets[item.name] = url
            except NoReverseMatch:
                url = unicode(item._regex)
                url = request.build_absolute_uri() + url.strip('^$')
                views[item.name] = url
        return Response({
            'viewsets': viewsets,
            'views': views,
        })


class ApiRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super(ApiRouter, self).__init__(*args, **kwargs)
        self.additional_urls = []

    def get_urls(self):
        return super(ApiRouter, self).get_urls() + self.additional_urls

    def register(self, prefix, viewset, base_name=None):
        super(ApiRouter, self).register(prefix, viewset, base_name)

    def get_api_root_view(self, api_urls=None):
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        return APIRootView.as_view(api_root_dict=api_root_dict, additional_urls=self.additional_urls)


