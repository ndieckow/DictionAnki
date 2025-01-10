# DictionAnki
A simple and easy-to-use web application built with NiceGUI that looks up a word in an online dictionary (Merriam Webster and dict.cc are supported), lets you select a meaning and translation and adds it to a list. Once you're happy, you can export the list as a set of Anki flashcards. I wrote this mostly for personal use, so the structure of the exported Anki cards is hardcoded, but it is easy to adapt.

## Showcase
![](res/application.png)

## Planned Features
- [ ] layout and design improvements
    - [ ] larger card height
    - [ ] hide all of the `{}` and `[]` stuff, unless mouse is hovering over the entry 
- [ ] option to select different dictionaries
- [x] ability to select several meanings and translations
    - *done: 30.12.24*
- [ ] ability to edit the cards in the list, as well as to rearrange or delete (some of) them
- [ ] implement support for Merriam Webster API
- [ ] different parsing of dict.cc, so that we also get tabs
- [ ] for MerriamWebster: indicate redirections
    - e.g. typing "prospector" actually yields the results for "prospect," but this fact is hidden in DictionAnki
- [ ] mark transitive vs. intransitive verbs