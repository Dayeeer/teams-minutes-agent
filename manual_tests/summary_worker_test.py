from app.workers.summary_worker import process_summaries


result = process_summaries(limit=10)

print("\nSUMMARY WORKER RESULT:")
print(result)

