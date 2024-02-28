We purchase corpora from external sources and also sell our self-constructed corpora. To ensure a minimum quality of the corpus, we check the following items. All processes are conducted after the refinement (apps/libs/cleaning).

## 1. Quality Check Items

```
Item               | Description
-------------------+--------------------------------------------------------------
dup_xx             | Checks for duplicates within the file.
translated         | Checks if the translation is the same as the original (not translated).
str_xx             | Checks if the string is correct.
no_wrong_char_xx   | Checks for wrong characters (e.g., u'\xa0', matching quotes/brackets, etc.).
no_url             | Checks if URLs are included.
no_email           | Checks if emails are included.
no_html            | Checks if HTML tags are included.
min_length_xx      | Checks if the minimum length is met (word count for languages with spaces, character count for languages without spaces).
no_profanity_xx    | Checks for the presence of profanity or sexual words.
no_similar_xx      | Checks for texts that are not identical but similar. (Sørensen–Dice coefficient: https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient)
```

## 2. Language-specific Profanity Words

Path:
- ~/project/corpus_raw/texts/profanity_words

Sources:
- Russian: https://github.com/rominf/profanity-filter
- Spanish: https://www.freewebheaders.com/full-list-of-bad-words-banned-by-google
- English: https://github.com/rominf/profanity-filter
- Italian: https://www.freewebheaders.com/full-list-of-bad-words-banned-by-google
- Indonesian: https://www.freewebheaders.com/full-list-of-bad-words-banned-by-google
- French: https://www.freewebheaders.com/full-list-of-bad-words-banned-by-google
- Korean: Own internet search
- Others: https://github.com/chucknorris-io/swear-words

## 3. Execution

Options:
```
--add_filter_result : Adds the filtering result to Excel.
--drop_alphabet_in_CJK : Checks as faulty if there are alphabets in Chinese/Japanese/Korean.
--drop_email : Checks as faulty if emails are included.
--drop_url : Checks as faulty if URLs are included.
--max_len_ratio : Checks as faulty if the length ratio between two sentences exceeds a certain value.
--min_chars_count : Checks as faulty if below a minimum number of characters.
--min_words_count : Checks as faulty if below a minimum number of words.
--not_check_in_flitto : Checks as faulty if it's a sentence already owned.
--not_check_one_text : Checks as faulty if there are more than two sentences.
--not_check_profanity : Checks as faulty if there is profanity or sexual words.
--not_check_similarity : Does not check the similarity between sentences.
--not_check_verb : Checks as faulty if there is no verb.
--similarity_col_name : The column name to check for similarity.
--similarity_sid_col_name : The column name used when showing sentences with high similarity. If omitted, row numbers are used.
--max_similarity : Checks as faulty if exceeding a certain similarity.
--mt_sample_ratio : Extracts sentences at a certain ratio to compare with machine translation.
--mt_lang_codes : Source language, target language for machine translation.
```

Single corpus quality check:
```shell
$ cd apps/texts/check_quality
$ ./check_quality.py \
    -p ~/project/corpus_raw/texts/mono \
    --add_sid \
    -i mono_fr_1.xlsx \
    --col_indices 2 3 \
    --col_names fr_id fr \
    --add_filter_result \
    --similarity_col_name fr \
    --not_check_in_flitto \
    --not_check_one_text \
    --not_check_verb
```

Quality check for two language pair corpora:
```shell
$ cd apps/texts/check_quality
$ ./check_quality.py \
    -p ~/project/corpus_raw/texts/2pairs \
    --add_sid \
    -i en_fr_1.xlsx \
    --col_indices 2 3 4 5 \
    --col_names en_id en fr_id fr \
    --add_filter_result \
    --not_check_in_flitto \
    --not_check_one_text \
    --not_check_verb
```

## 4. Example output

Single corpus:
```
sid  | group_id | en_id    | en                                                                                               | en_source         | tag | dup_en | str_en | no_wrong_char_en | min_length_en | no_profanity_en | no_similar_en
-----+----------+----------+--------------------------------------------------------------------------------------------------+-------------------+-----+--------+--------+------------------+---------------+-----------------+--------------
93   | 8921022  | 30124130 | If your intention is to make us clock in and out, then the answer is an emphatic "No thank you'. | 2020_MEGADIC_ENFR | nan | TRUE   | TRUE   | FALSE            | TRUE          | TRUE            | TRUE
3249 | 8917865  | 30116752 | People that don't put a circumflex accent on "râler" piss me off.                                | 2020_MEGADIC_ENFR | nan | TRUE   | TRUE   | TRUE             | TRUE          | FALSE           | TRUE
```
