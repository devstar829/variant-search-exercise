from typing import TYPE_CHECKING

from variant_search.models import Variant, AuditLog
from rest_framework import pagination, viewsets, filters
from variant_search.serializers import GeneSerializer, VariantSerializer

if TYPE_CHECKING:
    from django.db.models import QuerySet


class VariantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows queries to fetch Variant data.
    """
    # The variable must be named queryset
    # Filter out rows with a blank gene
    # Apply and then filter by the gene param if set
    queryset = Variant.objects.exclude(gene='')
    serializer_class = VariantSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('gene', )
    def perform_update(self, seralizer):
        instance = self.get_object()
        old_data = VariantSerializer(instance).data
        variant = seralizer.save()
        AuditLog.objects.create(
            variant=variant,
            action="updated",
            old_version=old_data,
            new_value=serializer.data
        )


class GeneViewSetPagination(pagination.PageNumberPagination):
    # Return a lot more gene values, since they are small
    page_size = 100


class GeneViewSet(viewsets.ModelViewSet):
    """
    API endpoint for the gene autosuggest feature
    """
    # The variable must be named queryset
    # Filter out rows with a blank gene
    # Apply and then filter by the gene param if set
    queryset = Variant.objects.exclude(gene='').values('gene').distinct()
    serializer_class = GeneSerializer
    # Return a lot more gene values, since they are small
    pagination_class = GeneViewSetPagination

    def get_queryset(self) -> "QuerySet":
        """
        Filter by the gene param if set
        """
        gene_suggest = self.request.query_params.get('geneSuggest', '').strip()
        return self.queryset.filter(gene__contains=gene_suggest.upper()) if gene_suggest else self.queryset
