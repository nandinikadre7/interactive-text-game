from typing import TypedDict
from langgraph.graph import StateGraph, END


class GameState(TypedDict):
    theme: str
    message: str
    # state: to store the theme and message


def setup_game(state: GameState) -> dict:
    theme = state["theme"].strip()

    if not theme:
        theme = "mystery world"
    #get the theme from user or mystry wrold and update the game state... with theme and put message ....

    return {
        "theme": theme,
        "message": f"Game started with theme: {theme}"
    }



def build_graph():
    graph = StateGraph(GameState)  # iniitalise graph
    graph.add_node("setup_game", setup_game)  # add node
    graph.set_entry_point("setup_game") # add entry point
    graph.add_edge("setup_game", END) # add edge start-> get user theme -> set-up node[update the theme]-> end
    return graph.compile()
