from time import time
from typing import Tuple, List
from collections import namedtuple

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

from scrape import scrape_merriam_webster, scrape_dict_cc

# ===== Custom Types =====
AnkiCard = namedtuple('AnkiCard', 'word definition german')
# ========================


# ===== Config =====
SEARCH_WAIT = 2
# ==================


# ===== Global State Variables =====
input_string: str = ''
search_string: str = ''
search_time: int = 0

selected_meaning = None  # Item of selected meaning
selected_translation = None

anki_cards: List[AnkiCard] = []  # List of Anki cards to be exported
# ==================================

def export_cards(cards):
    lines = []
    lines.append('#separator:tab')
    lines.append('#html:true')
    lines.append('#tags column:4')
    for card in cards:
        lines.append('\t'.join(card))
    ui.download('\n'.join(lines).encode('utf-8'), 'anki_cards.txt')

# ==================================

def add_anki_card(event):
    meaning_str: str = selected_meaning.default_slot.children[0].text
    german_str: str = selected_translation.default_slot.children[0].text.split(':::')[1]
    new_card = AnkiCard(word=search_string, definition=meaning_str, german=german_str)
    anki_cards.append(new_card)

    card_table.add_row(new_card._asdict())
    card_table.update()

def update_input_string(event):
    global input_string
    input_string = event.value

def select_meaning(event):
    global selected_meaning
    if selected_meaning is not None:
        selected_meaning.default_slot.children[0].style('background-color: white')
    if selected_meaning == event.sender:
        selected_meaning = None
        add_card_btn.disable()
        return
    selected_meaning = event.sender
    selected_meaning.default_slot.children[0].style('background-color: #ffdddd')
    if selected_translation is not None:
        add_card_btn.enable()

def select_translation(event):
    global selected_translation
    if selected_translation:
        selected_translation.default_slot.children[0].style('background-color: white')
    if selected_translation == event.sender:
        selected_translation = None
        add_card_btn.disable()
        return
    selected_translation = event.sender
    selected_translation.default_slot.children[0].style('background-color: #ffdddd')
    if selected_meaning is not None:
        add_card_btn.enable()

bababa = None
def search(event):
    global search_time, search_string

    if not input_string:
        ui.notify("Please enter a word.")
        return

    new_time = time()
    if new_time - search_time < SEARCH_WAIT:
        ui.notify(f"Wait {SEARCH_WAIT} seconds before searching again")
        return
    search_time = new_time
    search_string = input_string
    
    ui.notify(f"Searching for {search_string}...")
    
    merriam_webster_results = scrape_merriam_webster(search_string)
    dict_cc_results = scrape_dict_cc(search_string)

    result_row.clear()

    tabbies = []
    with result_row:
        with ui.column().classes('flex-grow'):
            with ui.tabs() as tabs:
                for pos,_ in merriam_webster_results:
                    tabbies.append(ui.tab(pos))
            with ui.tab_panels(tabs, value=tabbies[0]) as tab_panels:
                for res,tab in zip(merriam_webster_results, tabbies):
                    with ui.tab_panel(tab):
                        with ui.list().props('dense separator'):
                            for meaning in res[1]:
                                ui.item(f'{meaning}', on_click=select_meaning)
        
        with ui.scroll_area().classes('flex-grow'):
            """
            columns = [
                {'name':'word','label':'Word','field':'word','align':'left','style':'text-wrap: wrap'},
                {'name':'german','label':'German','field':'german','align':'left','style':'text-wrap: wrap'}
            ]
            rows = []
            for eng,ger in dict_cc_results:
                rows.append({'word': eng, 'german': ger})
            ui.table(columns=columns, rows=rows)
            """
            with ui.list().props('dense separator'):
                for eng,ger in dict_cc_results:
                    ui.item(f'{eng} ::: {ger}', on_click=select_translation)

with ui.row():
    ui.input('Word', on_change=update_input_string)
    ui.button('Search', on_click=search)

result_row = ui.grid(columns=2).classes('w-full')

add_card_btn = ui.button('Add card', on_click=add_anki_card)
add_card_btn.disable()

card_table = ui.table(columns=[
    {'name': 'word', 'label': 'Word', 'field': 'word', 'align': 'left'},
    {'name': 'definition', 'label': 'Definition', 'field': 'definition', 'align': 'left'},
    {'name': 'german', 'label': 'German', 'field': 'german', 'align': 'left'}
], rows=[])

export_btn = ui.button('Export to Anki', on_click=lambda: export_cards(anki_cards))
export_btn.bind_enabled_from(card_table, 'rows', lambda x: x != [])

ui.run(dark=False)