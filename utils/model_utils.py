import types


class ModelUtils:
    
    
    @staticmethod
    def join_models(model_list1, model_list2, model1_attr, model2_attr, setter_name, set_as_array = False, getter_name = None):
        """
            sets a model or an attribute from model_list2 on a model from model_list1 
            if model1_attr matches model2_attr
            if set_as_array == True, will set list of model2 otherwise will set last one found 
        """
        temp_hash = {}
        
        for model2 in model_list2:
            if hasattr(model2,model2_attr):
                model2_key = getattr(model2, model2_attr)
                
                if set_as_array:
                    if model2_key not in temp_hash:
                        temp_hash[model2_key] = []
                    
                    temp_hash[model2_key].append(model2)
                else:
                    temp_hash[model2_key] = model2
        
        
        for model1 in model_list1:
            if hasattr(model1,model1_attr):

                model1_key = getattr(model1, model1_attr)
                if type(model1_key) == types.MethodType:
                    model1_key = model1_key()
                
                if model1_key in temp_hash:
                    #if getter_name, then call that, otherwise use model2 as value
                    to_set = temp_hash[model1_key]
                    if getter_name:
                        getter = getattr(to_set, getter_name)
                        if type(getter) == types.MethodType:
                            to_set = getter()
                        else:
                            to_set = getattr(to_set, getter_name)
                    
                    setter = getattr(model1, setter_name)
                    if type(setter) == types.MethodType:
                        setter(to_set)
                    else:
                        setattr(model1, setter_name, to_set)
        