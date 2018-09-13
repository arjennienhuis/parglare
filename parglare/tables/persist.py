import json
from collections import OrderedDict
from parglare.tables import LRState, LRTable, Action


def save_table(file_name, table):

    # states
    states = []
    for state in table.states:
        states.append(_dump_state(state))

    with open(file_name, 'w') as f:
        json.dump(states, f)


def load_table(file_name, grammar):

    with open(file_name) as f:
        json_states = json.load(f)

    states = {}
    for json_state in json_states:
        state = LRState(grammar, json_state['state_id'],
                        grammar.get_symbol(json_state['symbol']))
        states[state.state_id] = state
        state.finish_flags = json_state['finish_flags']
        state.actions = json_state['actions']
        state.gotos = json_state['gotos']

    # Unpack actions and gotos
    for state in states.values():

        actions = OrderedDict()
        for json_action_fqn in state.actions:
            terminal_fqn, json_actions = json_action_fqn
            term_acts = []
            for json_action in json_actions:
                term_acts.append(
                    Action(json_action['action'],
                           states[json_action['state_id']],
                           grammar.productions[json_action['prod_id']]))
            actions[grammar.get_terminal(terminal_fqn)] = term_acts
        state.actions = actions

        gotos = OrderedDict()
        for json_goto_fqn in state.gotos:
            nonterm_fqn, goto_state = json_goto_fqn
            gotos[grammar.get_nonterminal(nonterm_fqn)] = states[goto_state]
        state.gotos = gotos

    table = LRTable(states, calc_finish_flags=False)

    return table


def _dump_state(state):
    s = {}
    s['state_id'] = state.state_id
    s['symbol'] = state.symbol.fqn
    s['actions'] = [[terminal.fqn, _dump_actions(action)]
                    for terminal, action in state.actions.items()]
    s['gotos'] = [[nonterminal.fqn, state.state_id]
                  for nonterminal, state in state.gotos.items()]
    s['finish_flags'] = state.finish_flags

    return s


def _dump_actions(actions):
    actions = []
    for action in actions:
        a = {}
        a['action'] = action.action
        a['state_id'] = action.state.state_id
        a['prod_id'] = action.prod.prod_id

    return actions