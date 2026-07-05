from src.services.postman_service import get_postman_summary

summary = get_postman_summary()

if summary:
    print("Postman Summary")
    print("----------------")
    print(summary)
else:
    print("Postman report not found!")