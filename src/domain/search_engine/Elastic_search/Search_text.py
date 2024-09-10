from __future__ import annotations

from domain.search_engine.Elastic_search.elastic_search import es

es.count_documents('od_index')
if es.client:
    search_results = es.search_od(
        index_name='od_index',
        query='clothing',
        min_count=1,
        max_count=10,
        topk=10, )
    for result in search_results:
        print(result)
