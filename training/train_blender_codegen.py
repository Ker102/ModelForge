"""
Blender Code Generation Fine-Tuning Script — QLoRA on Azure A100
================================================================

Usage on Azure ML:
  pip install -r requirements_training.txt
  python train_blender_codegen.py --data training_data.jsonl --epochs 3

This script fine-tunes Qwen3-8B (or 14B) using QLoRA (4-bit NF4)
for Blender Python code generation.

Requirements (requirements_training.txt):
  torch>=2.1.0
  transformers>=4.40.0
  peft>=0.10.0
  bitsandbytes>=0.43.0
  datasets>=2.18.0
  trl>=0.8.0
  accelerate>=0.28.0
  wandb
"""

import argparse
import json
import os

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer


# ─── Config ─────────────────────────────────────────────
DEFAULT_MODEL = "Qwen/Qwen3-8B"
LORA_R = 64
LORA_ALPHA = 128
LORA_DROPOUT = 0.05
MAX_SEQ_LEN = 2048

SYSTEM_PROMPT = (
    "You are a Blender Python code generator. "
    "Given a natural language instruction, write correct, production-ready "
    "Blender Python code using the bpy API (Blender 4.0+/5.0). "
    "Follow PBR material conventions, use correct socket names, "
    "and apply the factory pattern for materials and objects."
)


def load_training_data(path: str) -> Dataset:
    """Load JSONL training data into HuggingFace Dataset."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            records.append(record)

    print(f"Loaded {len(records)} training pairs")
    return Dataset.from_list(records)


def format_chat(example: dict, tokenizer) -> dict:
    """Format training pair into chat template."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["output"]},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False
    )
    return {"text": text}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to training_data.jsonl")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Base model name")
    parser.add_argument("--output", default="./output/blender-codegen-qlora")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--grad_accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--warmup", type=float, default=0.05)
    parser.add_argument("--no_wandb", action="store_true")
    args = parser.parse_args()

    # ─── Quantization config (4-bit NF4) ────────────────
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # ─── Load model + tokenizer ─────────────────────────
    print(f"Loading model: {args.model}")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model, trust_remote_code=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    model = prepare_model_for_kbit_training(model)

    # ─── LoRA config ────────────────────────────────────
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ─── Dataset ────────────────────────────────────────
    dataset = load_training_data(args.data)
    dataset = dataset.map(
        lambda ex: format_chat(ex, tokenizer),
        remove_columns=dataset.column_names,
    )

    # Split: 90% train, 10% eval
    split = dataset.train_test_split(test_size=0.1, seed=42)
    train_ds = split["train"]
    eval_ds = split["test"]
    print(f"Train: {len(train_ds)}, Eval: {len(eval_ds)}")

    # ─── Training args ──────────────────────────────────
    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        warmup_ratio=args.warmup,
        lr_scheduler_type="cosine",
        bf16=True,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        report_to="wandb" if not args.no_wandb else "none",
        run_name="blender-codegen-qlora",
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        max_grad_norm=0.3,
        group_by_length=True,
    )

    # ─── Trainer ────────────────────────────────────────
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        tokenizer=tokenizer,
        args=training_args,
        max_seq_length=MAX_SEQ_LEN,
    )

    print("Starting training...")
    trainer.train()

    # ─── Save ───────────────────────────────────────────
    final_path = os.path.join(args.output, "final")
    trainer.save_model(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"Model saved to {final_path}")

    # Merge LoRA weights for deployment
    merged_path = os.path.join(args.output, "merged")
    merged_model = model.merge_and_unload()
    merged_model.save_pretrained(merged_path)
    tokenizer.save_pretrained(merged_path)
    print(f"Merged model saved to {merged_path}")


if __name__ == "__main__":
    main()
