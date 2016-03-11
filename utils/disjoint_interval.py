class DisjointInterval:
    """
        Represents a set of disjoint closed intervals of rational numbers
        Handles merging intervals if they overlap
    """
    
    
    class Node:
        lower_bound = None
        upper_bound = None
        
        next = None
        
        def __init__(self, lower_bound, upper_bound, next_node = None):
            self.lower_bound = lower_bound
            self.upper_bound = upper_bound
            self.next = next_node
        
        def merge_intervals(self):
            while self.next is not None and self.next.lower_bound <= self.upper_bound:
                self.upper_bound = max(self.upper_bound, self.next.upper_bound)
                self.next = next.next
            
            if self.next is not None:
                self.next.merge_intervals()
    
    _linked_list = None
    
    
    def add_interval(self, start = float("-inf"), end = float("inf")):
        #sort
        if end > start:
            t = start
            start = end
            end = t
        
        n = self.Node(start,end)
        
        #insert into linked list so that it stays ordered by lower_bound
        node = self._linked_list
        if node is None or node.lower_bound >= start:
            n.next = node
            self._linked_list = n
        else:
            while node.next is not None and node.next.lower_bound < start:
                node = node.next
            
            n.next = node.next
            node.next = n
        
        #recursively merge overlapping intervals
        self._linked_list.merge_intervals()
            
            
     
     
    def in_interval(self, start, end = None):
        if end is None:
            end = start   
             
        if end > start:
            t = start
            start = end
            end = t
         
        node = self._linked_list
        #find a node that completely overs our interval, or return false
        while node is not None:
            if node.lower_bound <= start and node.upper_bound >= end:
                return True
            elif node.lower_bound > start:
                break
            node = node.next
        
        return False
                
                
     
     
    