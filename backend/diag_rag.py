import sys
from app.db.session import SessionLocal
from app.services.search_service import search_documents
from app.services.query_rewriter import rewrite_query
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT id FROM users LIMIT 1")).fetchone()
if not result:
    print("NO USERS FOUND")
    sys.exit(1)

user_id = result[0]
print("user_id:", user_id)

q_orig = "Bi\u1ebFn ng\u1eabu nhi\u00ean trong x\u00e1c su\u1ea5t th\u1ed1ng k\u00ea l\u00e0 g\u00ec"
q_rewr = rewrite_query(q_orig)
print("Original:", repr(q_orig))
print("Rewritten:", repr(q_rewr))

total = db.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
with_sv = db.execute(text("SELECT COUNT(*) FROM document_chunks WHERE search_vector IS NOT NULL")).scalar()
print("Total chunks:", total, " With search_vector:", with_sv)

results = search_documents(db=db, user_id=user_id, query=q_rewr, limit=10)
print("Results (rewritten):", len(results))
for i, r in enumerate(results):
    print("---", i+1, "---")
    print("  doc_id:", r.document_id)
    print("  name:", r.document_name)
    print("  url:", r.source_url)
    print("  page:", r.page_number, " heading:", r.heading)
    print("  score:", r.relevance_score)
    print("  len:", len(r.content))
    print("  text:", repr(r.content[:300]))

if not results:
    results2 = search_documents(db=db, user_id=user_id, query=q_orig, limit=10)
    print("Results (original):", len(results2))
    for i, r in enumerate(results2):
        print("---", i+1, "---")
        print("  doc_id:", r.document_id)
        print("  name:", r.document_name)
        print("  score:", r.relevance_score)
        print("  len:", len(r.content))
        print("  text:", repr(r.content[:300]))

db.close()