import numpy as np
import math

class Fuzzy_system:
    def __init__ (self, post_var, former_vars):
        '''
        former_var, post_var : a fuzzy variable with fuzzy_sets, stored by dictionary
        '''
        self.former_vars = former_vars
        self.post_var = post_var
        self.rule_set = {}      #{(A,B): C}
        self.t_norm = min
        self.t_conorm = maximum
        self.implication = mandani
        self.defuzzifier = gravity_center
    def output(self, crisp_inputs):
        if type(crisp_inputs) != tuple:
            raise TypeError("crisp_inputs must be tuple type")
        if len(crisp_inputs) != len(self.former_vars):
            raise IndexError("Number of input is illegal, it must be %d, but it's %d" % (len(self.former_vars), len(crisp_inputs))) 

        rule_funcs = []
        for former_fuzzysets, post_fuzzyset in self.rule_set.items():
            f_var_outputs = []
            for crisp, f_var, f_set in zip(crisp_inputs, self.former_vars, former_fuzzysets):
                f_var_outputs.append(f_var[f_set](crisp))
            act_strengh = self.t_norm(f_var_outputs)
            rule_member_func = self.implication(act_strengh, self.post_var[post_fuzzyset]) 
            rule_funcs.append(rule_member_func)
        output_member_func = self.t_conorm(rule_funcs)
        output = self.defuzzifier(output_member_func)
        return output

    def set_rule(self, post_set_name, former_set_names):
        if type(former_set_names) != tuple:
            raise TypeError("former_set_names must be tuple type")
        if len(former_set_names) != len(self.former_vars):
            raise IndexError("Number of former_varible is illegal, it must be %d, but it's %d" % (len(self.former_vars), len(former_set_names)))
        self.rule_set[former_set_names] = post_set_name
        
    @staticmethod
    def set_fuzzy_var(var, fuzzy_set_name, mean, dev, var_set = 'medium'):
        '''
        var : a container, dictionary, of fuzzy_variable.
        fuzzy_set_name : name of fuzzy_set 
        mean : the mean of membership func
        dev ; the deviation of mebership func
        '''
        if type(var) is not dict :
            raise TypeError("var must be dictionary type")
        if var_set == 'medium':
            var[fuzzy_set_name] = get_member_funtion(mean, dev)
        elif var_set == 'small':
            var[fuzzy_set_name] = get_member_funtion(mean, dev, small=True)
        else:
            var[fuzzy_set_name] = get_member_funtion(mean, dev, large=True)         

def get_member_funtion(mean, dev, small = False, large = False):
    def gaussian(x):
        if (small and x < mean) or (large and x > mean):
            return 1
        result = math.exp(-(x - mean)**2 / (2*dev**2))
        return result
    return gaussian
def mandani(act_strengh, post_member_func):
    def imp(x):
        return min(act_strengh, post_member_func(x))
    return imp
def maximum(funcs):                             # the maximum composition of functions
    def composition(x):
        out = []
        for func in funcs:
            out.append(func(x))
        return max(out)
    return composition
def gravity_center(func):
    range_min = -40
    range_max = 40
    num = (range_max - range_min)*5
    weight_val_sum = val_sum = 0
    for x in np.linspace(range_min, range_max, num, True):
        val = func(x)
        val_sum += val
        weight_val_sum += val * x
    return weight_val_sum / val_sum if val_sum != 0 else 0
