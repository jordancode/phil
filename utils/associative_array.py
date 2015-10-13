
SORT_HI_TO_LO = True
SORT_LO_TO_HI = False

class AssociativeArray:
    
    class Node:
        _key = None
        value = None
        
        next = None
        previous = None
        
        def __init__(self, key, value, next_node = None, previous_node = None):
            self._key = key
            self.value = value
            self.next = next_node
            self.previous = previous_node
        
        @property
        def key(self):
            return self._key
            
        
        def remove(self):
            if not self.previous:
                if self.next:
                    self.next.previous = None
            else:
                self.previous.next = self.next
                if self.next:
                    self.next.previous = self.previous
        
    
    
        
    _sort_order = None
    
    _linked_list = None
    _key_to_node = None
    
    @property
    def sort_order(self):
        return self._sort_order
    
    def __init__(self, sort_order = SORT_LO_TO_HI):
        self._sort_order = sort_order
        self._key_to_node = {}

    
    def __len__(self):
        return len(self._key_to_node)
    
    
    def __setitem__(self, key, value):
        if not isinstance( key, int ) or key < 0:
            raise KeyError()
        
        if key in self._key_to_node:
            self._key_to_node[key].value = value
        else:
            
            n = self.Node(key, value)
            
            node = self._linked_list
            if node is None:
                self._linked_list = n
            else:
                while node.next is not None and self._is_before(node.next, n):
                    node = node.next
                
                if node.next is not None:
                    node.next.previous = n
                    
                node.next = n
            
            self._key_to_node[key] = n
    
    
    def _is_before(self,node_a,node_b):
        if self._sort_order == SORT_LO_TO_HI:
            return node_a.key < node_b.key
        else:
            return node_b.key < node_a.key
    
    
    def get_range(self, start_key = None, count = None):
        ret = []
        
        if start_key is None:
            node = self._linked_list
        else:
            node = self._key_to_node[start_key]
            
        while node is not None and count is None or count > len(ret):
            ret.append(node)
            node = node.next
            
        return ret   
            
            
        
    def __getitem__(self, key):
        if isinstance( key, int ) and key >= 0 :
            return self._key_to_node[key].value
        else:
            raise KeyError()
        
    def __delitem__(self,key):
        if not isinstance( key, int ) or key < 0  :
            raise KeyError()
        
        del self._key_to_node[key]
        self._key_to_node[key].remove()
        
    def __iter__(self):
        node = self._linked_list
        while node is not None:
            yield node
            node = node.next

    
    def to_list(self):
        return self.get_range(None, None)
    
    def to_dict(self):
        return {(k, n.value) for (k,n) in self._key_to_node.items()}
    
    def keys(self):
        ret = []
        node = self._linked_list
        while node is not None:
            ret.append(node.key)
            node = node.next
            
        return ret