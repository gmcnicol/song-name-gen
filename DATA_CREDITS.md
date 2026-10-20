# Vocabulary source and attribution

The noun, base-form verb, and adjective pools were extracted from `textblob/en/en-lexicon.txt`, the English part-of-speech lexicon distributed with TextBlob. We selected lexical entries tagged `NN` or `NNS` (nouns), `VB` (verbs), and `JJ`, `JJR`, or `JJS` (adjectives), kept alphabetic words (including apostrophes and hyphens), converted to lowercase, and removed duplicates. The transformation is solely syntactic; it does not match or curate meanings.

The original lexicon identifies two sources:

- Eric Brill (1992), *A simple rule-based part of speech tagger*, Proceedings of the Workshop on Speech and Natural Language, Association for Computational Linguistics. The Brill tagger lexicon identifies MIT and the University of Pennsylvania, copyright 1993, under an MIT licence.
- Additional words from Carnegie Mellon University's Twitter Part-of-Speech Annotated Data: Kevin Gimpel, Nathan Schneider, Brendan O'Connor, et al. (2011), *Part-of-Speech Tagging for Twitter: Annotation, Features, and Experiments*, ACL, Portland, OR. These data are attributed by the source as CC BY 3.0; see https://creativecommons.org/licenses/by/3.0/ and https://www.ark.cs.cmu.edu/TweetNLP/.

The generated wordlists and the self-contained HTML contain vocabulary derived from these sources. This credits upstream data rather than asserting that the wordlists are original authorship. The generator code is separately authored for this project.
