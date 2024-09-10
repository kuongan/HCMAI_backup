from __future__ import annotations

from domain.search_engine.Elastic_search.elastic_search import es

if es.client:
    es.indexer('od_index')
    es.add_object(r'E:\OD', 'od_index')
    es.indexer('asr_index')
    es.add_asr(r'E:\test\asr', 'asr_index')
    es.indexer('ocr_index')
    es.add_ocr(r'E:\real_OCR', 'ocr_index')
    es.indexer('color_index')
    es.add_color(r'E:\Color', 'color_index')
