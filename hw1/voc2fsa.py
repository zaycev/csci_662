#!/usr/bin/env python
# coding: utf-8
# Author: Vladimir M. Zaytsev <zaytsev@usc.edu>

# Incremental Minimal FSA algorithm:
#   [1] http://aclweb.org/anthology-new/J/J00/J00-1002.pdf
#   [2] http://habrahabr.ru/post/190694/


import sys
import itertools
import collections


class State(object):
    
    def __init__(self, key):
        self.key = key
        self.final = False
        self.inputs = collections.OrderedDict()
        self.outputs = collections.OrderedDict()
    
    def make_final(self):
        self.final = True
        
    def __eq__(self, other):
        if self.final != other.final:
            return False
        if len(self.outputs) == 0 and len(other.outputs) == 0:
            if self.final and other.final:
                return True
            else:
                sys.stderr("ERROR")
                return False
        else:
            if len(self.outputs) != len(other.outputs):
                return False
            else:
                outputs_pairs = itertools.izip(self.outputs.iteritems(), other.outputs.iteritems())
                for (trans_1, state_1), (trans_2, state_2) in outputs_pairs:
                    if trans_1 != trans_2:
                        return False
                    if state_1 != state_2:
                        return False
                return True
    
    def __ne__(self, other):
        return not self.__eq__(other)


class MinimalIncrFSA(object):

    def __init__(self):
        self.__state_counter = 1
        self.START = State("0")
        self.reg = collections.OrderedDict({self.START.key: self.START})
        self.FINISH = None
        
    def new_state(self, key=None):
        if key is None:
            key = str(self.__state_counter)
            self.__state_counter += 1
        new_state = State(key)
        return new_state
            
    def prefix(self, word):
        state_list = [self.START]
        current_state = state_list[-1] 
        for symbol in word:
            next_state = self.get_state(current_state, symbol)
            if next_state is None:
                return state_list
            state_list.append(next_state)
            current_state = next_state
        return state_list
        
    def add_suffix(self, word, state_list):
        current_state = state_list[-1]
        for i in xrange(len(state_list) - 1, len(word)):
            new_state = self.new_state()
            symbol = word[i]
            self.add_trans(current_state, new_state, symbol)
            current_state = new_state
            state_list.append(current_state)
        current_state.make_final()
        
    def add_word(self, word):
        prefix_states = self.prefix(word)
        self.add_suffix(word, prefix_states)
        
    def register_get(self, state):
        if state.key in self.reg:
            return self.reg[state.key]
        for reg_state in self.reg.values():
            if reg_state == state:
                return reg_state
        return None
    
    def get_state(self, from_state, trans_symbol):
        return from_state.outputs.get(trans_symbol)
    
    def add_trans(self, from_state, to_state, trans_symbol):
        from_state.outputs[trans_symbol] = to_state
        to_state.inputs[trans_symbol] = from_state
    
    def rem_trans(self, from_state, to_state, trans_symbol):
        if trans_symbol in from_state.outputs:
            from_state.outputs.pop(trans_symbol, None)
        if trans_symbol in to_state.inputs:
            to_state.inputs(trans_symbol, None)

    def replace_or_register(self, word, state_list):
        state_idx = len(state_list) - 1
        word_idx = len(word) - 1
        while state_idx > 0:
            state = state_list[state_idx]
            reg_state = self.register_get(state)
            if reg_state is None:
                # print state.key, "not in register"
                self.reg[state.key] = state
            elif state.key == reg_state.key:
                # print state.key, "is", reg_state.key
                word_idx -= 1
                state_idx -= 1
                continue
            else:
                # print state.key, "==", reg_state.key
                trans_symbol = word[word_idx]
                prev_state = state_list[state_idx - 1]
                state_list[state_idx] = reg_state
                # self.rem_trans(prev_state, state, trans_symbol)
                self.add_trans(prev_state, reg_state, trans_symbol)
            word_idx -= 1
            state_idx -= 1
        
    def find_confluence_index(self, state_list):
        for i in xrange(1, len(state_list)):
            state = state_list[i]
            if len(state.inputs) > 1:
                arcs = 0
                for i_state in state.inputs.values():
                    for v in i_state.outputs.values():
                        if v.key == state.key:
                            arcs += 1
                            if arcs > 1:
                                return i
                # print "CONF:", state.key
                # print "INPUTS:"
                # for k, v in state.inputs.iteritems():
                #     print "%s -%s-> %s" % (v.key, k, state.key)
                #     for k2, v2 in v.outputs.iteritems():
                #         print "  %s -%s-> %s" % (v.key, k2, v2.key)
                # return i
        return -1
        
    def clone_state(self, state):
        clone = self.new_state()
        # for key, val in state.inputs.iteritems():
        #     clone.inputs[key] = val
        clone.final = state.final
        return clone
    
    def make_single_final_state(self):
        nodes = [self.START]
        visited_states = set()
        final_states = []
        while len(nodes) > 0:
            new_nodes = []
            for node in nodes:
                for next_state in node.outputs.itervalues():
                    if next_state.key in visited_states:
                        continue
                    else:
                        new_nodes.append(next_state)
                        visited_states.add(next_state.key)
                    if next_state.final:
                        final_states.append(next_state)
            nodes = new_nodes
        self.FINISH = self.new_state()
        for i in xrange(0, len(final_states)):
            self.add_trans(final_states[i], self.FINISH, "*e*")
            final_states[i].final = False

    def pprint(self):
        printed = set()
        print_str = ""
        nodes = [self.START]
        while len(nodes) > 0:
            new_nodes = []
            for node in nodes:
                for trans_symbol, next_state in node.outputs.iteritems():
                    if next_state.final:
                        print_str += "%s  -%s-> (%s)\n" % (node.key, trans_symbol, next_state.key)
                    else:
                        print_str += "%s  -%s->  %s\n" % (node.key, trans_symbol, next_state.key)
                    if next_state.key not in printed:
                        new_nodes.append(next_state)
                        printed.add(next_state.key)
            nodes = new_nodes
        return print_str

    def to_carmel(self, fout):
        printed = set()
        nodes = [self.START]
        fout.write("%s\n" % self.FINISH.key)
        while len(nodes) > 0:
            new_nodes = []
            for node in nodes:
                for trans_symbol, next_state in node.outputs.iteritems():
                    arc = "%s%s%s" % (node.key, next_state.key, trans_symbol)
                    if arc in printed:
                        continue
                    if trans_symbol == "*e*":
                        fout.write("(%s (%s *e*))\n" % (node.key, next_state.key))
                    else:
                        fout.write("(%s (%s \"%s\"))\n" % (node.key, next_state.key, trans_symbol))
                    new_nodes.append(next_state)
                    printed.add(arc)
            nodes = new_nodes

    def add_min_word(self, word):
        # print self.pprint()
        state_list = self.prefix(word)
        # print [s.key for s in state_list]
        confl_idx = self.find_confluence_index(state_list)
        # print state_list[confl_idx].key
        # print [i for i in state_list[confl_idx].inputs.keys()]
        if confl_idx > -1:
            idx = confl_idx
            while idx < len(state_list):
                # print idx
                prev = state_list[idx - 1]
                cloned = self.clone_state(state_list[idx])
                self.add_trans(prev, cloned, word[idx - 1])
                # print "cloned: %s  -%s-> %s " % (prev.key, word[idx - 1], cloned.key)
                # print cloned.final
                # print cloned.inputs
                # for v in cloned.inputs.values():
                #     print v.key
                state_list[idx] = cloned
                idx += 1
                confl_idx += 1
        
        # print
        # print self.pprint()
        
        self.add_suffix(word, state_list)
        
        # print
        # print self.pprint()
        # print self.pprint()
        self.replace_or_register(word, state_list)


