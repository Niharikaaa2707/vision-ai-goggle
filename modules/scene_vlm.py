# modules/scene_vlm.py
# moondream2 via HuggingFace Transformers — offline, no API key.
# Uses transformers 4.x compatible approach with config patching.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from PIL import Image


class SceneVLM:
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        print("[SceneVLM] Loading moondream2...")
        try:
            from transformers import AutoTokenizer, AutoConfig
            import torch

            model_id = "vikhyatk/moondream2"
            revision = "2024-03-13"

            # Load tokenizer first
            self._tokenizer = AutoTokenizer.from_pretrained(
                model_id, revision=revision
            )

            # Load and patch config BEFORE loading model
            config = AutoConfig.from_pretrained(
                model_id,
                revision=revision,
                trust_remote_code=True
            )

            # Patch missing attributes that newer transformers expects
            if not hasattr(config, 'pad_token_id') or config.pad_token_id is None:
                config.pad_token_id = self._tokenizer.eos_token_id
            if not hasattr(config, 'bos_token_id') or config.bos_token_id is None:
                config.bos_token_id = self._tokenizer.bos_token_id
            if not hasattr(config, 'eos_token_id') or config.eos_token_id is None:
                config.eos_token_id = self._tokenizer.eos_token_id

            # Also patch the text_config if it exists
            if hasattr(config, 'text_config'):
                if not hasattr(config.text_config, 'pad_token_id'):
                    config.text_config.pad_token_id = self._tokenizer.eos_token_id

            from transformers import AutoModelForCausalLM
            self._model = AutoModelForCausalLM.from_pretrained(
                model_id,
                config=config,
                trust_remote_code=True,
                revision=revision,
                torch_dtype=torch.float32
            )
            self._model.eval()
            self._loaded = True
            print("[SceneVLM] moondream2 loaded successfully.")

        except Exception as e:
            print(f"[SceneVLM] Could not load moondream2: {e}")
            import traceback
            traceback.print_exc()
            self._loaded = False

    def _frame_to_pil(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)

    def _ask(self, frame, question):
        if not self._loaded:
            return "Scene model not available right now."
        try:
            pil_image = self._frame_to_pil(frame)
            enc_image = self._model.encode_image(pil_image)
            answer = self._model.answer_question(
                enc_image, question, self._tokenizer
            )
            return answer
        except Exception as e:
            print(f"[SceneVLM] Inference error: {e}")
            import traceback
            traceback.print_exc()
            return "Sorry, I could not process that right now."

    def describe(self, frame):
        print("[SceneVLM] Running scene description...")
        result = self._ask(frame,
            "Describe what you see in this scene in one or two short sentences.")
        print(f"[SceneVLM] Description: {result}")
        return result

    def read_text(self, frame):
        print("[SceneVLM] Running text reading...")
        result = self._ask(frame,
            "What text is visible in this image? If no text, say No text visible.")
        print(f"[SceneVLM] Text: {result}")
        return result

    def answer(self, frame, question):
        result = self._ask(frame, question)
        return result


_vlm = None

def get_vlm():
    global _vlm
    if _vlm is None:
        _vlm = SceneVLM()
    return _vlm


if __name__ == "__main__":
    vlm = SceneVLM()
    cap = cv2.VideoCapture(0)
    print("Press 'd' to describe, 'r' to read text, 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("SceneVLM Test", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('d'):
            print(vlm.describe(frame))
        elif key == ord('r'):
            print(vlm.read_text(frame))
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
