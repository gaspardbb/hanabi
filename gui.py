import tkinter as tk
from functools import partial
from tkinter.ttk import *
from typing import List, Callable

from game import Information
from one_player_perspective import OnePlayer
from utils import pretty_probability

COLORS = ["Blue", "White", "Red", "Yellow", "Green"]
VALUES = [1, 2, 3, 4, 5]
COLORS_ID = {c: int(i) for i, c in enumerate(COLORS)}
VALUES_ID = {str(v): int(v-1) for v in VALUES}

window = tk.Tk()
window.title("Hanabi")


def get_color_combobox(row, column):
    new_combobox = Combobox(window)
    new_combobox['values'] = COLORS
    new_combobox.current(0)
    new_combobox.grid(column=column, row=row)
    return new_combobox


def get_value_combobox(row, column):
    new_combobox = Combobox(window)
    new_combobox["values"] = VALUES
    new_combobox.current(0)
    new_combobox.grid(column=column, row=row)
    return new_combobox


def get_label_and_combo(label: str, rows: List[int], columns: List[int], color_and_value=(True, True)):
    assert len(rows) == len(columns)
    show_color, show_value = color_and_value

    lab_obj = tk.Label(window, text=label)
    lab_obj.grid(column=columns[0], row=rows[0])

    if show_color and show_value:
        col = get_color_combobox(rows[1], columns[1])
        val = get_value_combobox(rows[2], columns[2])
        return lab_obj, col, val
    else:
        if show_color:
            col = get_color_combobox(rows[1], columns[1])
            return lab_obj, col
        else:  # show_value
            val = get_value_combobox(rows[1], columns[1])
            return lab_obj, val


def display_probabilities():
    """Display probabilities text zones."""
    probability_labels = []
    for i in range(op.hand.n_cards):
        lab_card_i = tk.Label(window, text=f"Card {i+1}", font=("Arial Bold", 30))
        lab_card_i.grid(column=i, row=4)

        proba_i, denominator_i = op.card_probability(i)
        lab_proba_i = tk.Label(window, text=pretty_probability(proba_i), font=("Arial", 10))
        lab_proba_i.grid(column=i, row=5)

        lab_denominator_i = tk.Label(window, text="/" + str(denominator_i), font=("Arial Bold", 10))
        lab_denominator_i.grid(column=i, row=6)

        probability_labels.append((lab_card_i, lab_proba_i, lab_denominator_i))
    return probability_labels


def color_to_id(c):
    return COLORS_ID[c]


def values_to_id(v):
    return VALUES_ID[v]


def get_radio_list(rows, columns):
    assert len(rows) == len(columns) == 5

    bool_buttons = []
    for i in range(5):
        bool_var = tk.BooleanVar()
        check_button = tk.Checkbutton(window, text=i+1, var=bool_var)
        check_button.grid(row=rows[i], column=columns[i])
        bool_buttons.append((check_button, bool_var))
    return bool_buttons


def box_action(func: Callable, params, preprocessing, add_card=False, display=True):
    """
    Function which returns a callable, taking as input a list of tkinter widgets implementing the get() method and
    regular parameters.

    Given:
        params = [p_1, ..., p_n]
        preprocessing = [f_1, ..., f_n]
    Computes the following list of parameters:
        x = p_i            if f_i is None
            f_i(p_i.get()) otherwise
                                for i in 1, ..., n.
    and returns a callable:
        func(x)

    Args:
        func:
            The function to execute.
        params:
            A list of tkinter widgets, implementing the .get() method, or regular parameters.
        preprocessing:
            A list of function f: x -> f(x), which will receive as input the boxes.
        add_card:
            Whether to add a card after being called.
        display:
            Whether to call display_probabilities after being called.
    Returns:
        A callable.
    """
    assert len(params) == len(preprocessing)

    def wrap():
        list_of_params = []
        for param, f in zip(params, preprocessing):
            if f is None:
                list_of_params.append(param)
            else:
                list_of_params.append(f(param.get()))

        func(*list_of_params)
        if add_card:
            op.add_card()
        if display:
            display_probabilities()
    return wrap



# Init player
op = OnePlayer()
display_probabilities()

# See card
see_label, see_color, see_values = get_label_and_combo("See", [0]*3, [0, 1, 2])
see_button = tk.Button(window, text="Seen!",
                       command=box_action(op.see_card, [see_color, see_values],
                                          [color_to_id, values_to_id], add_card=True))
see_button.grid(row=0, column=3)

##### COLOR INFO #####
color_info_label, color_info_value = get_label_and_combo("Color information", [1]*2, [0, 1],
                                                            color_and_value=(True, False))
radio_color = get_radio_list([1]*5, list(range(2, 7)))

def get_color_info():
    cards = []
    for i in range(5):
        if radio_color[i][1].get():
            cards.append(i)
    op.add_information(cards, Information("color", color_to_id(color_info_value.get()), False))
    display_probabilities()

color_info_button = tk.Button(window, text="Get info!", command=get_color_info)
color_info_button.grid(row=1, column=8)

##### VALUE INFO #####
value_info_label, value_info_value = get_label_and_combo("Value information", [2]*2, [0, 1],
                                                            color_and_value=(False, True))
radio_value = get_radio_list([2]*5, list(range(2, 7)))

def get_value_info():
    cards = []
    for i in range(5):
        if radio_value[i][1].get():
            cards.append(i)
    print(cards)
    op.add_information(cards, Information("value", values_to_id(value_info_value.get()), False))
    display_probabilities()

value_info_button = tk.Button(window, text="Get info!", command=get_value_info)
value_info_button.grid(row=2, column=8)

##### PLAY #####
play_objects = []
play_buttons = []
for i in range(5):
    play_label, play_color, play_value = get_label_and_combo("Play:", [7, 8, 9], [i]*3)
    play_button = tk.Button(window, text="Played!",
                                  command=box_action(op.play_card, [i, play_color, play_value],
                                                      [None, color_to_id, values_to_id], add_card=True))
    play_button.grid(row=10, column=i)

##### Reorder #####
card_index_label, card_index_value = get_label_and_combo("Card index", [11]*2, [0, 1],
                                                            color_and_value=(False, True))
card_newindex_label, card_newindex_value = get_label_and_combo("New index", [11]*2, [2, 3],
                                                            color_and_value=(False, True))

def change_position():
    card_idx = VALUES_ID[card_index_value.get()]
    new_idx = VALUES_ID[card_newindex_value.get()]
    op.hand.reorder(card_idx, new_idx)
    display_probabilities()


reorder_button = tk.Button(window, text="Change!", command=change_position)
reorder_button.grid(row=11, column=4)

window.mainloop()