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

selected_meanings = []  # Item of selected meaning
selected_translations = None

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

def listify(strings: List[str]):
    assert len(strings) != 0
    return '<ol><li>' + '</li><li>'.join(strings) + '</li></ol>' if len(strings) > 1 else strings[0]

def add_anki_card(event):
    meanings = [y['meaning'] for x in selected_meanings for y in x]
    germans = [x['german'] for x in selected_translations]
    meaning_str: str = listify(meanings)
    german_str: str = listify(germans)

    new_card = AnkiCard(word=search_string, definition=meaning_str, german=german_str)
    anki_cards.append(new_card)

    #card_table.add_row(new_card._asdict())
    card_table.add_row({
        'word': search_string,
        'definition': ';\n '.join(meanings),
        'german': ';\n '.join(germans)
    })
    card_table.update()

def update_input_string(event):
    global input_string
    input_string = event.value

def select_meaning(event):
    table = event.sender
    row: dict = event.args[1]

    if row in table.selected:
        table.selected.remove(row)
    else:
        table.selected.append(row)
    table.update()

    if all([ls == [] for ls in selected_meanings]):
        add_card_btn.disable()
    elif selected_translations != []:
        add_card_btn.enable()

def select_translation(event):
    table = event.sender
    row: dict = event.args[1]

    if row in table.selected:
        table.selected.remove(row)
    else:
        table.selected.append(row)
    table.update()

    if table.selected == []:
        add_card_btn.disable()
    elif any([ls != [] for ls in selected_meanings]):
        add_card_btn.enable()

bababa = None
async def search(event):
    global search_time, search_string, selected_translations, selected_meanings

    if not input_string.strip():
        ui.notify("Please enter a word.")
        return

    new_time = time()
    if new_time - search_time < SEARCH_WAIT:
        ui.notify(f"Wait {SEARCH_WAIT} seconds before searching again")
        return
    search_time = new_time
    search_string = input_string.strip()

    with result_row:
        ui.skeleton(height='20em')
        ui.skeleton(height='20em')
    
    merriam_webster_results = await scrape_merriam_webster(search_string)
    dict_cc_results = await scrape_dict_cc(search_string)

    # reset
    result_row.clear()
    selected_meanings = []

    tabbies = []
    with result_row:
        with ui.card():
            with ui.column().classes('flex-grow'):
                ui.markdown("### Definition")
                with ui.tabs() as tabs:
                    for pos,_ in merriam_webster_results:
                        tabbies.append(ui.tab(pos))
                with ui.tab_panels(tabs, value=tabbies[0]):
                    for res,tab in zip(merriam_webster_results, tabbies):
                        with ui.tab_panel(tab):
                            rows = []
                            for i,meaning in enumerate(res[1]):
                                #ui.item(f'{meaning}', on_click=select_meaning)
                                rows.append({'meaning': meaning, 'id': i})
                            table = ui.table(columns=[{'name':'meaning','field':'meaning','align':'left','style':'text-wrap: wrap'}], rows=rows).classes('no-shadow').props('dense table-header-class=hidden')
                            table.on('rowClick', select_meaning)
                            selected_meanings.append(table.selected)
        
        with ui.card():
            ui.markdown("### Translation")
            with ui.scroll_area().classes('flex-grow'):
                columns = [
                    {'name':'word','label':'Word','field':'word','align':'left','style':'text-wrap: wrap'},
                    {'name':'german','label':'German','field':'german','align':'left','style':'text-wrap: wrap'}
                ]
                rows = []
                for i,(eng,ger) in enumerate(dict_cc_results):
                    rows.append({'word': eng, 'german': ger, 'id': i})
                translation_table = ui.table(columns=columns, rows=rows).classes('no-shadow').props('dense table-header-class=hidden')
                translation_table.on('rowClick', select_translation)
                selected_translations = translation_table.selected

# =========================================

ui.page_title('DictionAnki')
with ui.header():
    ui.html('<strong>DictionAnki</strong>')

ui.add_head_html("""
<style>
    body {
        background-color: #ccddee;
    }
    .q-page-container {
        margin-left: 15%;
        margin-right: 15%;
        min-width: 600px;
        background-color: white;
    }
    .q-table tr.selected {
        background-color: #ffdddd
    }
</style>
""")

with ui.row().classes('w-full justify-center'):
    ui.input('Word', on_change=update_input_string).props('autofocus outlined rounded item-aligned input-class="ml-3"') \
    .classes('w-5/6 self-center transition-all') \
    .style('font-size: 1.25em;')
    ui.button('', icon='search', on_click=search).classes('self-center').props('round')

result_row = ui.grid(columns=2).classes('w-full')

add_card_btn = ui.button('Add card', icon='playlist_add', on_click=add_anki_card)
add_card_btn.disable()

ui.separator()

ui.markdown("### Vocabulary List")

card_table = ui.table(columns=[
    {'name': 'word', 'label': 'Word', 'field': 'word', 'align': 'left','style':'text-wrap: wrap'},
    {'name': 'definition', 'label': 'Definition', 'field': 'definition', 'align': 'left','style':'text-wrap: wrap'},
    {'name': 'german', 'label': 'German', 'field': 'german', 'align': 'left','style':'text-wrap: wrap'}
], rows=[]).classes('w-full')
card_table.add_slot('body-cell', r'''
    <td :props="props" :style="{'white-space':'pre-line'}">{{ props.value }}</td>
''')

export_btn = ui.button('Export to Anki', icon='file_download', on_click=lambda: export_cards(anki_cards))
export_btn.bind_enabled_from(card_table, 'rows', lambda x: x != [])

ui.run(dark=False)