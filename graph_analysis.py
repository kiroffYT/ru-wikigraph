import networkx as nx
import json
import os

def analyze_and_sort(links_graph, output_dir, date_str):
    G = nx.DiGraph(links_graph)
    
    # Считаем входящие ссылки (In-degree)
    in_degrees = dict(G.in_degree())
    sorted_by_inbound = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
    
    # Считаем PageRank (осторожно: требует много RAM на 2 млн узлов)
    # Используем меньший параметр tol для ускорения, если падаем по тайм-ауту
    pagerank = nx.pagerank(G, alpha=0.85, tol=1e-4)
    sorted_by_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    
    # Сохраняем результаты сортировки
    sort_dir = os.path.join(output_dir, date_str, "sorting")
    os.makedirs(sort_dir, exist_ok=True)
    
    with open(os.path.join(sort_dir, "inbound_links.json"), 'w', encoding='utf-8') as f:
        json.dump({"sorting_type": "inbound", "results": sorted_by_inbound[:10000]}, f, ensure_ascii=False)
        
    with open(os.path.join(sort_dir, "pagerank.json"), 'w', encoding='utf-8') as f:
        json.dump({"sorting_type": "pagerank", "results": sorted_by_pr[:10000]}, f, ensure_ascii=False)