# s0 = State(0, )
# s1 = State(1, )
# s2 = State(2, )
# 
# s3 = State(3, )
# s4 = State(4, )
# 
# s5 = State(5, )
# s6 = State(6, )
# 
# s1.inputs[s0.key] = s0
# s2.inputs[s0.key] = s0
# 
# s1.outputs["y"] = s3
# s1.outputs["x"] = s4
# 
# s2.outputs["y"] = s5
# s2.outputs["x"] = s6
# 
# s3.inputs["y"] = s1
# s4.inputs["x"] = s1
# s5.inputs["y"] = s2
# s6.inputs["x"] = s2
# 
# s3.make_final()
# s4.make_final()
# s5.make_final()
# s6.make_final()


# print s1 == s2


fsa = MinimalIncrFSA()

# fsa.add_min_word("a")
# fsa.add_min_word("aaron")
# fsa.add_min_word("ab")
# fsa.add_min_word("aba")
# print fsa.pprint()
# fsa.add_min_word("abacha")
# print fsa.pprint()

# fsa.make_single_final_state()
# print fsa.pprint()


# i = 0
for line in sys.stdin:
    word = line.replace(" ", "")
    word = word.replace("\n", "")
    fsa.add_word(word)
    
    # print fsa.pprint()
    # print
    
    
    # print fsa.pprint()
    # print "<<%d>>" % i
    # print
    # print

fsa.make_single_final_state()
# print fsa.pprint()
fsa.to_carmel(sys.stdout)
