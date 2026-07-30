# fix_phi.py - Rewrites prepare_inputs_for_generation to be compatible with transformers 5.x

import os
import re

paths = [
    r"C:\Users\smart\.cache\huggingface\modules\transformers_modules\vikhyatk\moondream2\2b705eea63f9bff6dae9b52c2daeb26bc10e4aeb\modeling_phi.py",
    r"C:\Users\smart\.cache\huggingface\modules\transformers_modules\vikhyatk\moondream2\79671eae7b5340017e91065d09c1ce1a352c0e8d\modeling_phi.py",
]

# Modern replacement for prepare_inputs_for_generation
NEW_PREPARE_INPUTS = '''    def prepare_inputs_for_generation(
        self,
        input_ids,
        past_key_values=None,
        attention_mask=None,
        inputs_embeds=None,
        **kwargs,
    ):
        if past_key_values is not None:
            # Get past length - compatible with both old and new transformers
            if hasattr(past_key_values, "get_seq_length"):
                past_length = past_key_values.get_seq_length()
            elif hasattr(past_key_values, "seen_tokens"):
                past_length = past_key_values.seen_tokens
            else:
                past_length = past_key_values[0][0].shape[2]

            # Get max cache length
            if hasattr(past_key_values, "get_max_cache_shape"):
                max_cache_length = past_key_values.get_max_cache_shape()
            elif hasattr(past_key_values, "get_max_length"):
                max_cache_length = past_key_values.get_max_length()
            else:
                max_cache_length = None

            # Trim input_ids
            if max_cache_length is not None:
                input_ids = input_ids[:, -min(1, input_ids.shape[1] - past_length):]
            else:
                input_ids = input_ids[:, past_length:]

        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update({
            "past_key_values": past_key_values,
            "use_cache": kwargs.get("use_cache"),
            "attention_mask": attention_mask,
        })
        return model_inputs
'''

for path in paths:
    if not os.path.exists(path):
        print(f"Not found: {path}")
        continue

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and replace the entire prepare_inputs_for_generation method
    pattern = r'    def prepare_inputs_for_generation\(.*?(?=\n    def |\nclass |\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        content = content[:match.start()] + NEW_PREPARE_INPUTS + content[match.end():]
        print(f"Replaced prepare_inputs_for_generation in: {path}")
    else:
        print(f"Function not found in: {path}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Done.")

print("Finished.")
