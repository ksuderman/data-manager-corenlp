#!/usr/bin/env python
"""
Data Manager for Stanford CoreNLP Language Models

This script downloads and registers CoreNLP language model JARs for use with Galaxy.
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


# CoreNLP version and model information
CORENLP_VERSION = "4.5.10"

# Common models JAR (contains dcoref dictionaries and common models)
COMMON_MODELS = {
    "name": "Common Models",
    "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models.jar",
    "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models.jar"
}

LANGUAGE_MODELS = {
    "ar": {
        "name": "Arabic",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-arabic.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-arabic.jar"
    },
    "zh": {
        "name": "Chinese",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-chinese.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-chinese.jar"
    },
    "en": {
        "name": "English",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-english.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-english.jar"
    },
    "fr": {
        "name": "French",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-french.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-french.jar"
    },
    "de": {
        "name": "German",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-german.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-german.jar"
    },
    "hu": {
        "name": "Hungarian",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-hungarian.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-hungarian.jar"
    },
    "it": {
        "name": "Italian",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-italian.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-italian.jar"
    },
    "es": {
        "name": "Spanish",
        "jar_name": f"stanford-corenlp-{CORENLP_VERSION}-models-spanish.jar",
        "url": f"https://repo1.maven.org/maven2/edu/stanford/nlp/stanford-corenlp/{CORENLP_VERSION}/stanford-corenlp-{CORENLP_VERSION}-models-spanish.jar"
    }
}


def download_model(url, target_path):
    """
    Download a file from URL to target path with progress reporting.
    """
    print(f"Downloading from {url}")
    print(f"Saving to {target_path}")

    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(100, (downloaded / total_size) * 100) if total_size > 0 else 0
        print(f"\rProgress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end="")

    try:
        urllib.request.urlretrieve(url, target_path, reporthook=report_progress)
        print()  # New line after progress
        print("Download complete!")
        return True
    except Exception as e:
        print(f"\nError downloading file: {e}", file=sys.stderr)
        return False


def load_existing_models(data_table_path):
    """Load existing model entries from the data table to avoid duplicates."""
    existing = set()
    if data_table_path and Path(data_table_path).exists():
        with open(data_table_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if parts:
                        existing.add(parts[0])  # Add the value (first column)
    return existing


def main():
    parser = argparse.ArgumentParser(description="Download and register CoreNLP language models")
    parser.add_argument("--language", action="append", choices=LANGUAGE_MODELS.keys(),
                        help="Language code(s) for the model(s) to download (can be specified multiple times)")
    parser.add_argument("--common-models", action="store_true",
                        help="Download the common models JAR (required for coreference)")
    parser.add_argument("--target-directory", required=True,
                        help="Directory to store the downloaded model JARs")
    parser.add_argument("--output", required=True,
                        help="JSON output file for Galaxy data manager")
    parser.add_argument("--data-table", required=False,
                        help="Path to existing data table file to check for duplicates")

    args = parser.parse_args()

    # Require at least one option
    if not args.language and not args.common_models:
        parser.error("At least one of --language or --common-models must be specified")

    # Load existing models to avoid duplicates
    existing_models = load_existing_models(args.data_table)

    # Create target directory
    target_dir = Path(args.target_directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    # List to collect all data table entries
    data_table_entries = []

    # Process common models if requested
    if args.common_models:
        if "common" in existing_models:
            print(f"\n{'=' * 60}")
            print(f"Skipping {COMMON_MODELS['name']} - already in data table")
            print(f"{'=' * 60}")
        else:
            print(f"\n{'=' * 60}")
            print(f"Processing {COMMON_MODELS['name']}...")
            print(f"{'=' * 60}")

            # Download common models JAR
            jar_path = target_dir / COMMON_MODELS["jar_name"]

            if jar_path.exists():
                print(f"Model already exists at {jar_path}")
            else:
                if not download_model(COMMON_MODELS["url"], str(jar_path)):
                    print(f"WARNING: Failed to download {COMMON_MODELS['name']}", file=sys.stderr)
                else:
                    print(f"Successfully downloaded {COMMON_MODELS['name']}")

            # Prepare data table entry for common models
            data_table_entries.append({
                "value": "common",
                "name": COMMON_MODELS["name"],
                "lang_code": "common",
                "models_path": str(jar_path.absolute())
            })

            print(f"Successfully registered {COMMON_MODELS['name']}")
            print(f"  Value: common")
            print(f"  Language code: common")
            print(f"  Path: {jar_path.absolute()}")

    # Process each language
    if args.language:
        for lang_code in args.language:
            if lang_code in existing_models:
                print(f"\n{'=' * 60}")
                print(f"Skipping {LANGUAGE_MODELS[lang_code]['name']} - already in data table")
                print(f"{'=' * 60}")
            else:
                print(f"\n{'=' * 60}")
                print(f"Processing {LANGUAGE_MODELS[lang_code]['name']} model...")
                print(f"{'=' * 60}")

                model_info = LANGUAGE_MODELS[lang_code]

                # Download model JAR
                jar_path = target_dir / model_info["jar_name"]

                if jar_path.exists():
                    print(f"Model already exists at {jar_path}")
                else:
                    if not download_model(model_info["url"], str(jar_path)):
                        print(f"WARNING: Failed to download {model_info['name']} model", file=sys.stderr)
                        continue  # Skip this model but continue with others

                # Prepare data table entry
                value = lang_code
                name = model_info["name"]
                models_path = str(jar_path.absolute())

                data_table_entries.append({
                    "value": value,
                    "name": name,
                    "lang_code": lang_code,
                    "models_path": models_path
                })

                print(f"Successfully registered {name} model")
                print(f"  Value: {value}")
                print(f"  Language code: {lang_code}")
                print(f"  Path: {models_path}")

    # Create data manager JSON output
    data_manager_output = {
        "data_tables": {
            "corenlp_models": data_table_entries
        }
    }

    # Write output JSON
    with open(args.output, "w") as f:
        json.dump(data_manager_output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Summary: Successfully registered {len(data_table_entries)} model(s)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
