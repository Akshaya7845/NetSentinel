from src.ai.report_generator import ReportGenerator

generator = ReportGenerator()

files = generator.generate_reports()

print("Reports Generated Successfully!\n")

print(files["executive_summary"])

print(files["detailed_report"])