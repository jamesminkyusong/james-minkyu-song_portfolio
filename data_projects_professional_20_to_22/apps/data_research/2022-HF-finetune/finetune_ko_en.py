from configparser import ConfigParser
from multiprocessing.sharedctypes import Value
import os
import pandas as pd

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)
from datasets import load_dataset, load_metric
import numpy as np


def parsers():
    c_parser = ConfigParser()
    c_parser.read("train_MarianMT.ini")
    return c_parser


def preprocess_function(examples):
    prefix = ""
    max_input_length = 128
    max_target_length = 128
    source_lang = "ko"
    target_lang = "en"
    inputs = [prefix + ex[source_lang] for ex in examples["translation"]]
    targets = [ex[target_lang] for ex in examples["translation"]]
    model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)
    # Setup the tokenizer for targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=max_target_length, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]
    return preds, labels


def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    # Some simple post-processing
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)
    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    result = {"bleu": result["score"]}
    prediction_lens = [
        np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds
    ]
    result["gen_len"] = np.mean(prediction_lens)
    result = {k: round(v, 4) for k, v in result.items()}
    return result


if __name__ == "__main__":
    configs = parsers()
    model_dir = configs.get("PATHS", "model_dir")
    train_dir = configs.get("PATHS", "train_dir")
    valid_dir = configs.get("PATHS", "valid_dir")
    test_dir = configs.get("PATHS", "test_dir")
    model_outdir = configs.get("PATHS", "out_dir")
    source_lang = "ko"
    target_lang = "en"

    if torch.cuda.is_available():
        device = torch.device("cuda")  # 확실히 GPU 로 학습 진행 시키기
        os.environ["WANDB_DISABLED"] = "true"
        model_checkpoint = model_dir

        raw_datasets = load_dataset(
            "json",
            data_files={
                "train": train_dir,
                "validation": valid_dir,
                "test": test_dir,
            },
        )
        metric = load_metric("sacrebleu")
        tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        tokenized_datasets = raw_datasets.map(preprocess_function, batched=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)

        batch_size = 16
        model_name = model_checkpoint.split("/")[-1]
        args = Seq2SeqTrainingArguments(
            os.path.join(
                model_outdir, f"{model_name}-finetuned-{source_lang}-to-{target_lang}"
            ),
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            weight_decay=0.01,
            save_total_limit=2,
            num_train_epochs=3,
            predict_with_generate=True,
        )
        data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

        trainer = Seq2SeqTrainer(
            model,
            args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"],
            data_collator=data_collator,
            tokenizer=tokenizer,
            compute_metrics=compute_metrics,
        )

        transformers.logging.set_verbosity_info()
        trainer.train()
    else:
        raise ValueError("GPU NOT FOUND")
