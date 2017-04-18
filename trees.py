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
        return str(self)

    def discount(self, p, r):
        '''
        must be fixed to... if up is a tree, .get('val') can be an issue
        :param p: probability of up
        :param r: rate of interest
        :return: (1/(1+r))*Expected value
        '''
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

    def real_discount(self, N):
        '''
        computes discount from a certain time to present. N should be at least 1 that is. But less than or equal
        to tree depth. Keep in mind this can be useful for options. It is possible to create properties called
        European_call, European_put etc... that use this type of discount function. American options would require
        special handling.
        :param N: period we want to discount from
        :return: present value
        '''
        assert (isinstance(N, int)), "Number of years (periods) must be an integer"
        assert (N > 0), "Discount from at least one year in the future"
        assert (N <= self.depth()), "Cannot discount from years past current tree depth"
        pass


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

a = BinaryTree('R', 12, up_value=24, down_value=6)
a.insert('H', up_factor = 2, down_factor = .5)
a.insert('T', up_factor = 2, down_factor = .5)
a.insert('HH', up_factor = 2, down_factor = .5)
a.insert('HT', up_factor = 2, down_factor = .5)
a.insert('TH', up_factor = 2, down_factor = .5)
a.insert('TT', up_factor = 2, down_factor = .5)

print(a)
print(a.find('HH'))
print(a.find('HT'))
print(a.find('TH'))
print(a.find('TT'))
print(a.depth())

b = stock_progress(12,2,.5,3)
print(b)
print(b.depth())
# might consider creating an equal property for trees, in fact this could be easy if itertools is used again