from src.ai.llm_service import LLMService

service = LLMService()

print("========== EXECUTIVE SUMMARY ==========\n")
print(service.generate_executive_report())

print("\n\n========== DETAILED TECHNICAL REPORT ==========\n")
print(service.generate_detailed_report())