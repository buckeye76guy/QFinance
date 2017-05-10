__author__= 'JosiahHounyo'

class BinaryTree:
    def __init__(self, root, val, **kwargs):
        '''
        :param root: the name of the root node. i.e. R for time 0, H for up at time 1,
        T for tail, HH, HT etc.
        :param val: the value of the root node
        :param kwargs: up_factor and down_factor: multiplied to the root value.
                        up_value and down_value: when factors not known, these are used.
                        note that the up and down will be given nodes as well i.e. they too
                        will be an instance of this class. Their children will be set as 'None'.
                        Generally None signifies the end of the tree so if either of **kwargs
                        is none, they will be put in place. Please make sure if root is 'R' to have
                        children not None.
        '''
        self.root, self.val = root, val
        assert (len(kwargs) >= 2), "Please provide up_factor/up_value and down_factor/down_value"

        if 'up_factor' in kwargs.keys():
            up = kwargs.get('up_factor')
            if self.root == 'R':
                self.up = {'root': 'H', 'val' : self.val*up if up is not None else None}
            else:
                self.up = {'root': self.root + 'H', 'val': self.val*up if up is not None else None}
        # basically we are creating HH, HT, TH, TT etc as we go
        if 'down_factor' in kwargs.keys():
            down = kwargs.get('down_factor')
            if self.root == 'R':
                self.down = {'root': 'T', 'val': self.val*down if down is not None else None}
            else:
                self.down = {'root': self.root + 'T',
                             'val': self.val*down if down is not None else None}

        if 'up_value' in kwargs.keys():
            up = kwargs.get('up_value')
            if self.root == 'R':
                self.up = {'root': 'H', 'val': up}
            else:
                self.up = {'root': self.root + 'H', 'val': up}

        if 'down_value' in kwargs.keys():
            down = kwargs.get('down_value')
            if self.root == 'R':
                self.down = {'root': 'T', 'val': down}
            else:
                self.down = {'root': self.root + 'T', 'val': down}

    def __str__(self):
        return str({self.root: (self.val, self.up, self.down)})

    def __repr__(self):
        # couldn't recreate tree from str. Many assumptions would have to be made. Idea is to have a small 1 year tree
        # that can be expanded with a good deal of freedom... in fact up factor from 1 year to another could differe, it
        # suffices to insert a new tree with new parameters at the end of a previous one. but such tree would require
        # different rates at different periods during discount. a list would suffice
        return str(self)

    def discount(self, p, r):
        '''
        must be fixed to... if up is a tree, .get('val') can be an issue
        Only on a one period model. This function is irrelvant but I'll leave it here.
        simply avoid using this
        :param p: probability of up
        :param r: rate of interest
        :return: (1/(1+r))*Expected value
        '''
        assert (r > 0 and r < 1), "Please provide a positive rate that is less than 1"
        assert (p >= 0 and p <= 1), "Please provide a valid probability"
        return (1/(1+r))*(p*self.up.get('val') + (1-p)*self.down.get('val'))

    def find(self, node):
        '''
        must add exception checking.
        :param node: HHT, HTT etc...
        :return: value and children if they exist
        '''
        assert (isinstance(node, str)), "Node must be a string!"
        for lt in node:
            if lt not in "HT":
                raise ValueError('Path must contain only "H" and "T".' + lt + ' is not valid.')
        assert (self.depth() >= len(node)), "You can search from root to the leaves of the tree; not beyond (DNE)!"
        if len(node) == 1:
            if node == 'H':
                cursor = self.up
            else:
                cursor = self.down
            return cursor
        else:
            cursor = 'self'
            for root in node:
                if root == 'H':
                    cursor += '.up'
                else:
                    cursor += '.down'
            return eval(cursor)

    def insert(self, node, **kwargs):
        # assumption is that we are inserting a new tree, i.e. updating self_up from dict to tree
        # so make sure node is not already a tree
        # I can now use depth to make sure insertion works. i.e. if depth is not equal to len(node) etc...
        '''
        Need error checking still
        :param node: 
        :param kwargs: 
        :return: 
        '''
        assert (isinstance(node, str)), "Node must be a string!"
        for lt in node:
            if lt not in "HT":
                raise ValueError('Path must contain only "H" and "T".' + lt + ' is not valid.')
        assert (self.depth() >= len(node)), "You can only insert a new tree at the end!" # could be better but...
        if len(node) == 1:
            if node == 'H':
                val = self.up.get('val')
                root = self.up.get('root')
                self.up = BinaryTree(root, val, **kwargs)
            else:
                val = self.down.get('val')
                root = self.down.get('root')
                self.down = BinaryTree(root, val, **kwargs)
        else:
            cursor = 'self'
            for root in node:
                if root == 'H':
                    cursor += '.up'
                else:
                    cursor += '.down'
            # assuming errors are checked and node is reached, we upgrade it to binary tree
            val = eval(cursor + ".get('val')") # because we only insert a tree at a node
            # root = eval(cursor + ".get('root')")
            # that was previously just a dictionary
            exec(cursor + ' = BinaryTree(node, val, **kwargs)')
        return None

    def depth(self):
        '''

        :return: Takes a tree, goes through it i.e. one path until it reaches the end. returns N: number of periods
        '''
        path, flag = '', True
        cursor = self
        while flag:
            if isinstance(cursor.up, dict):
                flag = False
            else:
                path += 'H'
                cursor = cursor.up
        return len(path) + 1

    def cut(self, n, keep = True):
        '''
        :param n: number of periods where to cut the tree
        :return: a new tree with n periods. It would be easy to have a get_up and get_down factors method,
        then simply recreate a tree using these factors. But this will limit some freedom
        :param keep: if this is true, use deepcopy. if not, create a completely different copy
        keep is only now used because having two copies of the same tree may not be good for memory
        '''
        assert (isinstance(n, int)), "Number of years (periods) must be an integer"
        assert (n > 0), "Discount from at least one year in the future"
        assert (n <= self.depth()), "Cannot discount from years past current tree depth"
        N = self.depth()
        if n == N:
            return self
        from itertools import product
        from copy import deepcopy
        if keep:
            temp = deepcopy(self)  # avoid changing the initial tree: inspect input tree, if any bug occurs, fix it
        else:
            temp = self
        paths = product('HT', repeat = n)
        paths = [''.join(node) for node in paths]
        for path in paths:
            cursor = 'temp'
            for root in path:
                if root == 'H':
                    cursor += '.up'
                else:
                    cursor += '.down'
            val = eval(cursor + '.val')
            mydict = {'root':path, 'val':val}
            exec(cursor + '= mydict')
        return temp

    def real_discount(self, N, p, r, keep = True):
        '''
        computes discount from a certain time to present. N should be at least 1 that is. But less than or equal
        to tree depth. Keep in mind this can be useful for options. It is possible to create properties called
        European_call, European_put etc... that use this type of discount function. American options would require
        special handling. Note that this function is really useful when only the end nodes are known.
        By using symbolic python or even bogus placeholder for all other nodes except the last ones, we can discount to
        the present and obtain the true present value. In fact, if one can build a binomial tree using the stock_progress
        function and only update all the last nodes to values of an option, one can discount all of it to the present!
        
        :param N: period we want to discount from. [equal to depth at the moment, future work: N can be less than depth! done]
        :param p: probability of up
        :param r: rate of interest, could be an integer (or a list: future work) of size N! r should probably be restricted to 0 < r < 1
        :param keep: if this is true, use deepcopy. if not, create a completely different copy
        :return: present value
        '''
        assert (isinstance(N, int)), "Number of years (periods) must be an integer"
        assert (N > 0), "Discount from at least one year in the future"
        assert (N <= self.depth()), "N must match number of years(periods) in tree: edit: N <= depth"
        assert (r > 0 and r < 1), "Please provide a positive rate that is less than 1"
        assert (p >= 0 and p <= 1), "Please provide a valid probability"
        from itertools import product
        temp = self.cut(N, keep)

        for step in range(N,0,-1):
            paths = product('HT', repeat = step)
            paths = [''.join(node) for node in paths] # goal is to collapse trees until we get a 1 period tree
            # so we will have to use the exec() again. could create a function that updates a given node but this sort
            # of freedom could be problematic. so no...
            # thanks to itertool, we can advance through the list by pair, i.e. each group of 2 has the same parent node
            length = len(paths)
            for ind in range(0,length,2):
                parent_node = paths[ind][0:-1]
                vals_up = temp.find(parent_node).up.get('val') # since each tree is collapsed to a dictionary, this is ok
                vals_down = temp.find(parent_node).down.get('val')
                disc_val = (1/(1+r))*(p*vals_up + (1-p)*vals_down) # discounted value
                temp_dict = {'root':parent_node, 'val':disc_val}
                cursor = 'temp'
                for root in parent_node:
                    if root == 'H':
                        cursor += '.up'
                    else:
                        cursor += '.down'
                exec(cursor + ' = temp_dict')
        return temp.discount(p, r)

