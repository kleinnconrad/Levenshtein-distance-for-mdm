# Address Matching & Deduplication Pipeline

## Table of Contents
* [`levenshtein.py` Overview](#-levenshteinpy-overview)
* [Understanding Levenshtein Distance](#-understanding-levenshtein-distance)
  * [How It Works](#how-it-works)
  * [What It Is Good For](#what-it-is-good-for)
* [Databricks Asset Bundles (DABs)](#-databricks-asset-bundles-dabs)
* [CI/CD Pipeline (GitHub Actions)](#%EF%B8%8F-cicd-pipeline-github-actions)

---

## `levenshtein.py` Overview

The core logic of the deduplication process is handled by the `levenshtein.py` script. It operates using the `pandas` and `Levenshtein` libraries through the following sequential steps:

1. **Data Loading:** Ingests the source data containing system IDs, record IDs, company names, street names, and zip codes.
2. **Data Standardization:** Applies regular expressions to clean the text fields. It standardizes the data by converting strings to lowercase, stripping out common legal entity suffixes (e.g., GmbH, KG, AG), removing common street suffixes (e.g., strasse, weg), and eliminating whitespace and special characters. 
3. **Blocking (Self-Join):** Merges the dataset against itself based strictly on the `zip_code`. This "blocking" strategy prevents an expensive computational cross-join (comparing every record to every other record) by only comparing records within the same geographic area. Self-matches are then filtered out.
4. **Similarity Scoring:** Calculates the Levenshtein edit distance for both the cleaned company names and street names, translating the result into a percentage similarity score (0 to 100).
5. **Threshold Filtering:** Filters the paired records, keeping only those where both the company name and street name have a similarity score of 90% or higher.
6. **Output Generation:** Formats the final list of duplicate pairs, returning the original source IDs and their matched counterparts.

---

## Understanding Levenshtein Distance

### How It Works
The **Levenshtein Distance** (or Edit Distance) is a string metric used for measuring the difference between two sequences. Informally, the Levenshtein distance between two words is the minimum number of single-character edits required to change one word into the other. 

The allowable edits are:
* **Insertion** (e.g., `cat` → `cart`)
* **Deletion** (e.g., `cart` → `cat`)
* **Substitution** (e.g., `cat` → `bat`)

The Python script uses `Levenshtein.ratio()`, which normalizes this edit distance into a ratio based on the lengths of the two strings, providing a convenient percentage score where 100% is an exact match.

### What It Is Good For
* **Master Data Management & CRM Deduplication:** Merging fragmented customer records (e.g., matching "TechCorp" with "Tech Corp Inc.").
* **Spell Checking and Autocorrect:** Suggesting the closest valid word in a dictionary when a user makes a typo.
* **Plagiarism Detection:** Finding closely matching sentences or paragraphs in large text corpora.
* **Bioinformatics:** Aligning DNA or protein sequences to find genetic similarities.

---

## Databricks Asset Bundles (DABs)

This project relies on **Databricks Asset Bundles** to manage its infrastructure. DABs represent Databricks' native Infrastructure-as-Code (IaC) solution. 

Instead of manually clicking through the Databricks UI to create jobs, clusters, and tasks, the entire architecture is defined in declarative YAML files (e.g., `databricks.yml` and job-specific configurations). 
* **Reproducibility:** Ensures that the environment and job configurations can be perfectly replicated across development, staging, and production workspaces.
* **Serverless Compute:** Seamlessly integrates with Serverless compute, allowing notebooks or scripts (via the `# Databricks notebook source` magic comment) to run instantly without managing underlying cluster infrastructure.

---

## CI/CD Pipeline (GitHub Actions)

To maintain synchronization between the repository code and the live Databricks workspace, this project utilizes a Continuous Integration/Continuous Deployment (CI/CD) pipeline powered by **GitHub Actions**.

* **Trigger:** The workflow automatically initiates on a push to the `main` branch, but *only* if relevant files are modified (e.g., `src/levenshtein.py`, the `resources/` YAML files, or `databricks.yml`).
* **Validation:** It first runs `databricks bundle validate` to ensure all syntax and configurations are correct before interacting with the live environment.
* **Deployment:** Upon successful validation, it executes `databricks bundle deploy`. This command securely connects to the target workspace (authenticated via a GitHub Secret containing a Databricks Personal Access Token) and updates the Databricks Jobs and underlying source code automatically.