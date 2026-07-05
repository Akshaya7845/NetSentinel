from src.services.k6_service import get_latency_summary

summary = get_latency_summary()

if summary:
    print("Latency Summary")
    print("----------------")
    print(summary)
else:
    print("Report not found!")