class BDTTree(BinaryTree):
    '''
    This is an extension of the regular BinaryTree except that the discount functions are rewritten.
    insert is fixed so that it allows each subtree to be BDTTree
    '''

    def insert(self, node, **kwargs):
        # assumption is that we are inserting a new tree, i.e. updating self_up from dict to tree
        # so make sure node is not already a tree
        # I can now use depth to make sure insertion works. i.e. if depth is not equal to len(node) etc...
        '''
        Need error checking still
        :param node: 
        :param kwargs: 
        :return: 
        '''
        assert (isinstance(node, str)), "Node must be a string!"
        for lt in node:
            if lt not in "HT":
                raise ValueError('Path must contain only "H" and "T".' + lt + ' is not valid.')
        assert (self.depth() >= len(node)), "You can only insert a new tree at the end!" # could be better but...
        if len(node) == 1:
            if node == 'H':
                val = self.up.get('val')
                root = self.up.get('root')
                self.up = BDTTree(root, val, **kwargs)
            else:
                val = self.down.get('val')
                root = self.down.get('root')
                self.down = BDTTree(root, val, **kwargs)
        else:
            cursor = 'self'
            for root in node:
                if root == 'H':
                    cursor += '.up'
                else:
                    cursor += '.down'
            # assuming errors are checked and node is reached, we upgrade it to binary tree
            val = eval(cursor + ".get('val')") # because we only insert a tree at a node
            # root = eval(cursor + ".get('root')")
            # that was previously just a dictionary
            exec(cursor + ' = BDTTree(node, val, **kwargs)')
        return None

    def real_discount(self, N, p = .5, r = None, keep = True):
        '''
        same thing as original, but this is solely for a BDT tree of rates
        can be used to compute yield.
        This function discounts bond values by actually making sure that only the last nodes
        are of the form F/(1+r), the subsequent are just (1+r) times the future values.
        Use this on any type of tree!
        :param N: 
        :param p: 
        :param r: 
        :param keep: this should always be true for BDT
        :return: 
        '''
        assert (isinstance(N, int)), "Number of years (periods) must be an integer"
        assert (N > 0), "Discount from at least one year in the future"
        assert (N <= self.depth()), "N must match number of years(periods) in tree: edit: N <= depth"
        assert (p >= 0 and p <= 1), "Please provide a valid probability"
        from itertools import product

        if N == 1:
            temp = self.cut(1, keep)
            u = temp.up.get('val')
            d = temp.down.get('val')
            r = temp.val
            return (1 / (1 + r)) * (p/(1+u) + (1 - p)/(1+d))

        temp = self.cut(N, keep)
        for step in range(N, 0, -1):
            paths = product('HT', repeat=step)
            paths = [''.join(node) for node in paths]
            length = len(paths)
            for ind in range(0, length, 2):
                parent_node = paths[ind][0:-1]
                vals_up = temp.find(parent_node).up.get('val')
                vals_down = temp.find(parent_node).down.get('val')
                rate = temp.find(parent_node).val
                if step == N:
                    disc_val = (1/(1+rate))*(p/(1+vals_up) + (1-p)/(1+vals_down))
                else:
                    disc_val = (1/(1+rate))*(p*vals_up + (1-p)*vals_down)
                temp_dict = {'root': parent_node, 'val': disc_val}
                # print(temp_dict)
                cursor = 'temp'
                for root in parent_node:
                    if root == 'H':
                        cursor += '.up'
                    else:
                        cursor += '.down'
                exec(cursor + ' = temp_dict')
        u = temp.up.get('val')
        d = temp.down.get('val')
        r = temp.val
        return (1/(1+r))*(p*u + (1-p)*d)

