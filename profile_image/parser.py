import ast

class PrintChanger(ast.NodeTransformer):
    def generic_visit(self, node):
        return super().generic_visit(node)
    
    def visit_Expr(self, node):

        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if(node.value.func.id == 'print'):
                    #print("we gotta print")
                    #print(ast.dump(node))
                    return super().generic_visit(node)
        return super().generic_visit(node)
    
    def visit_Import(self, node):
        #print(ast.dump(node))
        return super().generic_visit(node)

    def visit_Assign(self, node):
        #print(ast.dump(node))
        return super().generic_visit(node)

    


class Profiler(ast.NodeTransformer):
    def generic_visit(self, node):
        return super().generic_visit(node)

    def visit_Module(self, node):

        write_f_node = ast.parse('f.write("time,name\\n")').body[0]
        open_f_node = ast.parse('f = open("ftimes.csv","w")').body[0]
        write_l_node = ast.parse('l.write("time,name\\n")').body[0]
        open_l_node = ast.parse('l = open("ltimes.csv","w")').body[0]
        import_time_node = ast.parse('import time').body[0]

        node.body.insert(0,write_l_node)
        node.body.insert(0,open_l_node)
        node.body.insert(0,write_f_node)
        node.body.insert(0,open_f_node)
        node.body.insert(0,import_time_node)
        ast.fix_missing_locations(node)
        return super().generic_visit(node)

    def visit_FunctionDef(self, node):
        #Profiler.insert_print(node, "In Function " + node.name + "()",0)
        Profiler.insert_write(node, "In Function "+node.name+"()",0,"f")
        Profiler.insert_write(node,"Leaving Function "+node.name+"()",len(node.body),"f")
        #print(ast.dump(node))
        return super().generic_visit(node)

    #def visit_Call(self, node):
        
        #print(node.func)
    #    if isinstance(node.func, ast.Name):
    #        if(node.func.id == 'print'):
                #print("we gotta print")
    #            new_node = ast.copy_location(ast.Call(
    #                func=ast.Name(id='print',ctx=ast.Load()),
    #                args=[ast.Str("")],
    #                keywords=[]),
    #                node
    #            )
    #            return super().generic_visit(new_node)
#
 #       return super().generic_visit(node)

    def visit_Name(self, node):
        #print(node.id)
        return super().generic_visit(node)

    def visit_Expr(self, node):
        #print(ast.dump(node))
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if(node.value.func.id == 'print'):
                    #print("we gotta print")
                    return super().generic_visit(node)
        return super().generic_visit(node)

    def visit_While(self, node):
        #Profiler.insert_print(node,"In While Loop",0)
        Profiler.insert_write(node, "Top of While Loop",0,"l")
        Profiler.insert_write(node,"Bottom of While Loop",len(node.body),"l")
        return super().generic_visit(node)

    def visit_For(self, node):
        #Profiler.insert_print(node,"In For Loop",0)
        Profiler.insert_write(node, "Top of For Loop",0,"l")
        Profiler.insert_write(node, "Bottom of For Loop",len(node.body),"l")
        return super().generic_visit(node)

    def insert_write(node, str, location, file):

        
        #print(ast.dump(my_node))
        #print(ast.dump(my_node.body[0]))
        func_str = "," + str + "\\n"
        my_node = ast.parse(file+'.write(str(time.time())+"'+func_str+'")')
        new_node = ast.copy_location(ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(
                        id='f',
                        ctx=ast.Load()
                    ),
                    attr='write',
                    ctx=ast.Load()
                ),
                args=[ast.BinOp(
                    left=ast.Call(
                        func=ast.Name(
                            id='str',
                            ctx=ast.Load()
                        ),
                        args=[ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(
                                    id='time',
                                    ctx=ast.Load()
                                ),
                                attr='time',
                                ctx=ast.Load()
                            ),
                            args=[],
                            keywords=[]
                        )],
                        keywords=[]

                    ),
                    op=ast.Add(),
                    right=ast.Str(func_str)
                )],
                keywords=[]
            )
        ),node.body[0])
        node.body.insert(location,my_node.body[0])
        #node.body.insert(location,new_node)
        ast.fix_missing_locations(node)
        return node

    def insert_print(node, str, location):
        #print(node.body)

        


        func_str = str + ","
        new_node = ast.copy_location(ast.Expr(
            value=ast.Call(
                func=ast.Name(id='print',ctx=ast.Load()),
                args=[

                    ast.Str(func_str),
                    ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(
                                id='time',
                                ctx=ast.Load()
                            ),
                            attr='time',
                            ctx=ast.Load()
                        ),
                        args=[],
                        keywords=[]
                    )

                    
                ],
                keywords=[]
                )
                ),
                node.body[0]
            )
        node.body.insert(location,new_node)
        ast.fix_missing_locations(node)
        #print(node.body)
        return node

def inOrderTree(node):
    print(node)
    if isinstance(node, ast.mod):
        print("mod!")
    if isinstance(node, ast.FunctionDef):
        print("function def!")
        print(node.name)
        print(node.body)
        new_node = ast.copy_location(ast.Expr(
            value=ast.Call(
                func=ast.Name(id='print',ctx=ast.Load()),
                args=[ast.Str(node.name)],
                keywords=[])),
                node.body[0]
            )
        print(new_node)
        node.body.insert(0,new_node)
        ast.fix_missing_locations(node)
        print(node.body)
    for lowernode in ast.iter_child_nodes(node):
        inOrderTree(lowernode)



from sys import argv    

filecontents = open(argv[1]).read()
parsed = ast.parse(filecontents)
#print(ast.dump(parsed, False, True))
#print(parsed._fields)
#print("\n\n\n")
#print("in order tree:")
#inOrderTree(parsed)
my_print_changer = PrintChanger()
print_modified = my_print_changer.visit(parsed)

del argv[0]
print(argv)
my_profiler = Profiler()
transformed = my_profiler.visit(print_modified)
ast.fix_missing_locations(transformed)
result = compile(transformed,'blah','exec')
exec(result)
something = ast.parse('print("hello")')
something_comp = compile(something,'fd','exec')
exec(something_comp)



    
    
