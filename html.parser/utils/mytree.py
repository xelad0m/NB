from html.parser import HTMLParser


class Node:
    def __init__(self, id, tag, attrs, par=None):
        self.id = id
        self.tag = tag
        self.par = par
        self.attrs = {}
        if attrs != []:
            for attr, value in attrs:
                self.attrs.update({attr: value})
        self.data = ""
        self.tail = ""
        self.chi = []


class Tree:
    def __init__(self):
        self.stack = list()
        self.tree = list()
        root_node = Node(0, "_root_", [], par=None)
        self.stack.append(root_node)
        self.tree.append(root_node)
    
    def __iter__(self):
        self.iter = iter(self.find_by_id(0).chi)                        # итерировать по индексам потомков рута
        return self

    def __next__(self):
        subroot_id = next(self.iter)
        return self.find(ID=subroot_id)                                 # возвращать поддерево с корнем в руте

    def find_by_id(self, ID):
        res = None
        for n in self.tree:
            if n.id == ID:
                res = n
                break
        return res

    def recursive_finder(self, subtree, node):
        subtree.tree.append(node)
        for child_id in node.chi:
            self.recursive_finder(subtree, self.find_by_id(child_id))

    def find(self, tag='', attrs={}, ID=False, find_first=True):
        res = Tree()
        for n in self.tree:
            if not ID:                                                                                       # если поиск не по id
                d_in_d = lambda d1, d2: all([(k, v) in d2.items() for (k, v) in d1.items()])                 # dict in dict expression
                if n.tag == tag and d_in_d(attrs, n.attrs):            
                    res.tree[0].chi.append(n.id)                                                             # root tags goes to _root_.chi
                    self.recursive_finder(res, n)                                                            # add all child nodes
                    if find_first: break                                                                     # find first or all
            else:
                if n.id == ID:
                    res.tree[0].chi.append(n.id)
                    self.recursive_finder(res, n)                                                            # add all child nodes
                    break
        
        return res

    def find_all(self, tag='', attrs={}):
        return self.find(tag, attrs, ID=False, find_first=False)

    def text(self):
        res = ''
        for n in self.tree:
            res += n.data + ' ' + n.tail + ' '
        return res.strip()
    
    def data(self):
        res = ''
        for n in self.tree:
            res += n.data + ' '
        return res.strip()

    def tail(self):
        res = ''
        for n in self.tree:
            res += n.tail + ' '
        return res.strip()


class TreeBuilder(HTMLParser, Tree):
    def __init__(self, source=None):
        HTMLParser.__init__(self)  # родительский инит
        Tree.__init__(self)
        self.id = 0
        self.is_last_tag_open = False
        if source: 
            self.feed(source)   # parent method to feed data source
        # self.close()      # force to handle all buffered data (as parser.goahead(end=True)) - usefull if stopped due to error

    def _is_tag_in_stack(self, tag):
        position = -1
        for i, n in enumerate(self.stack):
            if n.tag == tag:
                position = i                # выше всего в стеке
        if position == -1:
            return False
        else:
            return position
                
    def handle_starttag(self, tag, attrs):
        self.id += 1
        self.is_last_tag_open = True
        parent = self.stack[-1].id
        node = Node(self.id, tag, attrs, par=parent)
        self.stack.append(node)

    def handle_endtag(self, tag):
        self.is_last_tag_open = False
        if tag == self.stack[-1].tag:       # закрывающий тэг соответствует тому что в стеке, т.е. все ОК
            node = self.stack.pop()
            self.stack[-1].chi.append(node.id)
            self.tree.append(node)
        else:                               # Два варианта:
            pos = self._is_tag_in_stack(tag)
            if pos:                         # 1.тэг есть в стеке - закрыть и выпихнуть все после него
                for n in self.stack[pos:]:    
                    parent = self.stack[-1].id
                    node = self.stack.pop()
                    self.stack[-1].chi.append(node.id)
                    self.tree.append(node)
            else:                           # 2. тэга нет в стеке - создать пустой элемент под сломанный тэг
                self.id += 1                    
                parent = self.stack[-1].id
                node = Node(self.id, tag, attrs={}, par=parent)
                self.stack[-1].chi.append(node.id)
                self.tree.append(node)


    def handle_data(self, data):
        if self.is_last_tag_open:
            self.stack[-1].data = data.strip()
        else:
            self.tree[-1].tail = data.strip()

    def handle_comment(self, data):
        ...

    def handle_entityref(self, name):
        ...

    def handle_charref(self, name):
        ...

    def handle_decl(self, data):
        ...

    def buildElementTree(self):
        ...
    
    def error(self, message):
        ...


if __name__ == '__main__':
    
    # Test code

    content = """<html>
        <head>
            <title>Example page</title>
        </head>
        <body>
            <p>Moved to <a href="http://example.org/">example.org</a>
            or <a href="http://example.com/">example.com</a>.</p>
        </body>
    </html>
    """
    content1 = """<html>
        <head>
            <title>Example page</title>
            </broken>broken<broken>broken1<broken>broken2<broken>broken3<broken>broken4<broken>broken5
        </head>
        <body>
            <p>Moved to <a href="http://example.org/">                                 example&amp;org</a>
            or <a href="http://example.com/">example&#39;com                  </a>                        .</p>
        </body>
    </html>
    """
    content2 = "<a><b>1<c>2<d/>3</c></b>4</a><a><b>1<c>2<d/>3</c></b>4</a>"  # the a element has None for both text and tail attributes, the b element has text "1" and tail "4", the c element has text "2" and tail None, and the d element has text None and tail "3".
    content3 = '<a href="asdas"/>some tail'
    content4 = "<a/>"
    content5 = 'd<dd'       # not implemented

    etree = TreeBuilder(content)

    print('Testing mytree parser find:')
    print('-'*100)
    body = etree.find("body")
    a = body.find("a", {"href": "http://example.org/"})
    print('Text from <a href= http://example.org/">:', a.text())
    a = body.find("a", {"href": "http://example.com/"})
    print('Text from <a href= http://example.com/">:', a.text())