def stock_progress(S_0, u, d, N):
    '''
    Basic stock progression
    :param S_0: Initial value of stock
    :param u: up factor
    :param d: down factor
    :param N: number of periods
    :return: binary tree with the right nodes and values
    '''
    assert (N > 0); "N should be at least 1. Otherwise stock progress isn't of interest"
    from itertools import product
    tree = BinaryTree('R', S_0, up_factor = u, down_factor = d)
    if N == 1:
        return tree # simply stop here

    for i in range(1,N):
        paths = product('HT', repeat = i)
        paths = [''.join(node) for node in paths]
        for node in paths:
            tree.insert(node, up_factor = u, down_factor = d)
    return tree

# a = BinaryTree('R', 12, up_value=24, down_value=6)
# a.insert('H', up_factor = 2, down_factor = .5)
# a.insert('T', up_factor = 2, down_factor = .5)
# a.insert('HH', up_factor = 2, down_factor = .5)
# a.insert('HT', up_factor = 2, down_factor = .5)
# a.insert('TH', up_factor = 2, down_factor = .5)
# a.insert('TT', up_factor = 2, down_factor = .5)

# print(a)
# print(a.find('HH'))
# print(a.find('HT'))
# print(a.find('TH'))
# print(a.find('TT'))
# print(a.depth())
# print(a.real_discount(3, .4, .1))
# print(a)

# b = stock_progress(12,2,.5,1)
# c = stock_progress(12,2,.5,3)
# d = c.cut(1)
# e = BDTTree('R',.1,up_value=.1432,down_value=.0979)
# e.insert('H',up_value=.1942,down_value=.1377)
# e.insert('T',up_value=.1377,down_value=.0976)
# e.insert('HH',up_value=.2179,down_value=.1606)
# e.insert('HT',up_value=.1606,down_value=.1183)
# e.insert('TH',up_value=.1606,down_value=.1183)
# e.insert('TT',up_value=.1183,down_value=.0872)
# print(b)
# print(c)
# print(d)
# print(c.real_discount(2, .4, .1))
# print(type(e.find('HH')))
# print(e.real_discount(1)**(-1/4) - 1)
# f = e.up
# print(f)
# print(e.find('H'))
# print(f.real_discount(1)**(-1/2)-1)
# might consider creating an equal property for trees, in fact this could be easy if itertools is used again