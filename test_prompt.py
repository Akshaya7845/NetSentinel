from src.ai.prompt_builder import PromptBuilder

builder = PromptBuilder()

print("========== EXECUTIVE PROMPT ==========\n")
print(builder.build_executive_prompt())

print("\n\n========== DETAILED PROMPT ==========\n")
print(builder.build_detailed_prompt())