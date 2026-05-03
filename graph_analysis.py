import networkx as nx
import json
import os

def analyze_and_sort(links_graph, output_dir, date_str):
    G = nx.DiGraph(links_graph)
    
    # Метрики
    in_degrees = dict(G.in_degree())
    # PageRank с расслабленными допусками для скорости
    pagerank = nx.pagerank(G, alpha=0.85, tol=1e-3) 
    
    sort_dir = os.path.join(output_dir, date_str, "sorting")
    os.makedirs(sort_dir, exist_ok=True)
    
    # Сохраняем ТОП-5000 для экономии места
    results = {
        "inbound": sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5000],
        "pagerank": sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5000]
    }
    
    for key, data in results.items():
        with open(os.path.join(sort_dir, f"{key}.json"), 'w', encoding='utf-8') as f:
            json.dump({"sorting_type": key, "results": data}, f, ensure_ascii=False)
