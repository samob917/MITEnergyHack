import pandas as pd
import matplotlib.pyplot as plt
import seaborn
import pandas as pd
import xml.etree.ElementTree as et

def parse_XML(xml_file, df_cols): 
    """Parse the input XML file and store the result in a pandas 
    DataFrame with the given columns. 
    
    The first element of df_cols is supposed to be the identifier 
    variable, which is an attribute of each node element in the 
    XML data; other features will be parsed from the text content 
    of each sub-element. 
    """
    
    xtree = et.parse(xml_file)
    xroot = xtree.getroot()
    rows = []
    
    for node in xroot: 
        res = []
        res.append(node.attrib.get(df_cols[0]))
        for el in df_cols[1:]: 
            if node is not None and node.find(el) is not None:
                res.append(node.find(el).text)
            else: 
                res.append(None)
        rows.append({df_cols[i]: res[i] 
                     for i, _ in enumerate(df_cols)})
    
    out_df = pd.DataFrame(rows, columns=df_cols)
        
    return out_df




if __name__ == '__main__':
    tree = et.parse("REFIT_BUILDING_SURVEY.xml")
    root = tree.getroot()
    print()
    print("-------------- LEVEL 1 -------------------")
    print()
    for child in root: 
        print(child.tag, child.attrib)
        print()
        print("-------------- LEVEL 2 -------------------")
        print()
        for gchild in child:
            print(gchild.tag, gchild.attrib)
            print()
            print("-------------- LEVEL 3 -------------------")
            print()
            for ggchild in gchild:
                print(ggchild.tag, ggchild.attrib)
                print()
                print("-------------- LEVEL 4 -------------------")
                print()
                for gggchild in ggchild:
                    print(gggchild.tag, gggchild.attrib)
                    print()
                    print("-------------- LEVEL 5 -------------------")
                    print()
                    for g4child in gggchild:
                        print(g4child.tag, g4child.attrib)
                        print()
                        print("-------------- LEVEL 6 -------------------")
                        print()
                        for g5child in g4child:
                             print(g5child.tag, g5child.attrib)
                             print()
                             print("-------------- LEVEL 7 -------------------")
                             print()
                             for g6child in g5child:
                                print(g6child.tag, g6child.attrib)
