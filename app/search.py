from flask import current_app



def add_index(index,model):
    if not current_app.elasticsearch:
        return
    payload = {}
    
    for field in model.__searchable__:
        payload[field] = getattr(model,field)
    current_app.elasticsearch.index(index=index,id=model.id,document=payload)


def remove_index(index,model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index,id=model.id)



def query_index(index,query,page,per_page):
    if not current_app.elasticsearch:
        return [],0
    body = {
    "query": {
        "multi_match": {
            "query": query,
            "fields": ["*"],
            "type": "best_fields"
        }
    },
    "from": (page-1)*per_page,
    "size": per_page
    }

    search = current_app.elasticsearch.search(index=index,body= body)
    print(search)
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids , search['hits']['total']['value']