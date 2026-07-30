# patch_moondream.py - Final comprehensive patch for moondream2 + transformers 5.x

import os
import glob

cache_base = os.path.expanduser(
    r"~/.cache/huggingface/modules/transformers_modules/vikhyatk/moondream2"
)

if not os.path.exists(cache_base):
    print(f"Cache not found at {cache_base}")
    exit(1)

patched_total = 0

# --- Patch modeling_phi.py ---
phi_files = glob.glob(os.path.join(cache_base, "**", "modeling_phi.py"), recursive=True)

for phi_path in phi_files:
    print(f"\nPatching: {phi_path}")
    with open(phi_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Fix 1: pad_token_id assignment
        line = line.replace(
            "self.padding_idx = config.pad_token_id",
            "self.padding_idx = getattr(config, 'pad_token_id', None)"
        )
        # Fix 2: pad_token_id as kwarg
        line = line.replace(
            "padding_idx=config.pad_token_id",
            "padding_idx=getattr(config, 'pad_token_id', None)"
        )
        # Fix 3: rope_scaling type
        line = line.replace(
            'scaling_type = self.config.rope_scaling["type"]',
            'scaling_type = (self.config.rope_scaling or {}).get("type", "linear")'
        )
        line = line.replace(
            'self.config.rope_scaling["type"]',
            '(self.config.rope_scaling or {}).get("type", "linear")'
        )
        # Fix 4: rope_scaling factor
        line = line.replace(
            'self.config.rope_scaling["factor"]',
            '(self.config.rope_scaling or {}).get("factor", 1.0)'
        )
        # Fix 5: Add GenerationMixin to PhiForCausalLM class line
        if "class PhiForCausalLM(PhiPreTrainedModel):" in line:
            line = line.replace(
                "class PhiForCausalLM(PhiPreTrainedModel):",
                "class PhiForCausalLM(PhiPreTrainedModel, GenerationMixin):"
            )
        new_lines.append(line)

    content = "".join(new_lines)

    # Fix 6: Add GenerationMixin import at the very top (after existing imports)
    if "GenerationMixin" in content and "from transformers.generation" not in content and "import GenerationMixin" not in content:
        # Find the first import line and insert before it
        first_import_idx = next(
            (i for i, l in enumerate(new_lines) if l.startswith("import ") or l.startswith("from ")),
            0
        )
        new_lines.insert(first_import_idx, "from transformers.generation.utils import GenerationMixin\n")
        content = "".join(new_lines)

    with open(phi_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Done.")
    patched_total += 1

# --- Patch moondream.py: add all_tied_weights_keys ---
md_files = glob.glob(os.path.join(cache_base, "**", "moondream.py"), recursive=True)

for md_path in md_files:
    print(f"\nPatching: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content

    if "all_tied_weights_keys" not in content:
        # Find class body start and insert property
        target = "class Moondream("
        idx = content.find(target)
        if idx != -1:
            # Find end of class declaration line
            end = content.find("\n", idx) + 1
            prop = (
                "    @property\n"
                "    def all_tied_weights_keys(self):\n"
                "        return {}\n\n"
            )
            content = content[:end] + prop + content[end:]
            print(f"  Added all_tied_weights_keys property.")

    if content != original:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        patched_total += 1

print(f"\nAll done. {patched_total} file(s) patched.")
