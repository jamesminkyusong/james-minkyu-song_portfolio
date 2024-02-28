# Natex README

## Disclaimer
This project was carried out as a part of my experience as an Undergraduate Research Assistant at Emory University's NLP Research Lab. 
I was closely working on this project with James D. Finch, who won the 2021 Amazon Alexa Prize Award with the Emora chatbot which utilized the Natex based State Transition Dialogue Manager, [`emora_stdm`](https://github.com/emora-chat/emora_stdm).

The challenge was that since this was a package developed solely for competition purposes, it was overfit into the competition's dataset. This made it difficult to generalize the package for other purposes and Dr. Jinho Choi gave me the chance to work on this project to make it more generalizable so that it can be used to for his course CS329 Computational Linguistics at Emory University.

While I was able to make some progress, I was not able to complete the project due to personal issues and other responsibilities. Furthermore, I began this project right as GPT-3 and other NLP models were becoming extremely popular and disrupting the NLP field. The field of Core-NLP (basic NLP tasks such as Tokenization, Part of Speech Tagging, Named Entity Recognition, etc) was becoming less popular and outperformed easily by LLM-models. 
Thus, it was getting extremely difficult to find motivation to continue while balancing my personal issues at the time on top of rigorous academic courses. 

This is a project that makes me feel bittersweet. Although we were all left unsure whether this package could have even been developed into a bug-free fully functioning package in the first place (as it only uses regular expression and no ML models), I was sure that it could have helped students understand the basics of NLP in Dr. Choi's course, regardless of the breakthroughs in LLM-models.
While I am not most proud of the lack of completion, I am still proud of the knowledge and wisdom I gained from various struggles associated with this project.

The key contributions I made are as follows:

- Refactoring the Abstract Syntax Tree Parsing Grammar (modifying the AST structure itself) so that it is more generalizable to the natural language, not the competition dataset.
- Creating vast more test cases to ensure that the refactored AST structure is working as expected.
- Reducing dependencies and extracting Natex from the emora_stdm package.
- Refactoring the code to so that it follows the standard development practice.

The original `natex_nlu.py` file was added as `natex_nlu_before_contribution.py` to the repository so that the reader can see the improvements I made to the package. 

## Overview

Natex NLU (Natural Language Understanding) is a Python library designed for advanced natural language pattern matching. It leverages a unique syntax that allows developers to define complex patterns that can match various linguistic constructs within text inputs. This flexibility makes it ideal for applications in natural language processing (NLP) tasks such as intent recognition, entity extraction, and more.

## Features

- **Flexible Pattern Matching**: Define patterns that can match exact phrases, optional elements, sequences, and alternatives.
- **Negation and Kleene Star**: Use negation to exclude specific terms and Kleene star for matching zero or more occurrences of a pattern.
- **Regular Expressions Support**: Incorporate regular expressions within your patterns for more granular control.
- **Macro Definitions**: Create reusable pattern components called macros, which can be parameterized for dynamic pattern generation.
- **Debugging Support**: Enable debugging options to visualize how patterns are matched against input text, aiding in pattern refinement.

## Syntax Highlights

- **Flexible Sequence**: `["term1", "term2"]` matches any sequence including "term1" and "term2".
- **Conjunction**: `"<term1, term2>"` requires both "term1" and "term2" to appear in any order.
- **Disjunction**: `"{term1, term2}"` matches either "term1" or "term2".
- **Negation**: `"~term"` excludes matches containing "term".
- **Kleene Star**: `"term*"` matches zero or more occurrences of "term".
- **Regular Expression**: `"/regex/"` matches based on the specified regular expression.
- **Macro**: `"@macroName(args)"` invokes a macro with the given arguments.

## Usage Example

The first example demonstrates a basic usage where the pattern seeks either a greeting followed by either "world" or "universe". 

The flexibility and power of Natex lie in its ability to define, nest and match such complex patterns with ease, making it a valuable tool for developers working on NLP tasks.

```python
from natex_nlu import Natex

pattern_1 = "[{greet, hello}, {world, universe}]"
natex = Natex(pattern_1)

# Check if the pattern matches the input text
if natex.match("hello universe"):
    print("Match found!")
else:
    print("No match.")
# Output: Match found!

if natex.match("greet world"):
    print("Match found!")
else:
    print("No match.")
# Output: Match found!

pattern_2 = "[{greet, hello}, ~world]"
natex = Natex(pattern_2)
if natex.match("hello universe"):
    print("Match found!")
else:
    print("No match.")
# Output: Match found!  

if natex.match("hello world"):
    print("Match found!")
else:
    print("No match.")
# Output: No match.
```
