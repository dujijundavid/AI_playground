import os
import openai
import re
import yaml
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define file paths for YAML configurations
CONFIG_FILES = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml'
}

def load_config():
    """Load configurations from YAML files."""
    configs = {}
    for config_type, file_path in CONFIG_FILES.items():
        with open(file_path, 'r', encoding='utf-8') as file:
            configs[config_type] = yaml.safe_load(file)
    return configs

def call_agent(agent_info, user_prompt, max_tokens=3000, model="gpt-4o-mini"):
    """
    Call OpenAI Chat Completion, combining agent_info into system_message and sending user_prompt.
    """
    system_message = f"""You are an AI expert assisting Mercedes-Benz in patent drafting.
Your role: {agent_info['role']}
Your goal: {agent_info['goal']}
Your background: {agent_info['backstory']}

Please adhere to the following requirements:
1. Mathematical formulas must be in a format directly usable in Word (avoid LaTeX).
2. Use standard mathematical symbols like: ∑, xᵢ, yⱼ, ∫, ⊕, ⊗, matrix representations, etc.
3. Formulas should be directly copyable into Word without conversion.

Please comply with the above instructions.
"""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return ""

def build_prompt_for_step(step_name, tasks, results):
    """
    Construct the prompt for the current step, incorporating outputs from previous steps if necessary.
    """
    base_prompt = tasks[step_name][0]

    if step_name == "initial_idea":
        return base_prompt

    previous_outputs = "\n\n".join([f"【{step} Output】\n{results.get(step, '')}" for step in tasks.keys() if step != step_name])
    return f"{base_prompt}\n\n---\n\nPlease consider the following previous outputs:\n\n{previous_outputs}"

def estimate_cost(usage_metrics):
    """
    Estimate the cost based on token usage.
    """
    costs = 0.150 * (usage_metrics['prompt_tokens'] + usage_metrics['completion_tokens']) / 1_000_000
    print(f"Total costs: ${costs:.4f}")

def main():
    # Load configurations
    configs = load_config()
    agents_config = configs['agents']
    tasks_config = configs['tasks']

    # Read initial idea from file
    initial_idea_file = "initial_idea.txt"
    with open(initial_idea_file, "r", encoding="utf-8") as f:
        initial_idea_input = f.read().strip()

    # Generate output folder name based on initial idea
    folder_name = "patent_" + "_".join(re.findall(r"\w+", initial_idea_input)[:5])
    output_dir = os.path.join("patent_outputs", folder_name)
    os.makedirs(output_dir, exist_ok=True)

    # Initialize results dictionary
    results = {}

    # Execute each step
    for task_name in ["initial_idea", "innovation", "qa", "customization", "deep_improvement"]:
        agent_key = f"{task_name}_agent"
        agent_info = agents_config.get(agent_key, {})
        token_limit = tasks_config.get(task_name, [None, 3000])[1]
        user_prompt = build_prompt_for_step(task_name, tasks_config, results)

        # Determine model to use
        model_to_use = "gpt-4o" if task_name in ["deep_improvement", "innovation"] else "gpt-4o-mini"

        # Call the agent
        result = call_agent(agent_info, user_prompt, max_tokens=token_limit, model=model_to_use)

        if result:
            results[task_name] = result
            output_file = os.path.join(output_dir, f"{task_name}_output.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"=== {task_name.replace('_', ' ').title()} ===")
            print(result)
            print(f"Output saved to {output_file}\n")
        else:
            print(f"=== {task_name.replace('_', ' ').title()} ===")
            print("No valid output received. Please check API calls or prompt content.\n")

    # Estimate and display costs
    # Assuming 'usage_metrics' is a dictionary containing 'prompt_tokens' and 'completion_tokens'
    usage_metrics = {'prompt_tokens': 1000, 'completion_tokens': 2000}  # Example values
    estimate_cost(usage_metrics)

if __name__ == "__main__":
    main()
