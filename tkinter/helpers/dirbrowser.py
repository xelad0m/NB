import os, sys
from tkinter import *
from tkinter.ttk import *

CHECKED = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\x9aIDAT8\x8d\xa5\x93A\x12\x83 \x0cE\x7f,\xbbn<\x97\xd7u\xc6\xcb1\xd3\xd7\rRP\xa2`\xb3\x03\xf2~\x92?\xc4\x00\xf4G\x04I2\xb3!\xc8L\x13\x08\x80P\xde\xf7\xc0\xaf\xa0\xb0F}\xf6\xf34R\xf9=k^\xa3b\xd5\r@\x1a\xe1\xb2\x83T9\xc3\x8b%\xb6W`C\xd9\xec\xc5d\x92\x00~#l\x882\xe9\x06\xceq\xf2\xe0(r\x05W\x02\xe5\xe3\x0e\xdd\xc1R\xc3\xc4\xd6\x18\x0e\\{\xe0%{\x95k\x19\x9d\xabz\x86\x1eP\\\x81\x8e\x00`\xe8'\xb6\xa2\xdc\x85G[\x19R/\x8f;\xf8\x02\xad3`\xed\x07\x12|h\x00\x00\x00\x00IEND\xaeB`\x82"
UNCHECKED = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00<IDAT8\x8d\xed\x93!\x12\x00 \x0c\xc3Rn\xff\xffr\x11C\xcc2\x0cb\xf1MUd\xdb<\x10\x00\x92Zc\xdb)8\xdcZ\x0c\xb0Z\xd7\x85\x11\x8c\xe0\x0fAm\xa1Ue@V\xd5e\x03\xa8\x9c\x0c \x00\x9enB\x00\x00\x00\x00IEND\xaeB`\x82"
TRISTATE = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x04\x98zTXtRaw profile type exif\x00\x00x\xda\xadWYr\xc5(\x0c\xfc\xe7\x14s\x04$\xb1\x1e\x87\xb5jn0\xc7\x9ff\xb1\xf3\xf6\xbc\x97\xc4\x94\r\xc8\xb2\xd4t\x03\xb6U\xfb\xef\xdf\xae\xfe\xc1\xc1l\xb42\xd6\x07\x17\x9d\xd38L4\x91\x13\x1aA\xaf#\xce+i3\xaf\xbb\xa3\x8f\xc6\x95]\x9d7\x18&A-\xab\xeb\xd3\xf6O\xb0\xdb\xaf\x07\x8e\x1c\x94\xaf\xed*\xec;\x1cv :\x03\xcfCF\xe6\xd1\xae\x97 a\xe7e\'\xb3\x03\xc5\xb6\x1a.\x06\x7f\t5\xef@e;N(\xfb4\'\xacU\x8d\xbe\xba2x\xb0T-\x12\ts\x13\x12=\xafa!\x90u&X\x08W\x163\xfcD\xd0\xd6\xe2\x14*#\xc7\x90@\xc8\xd5\xf0N\x02\xf5%AW$\x1f-u\xcb\xfe\xd9\xba!\x9f\xd3\xb6\xcb\r\x97ns\x84\xc6\xc3\x1bdo\xecr\xa6\xe1\xcb\xc4r"\xe2\xeb\x1b!i\x7f7\x9c}\xf6^C\xefm\x8d.\x19\x07F\xdd\x9eQ\x93l:\xc2\xc01\x83r\x99\x8f9\x14\x8f\xd3\xa2\xedg\x89(A\'] y\xd5Eg\x94B\x91\x18\xaatE\x86*%\xea\xd4f]\xa8\x00\xa2\xe1\xc6\x1e5sa\x99\xb6 \x9e#\x17\xe8C\x10\x07\x85:{\x89R%@\xb9\xc2MA>#|b\xa1\x997\xce|\x85\x022W\x82+\x13\x82\x11\x1eyZ\xd4\xab\x9b\x9f\x14\xd5{\x19\x14\x91\x0e\'W\xc0\xc5c^\x03\xc6Pn\\\xe1\x05A\xa8o\xdd\xec$\xf8([~}1\x7f0U\xa1\xa0\x9d4\x07\x0c0\xe9\xbcBdK_sK\xa6\xce\x02?\x8bz-!R\xbe\xee\x00\xa0\x08\xb9-\xc0`\t\x18\xd2\x8e\xc4\x92#\xed\x99=\x11x\x0c\x10(\x01\xf9X\x1b\x19\n\x90\xb5\\\x01\x92\xb12\x1c+\xcf\x81Gn<\xe3i\xfa\xb2e\xc7\xc3\x8c\xbd\tBXq\xe2\xa1M\x94\x04\xb1\x8c\xb1\x98?\xde\x04\xcc\xa1d\xc5\x1ak\xad\xb3\xde\x06e\xa3MN\x9cq\xd69\xe7\xdd\xd8\xe4\x92\x17o\xbc\xf5\xce{\x1f|\xf4)H0\xc1\x06\x17|\x08!\x86\x149\n\xf6@\x1b]\xf41\xc4\x18Sb\x95\x90(!V\x82\x7f\x82%s\x96l\xb2\xcd.\xfb\x1cr\xcc\xa9`\xfa\x14Slq\xc5\x97PbI\x95\xabTl\x13\xd5U_C\x8d55R\r;E3\xcd6\xd7|\x0b-\xb6\xd41\xd7\xbat\xd3mw\xdd\xf7\xd0cO\xa7j[\xd5\xbb\xf2\x81j\xb4U\xe3\xa9\xd4\xf0\xf3\xa7j\xb0*\xef\x8f\x104\xb6\x13;4\x83bl\x08\x8a\xfb\xa1\x00&4\x0f\xcdt cx(74\xd3q\xeci\x96\x01\xd2\x0emT\xa5\xa1\x18$4\x8d\xd8v:\xb5\xfbR\xee-\xdd\x94\ro\xe9\xc6\xdf)\xa7\x86t\x7f\xa1\x9c\x82t\xf7\xba=P\xad\x8e\xf7\\\x99\x8a\xadU88\xd5\x82\xd5\x07\x9f\xc4A\xe1\xd4\x1a\x97\xdf\xd6\xbf\n$\xed\xcb\xa4\xfe\x00\xcc\xc3@\xd2z\x7f\x1f\x87\xb4\x9af3\x17e\xa4y3\xcdi|\x00\xfc\xb8V\xb3\x01\x91V\xe0&\xa6\x87 \x99w\x1e\x07\xf5\xf2\x99?\xcb2w\xe7$\x87#J\x0f\x17\x81\xb2K\xd3\xdcI\xf7X\x7f\xad\x9a\x94\xdeV\xbcP\xa5\xb1n\xe5\x08\x1fz\xc5\x9biCh\xe2\x96\xd9\x99^\xaa\xee\xce\xae@\xb9\x9b*\xdd\xc6\xd7d~\xc7\xa5zI\xe2\x9b\xdc\x85\x8a\x1dr\xd8k\x94\x8e\xdd\xb9\xc6\r\xb9\xe2\xb1\xea\xee\xf2/V\x9f\x90\xaa>\x9b\xca\xcfIT\xafX4z\x0f\xac\x84\x9e=\x9e\xb4\xab_\xb3\xb4\x00\xd3\x8ez9\x8f.A\xcbj\xf6\xe2\xb0\xd7]\xf1pI\xc3~\xa0g\x86"e\xc9\xff3vo\xa2\xaa\xab\xb0\x07\xa9\x07\xeb\xae \xeeX~\xaf\x17\xdc|\xaf\xcd)\x8f\xcf\x89\xce\x98\xf6t\x91\x1f;\xf9\n\xec<ec\t\xbf\x08\x99}\xc3^\x9b\xf4\xe8\x11\xf6=\xe3k\x8e\xcdw\xf4\xc6/Dq\xb1\x8f7\x86]\xee\xa1\xf8\x16\x1d\xcd\x0e\xfe\x00^F\t\xb3\x837\x92U\xab\x81/6|\x10\x0c\x87Vc7\xf0\x19\xc3\xd9\xb1\xce\x98\xe5\xab\t\xe1vZ\xe7K\xa3\xa2\xd5\x8eO\xd8\xd4M\xacqu\xf1\x99\xde\x93=\xd2Qq;I\x89=&z\xe8\xa5\xee\xdcZXi}\x8d\xd4]\xa3\x1bX_\xf0\xcc1f\xe7+\x91\xc2;\xa0\x1e\xe3<\x86y\xd1tugg\xea\x92\xce(q=\x84\x91$D\x1c\x18\xd5\x83\xa1\xe8\'Cz\x89U}\x0f\xfa=\xcc\xea\x06\xf4\x0b\xf0\x17\xd8\xe3=V\xf5\x0e\xb1\xef`V\x1f\x13\xfd\x04\xbb:\xc1\xbf)\xfb\xb3Z\xfd\x8c\xda{\x94\xea\xa3\xb4/j\xf5\x0b\xc5\xaf`\xa9?\x81s\x1d\xe8#Xw\xb5zv\xe3\xd3\xfa6\xd0\x03\x1c\xef\xd5\xea\x0f\xc0\xdc\x06\xc2\xdf]\xc7\xd7\xe9\xff\x1f\x8a \x1a\xb9\x01\xa4\xf2\x00\x00\x01\x85iCCPICC profile\x00\x00x\x9c}\x91=H\xc3@\x1c\xc5_[\xa5\xa2\x15\x87v(\xe2\x90\xa1:Y\x14\x15\x11\\\xb4\nE\xa8\x10j\x85V\x1dL.\xfd\x10\x9a4$).\x8e\x82k\xc1\xc1\x8f\xc5\xaa\x83\x8b\xb3\xae\x0e\xae\x82 \xf8\x01\xe2\xe4\xe8\xa4\xe8"%\xfe/)\xb4\x88\xf1\xe0\xb8\x1f\xef\xee=\xee\xde\x01\xfez\x99\xa9f\xc7(\xa0j\x96\x91N&\x84lnE\x08\xbe\xa2\x07Q\x841\x8d\x11\x89\x99\xfa\xac(\xa6\xe09\xbe\xee\xe1\xe3\xeb]\x9cgy\x9f\xfbs\xf4*y\x93\x01>\x81x\x86\xe9\x86E\xbcN<\xb9i\xe9\x9c\xf7\x89#\xac$)\xc4\xe7\xc4\xc3\x06]\x90\xf8\x91\xeb\xb2\xcbo\x9c\x8b\x0e\xfbyf\xc4\xc8\xa4\xe7\x88#\xc4B\xb1\x8d\xe56f%C%\x9e \x8e)\xaaF\xf9\xfe\xac\xcb\n\xe7-\xcej\xb9\xca\x9a\xf7\xe4/\x0c\xe5\xb5\xe5%\xae\xd3\x1c@\x12\x0bX\x84\x08\x012\xaa\xd8@\x19\x16\xe2\xb4j\xa4\x98H\xd3~\xc2\xc3\xdf\xef\xf8Er\xc9\xe4\xda\x00#\xc7<*P!9~\xf0?\xf8\xdd\xadY\x18\x1fs\x93B\t\xa0\xf3\xc5\xb6?\x06\x81\xe0.\xd0\xa8\xd9\xf6\xf7\xb1m7N\x80\xc03p\xa5\xb5\xfc\x95:0\xf5Iz\xad\xa5\xc5\x8e\x80\xbem\xe0\xe2\xba\xa5\xc9{\xc0\xe5\x0e\x10}\xd2%Cr\xa4\x00M\x7f\xa1\x00\xbc\x9f\xd17\xe5\x80\xf0-\xd0\xbd\xea\xf6\xd6\xdc\xc7\xe9\x03\x90\xa1\xaeR7\xc0\xc1!0T\xa4\xec5\x8fww\xb5\xf7\xf6\xef\x99f\x7f?\xf9\xe9r\xdd\xca\x8fqU\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe4\x0b\x18\x14\x06-\xab\xd6M\n\x00\x00\x00\xadIDAT8\xcb\xa5\x93\xbd\r\xc20\x10F\xdf%,\xc0\x12\xd9\x85\x92.\x92\'`\x02f\xa0GJ\x8fd)\x1d\xfb\x84)\x18\x00}\x14\x18\xcbA$v\x92k|\x85\xdf\xb3u?&Il\x88\x1d\x80\x99-\x82$\xddCz4I23\xbc\xfcP\x02\x9fpM\x1f\xf2\x03\xa2Z\xf2r\n\xb7\xe1\xac\xd6\xc2Ot)\x16\xfc\xc2\x1d~0\xb3s,"\xc0\x1e\xd7\xa4\x17\xe6\xe0T\x1e\x7f\xd0\x02/\xa0\x0fP\t<\x12\\\xb9=\\\xc8\xfbBx$\xa8\xa9\xd5\xe1\x876\x91\xe4\xe0\xbfEL%9x\xb2\x0b_I\x0e\x9emc\t\xbch\x90\xa6"\xee\xc2\x9a\x90\xf4\x19\xa4-\x1b\xfd\x06\x99\xf0M\xd6\x80\xb6z\xce\x00\x00\x00\x00IEND\xaeB`\x82'
BROKEN = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00sIDAT8\x8d\xa5\x93Q\x0e\xc0 \x08C\x1f\x8b\xf7\xbfr\xf7\xa1K\x9cR3]\x7f\x95\x07\xa5!$\x89\x1f*\x00\x11qT,\xa9\x02\x9av)\x02\xb8\x8eZw\x9a\x00jd\xd3rz\x9b\x00\x01\x91}\x14(\x12\x9b\xa9\x85\x11\xe2\x8a\x81\xd7\x12-\xc4\x15\xdb\tvd\x01\xcf\xd8n'K\xc0\xe8y\x05Ic\xcc<;H\x1a\xa3\x1b\xf7s\x8c;\xeac<\xba\xca\x02\xf5\xaaNu\x03\xc1v&$\x044\xdbM\x00\x00\x00\x00IEND\xaeB`\x82"

class CheckboxTreeview(Treeview):
    """
        Treeview widget with checkboxes left of each item.
        The checkboxes are done via the image attribute of the item, so to keep
        the checkbox, you cannot add an image to the item.
        
        Once taged 'broken' node cant be switched to other tag (for bad format items)
        
        based on https://stackoverflow.com/questions/5104330/how-to-create-a-tree-view-with-checkboxes-in-python
        and https://github.com/TkinterEP/ttkwidgets
    """

    def __init__(self, master=None, **options):
        if "dirfont" in options:
            font = options["dirfont"]
            del options["dirfont"]                  # иначе _tkinter.TclError: unknown option "-font"
        else: font = None

        Treeview.__init__(self, master, **options)
        # checkboxes are implemented with pictures
        self.im_checked = PhotoImage(data=CHECKED).subsample(1)         # scale factor (int)
        self.im_unchecked = PhotoImage(data=UNCHECKED).subsample(1)
        self.im_tristate = PhotoImage(data=TRISTATE).subsample(1)
        self.im_broken = PhotoImage(data=BROKEN).subsample(1)
        self.tag_configure("unchecked", image=self.im_unchecked)
        self.tag_configure("tristate", image=self.im_tristate)
        self.tag_configure("checked", image=self.im_checked)
        self.tag_configure("broken", image=self.im_broken)
        self.tag_configure("dir", font=font)
        self.protected_tags = ("broken", "dir")                         # защищенные, "неисключающие" тэги
        # check / uncheck boxes on click
        self.bind("<Button-1>", self.box_click, True)

        self.style = Style()
        self.style.configure("Treeview.Heading", font=font)
    
    def __len__(self):
        return 'Not implemented'

    def set_tag(self, iid, tag):
        """set tag to item, save protected tags
        iid == item 
        """
        p_tags = tuple(t for t in self.item(iid, "tags") if t in self.protected_tags)
        if tag not in p_tags:
            self.item(iid, tags=p_tags + (tag,))

    def insert(self, parent, index, iid=None, **kw):
        """ same method as for standard treeview but add the tag 'unchecked'
            automatically if no tag among ('checked', 'unchecked', 'tristate')
            is given """
        if not "tags" in kw:
            kw["tags"] = ("unchecked",)
        else:
            kw["tags"] = kw["tags"] + ("unchecked",)
        return Treeview.insert(self, parent, index, iid, **kw)

    def check_childrens(self, item):
        """ check the boxes of item's descendants """
        children = self.get_children(item)
        for iid in children:
            tags = self.item(iid, "tags")
            if not ("broken" in tags): self.set_tag(iid, "checked")
            self.check_childrens(iid)

    def check_parents(self, item):
        """ check the box of item and change the state of the boxes of item's
            ancestors accordingly """
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["checked" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is not checked and item's box is checked
                self.tristate_parent(parent)
            else:
                # all boxes of the children (кроме 'broken') are checked
                self.check_parents(parent)

    def tristate_parent(self, item):
        """ put the box of item in tristate and change the state of the boxes of
            item's ancestors accordingly """
        self.set_tag(item, "tristate")
        parent = self.parent(item)
        if parent:
            self.tristate_parent(parent)

    def uncheck_childrens(self, item):
        """ uncheck the boxes of item's descendant """
        children = self.get_children(item)
        for iid in children:
            tags = self.item(iid, "tags")
            if not ("broken" in tags): self.set_tag(iid, "unchecked")
            self.uncheck_childrens(iid)

    def uncheck_parents(self, item):
        """ uncheck the box of item and change the state of the boxes of item's
            ancestors accordingly """
        self.set_tag(item, "unchecked")
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["unchecked" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is checked and item's box is unchecked
                self.tristate_parent(parent)
            else:
                # no box is checked
                self.uncheck_parents(parent)
    
    # recursive generator
    def checked(self, root=''):
        childrens = self.get_children(root)
        for iid in childrens:
            tags = self.item(iid, "tags")
            if self.get_children(iid):
                if ("checked" in tags):
                    yield self.item(iid)
                yield from self.checked(iid)                    # вся магия в yield from
            else:
                if ("checked" in tags):
                    yield self.item(iid)

    # recursive generator
    def tagged(self, root='', in_tags=(), ex_tags=()):
        childrens = self.get_children(root)
        for iid in childrens:
            tags = self.item(iid, "tags")
            fltr = [t in tags for t in in_tags] + [a not in tags for a in ex_tags]     
            if self.get_children(iid):
                if False not in fltr:
                    yield self.item(iid)
                yield from self.tagged(iid, in_tags, ex_tags)
            else:
                if False not in fltr:
                    yield self.item(iid) 


    def box_click(self, event):
        """ check or uncheck box when clicked """
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify_element(x, y)                    # or identify("element", x, y) -> part of item
        if "image" in elem:
            # a box was clicked
            iid = self.identify("item", x, y)
            tags = self.item(iid, "tags")
            if not ("broken" in tags):
                if ("unchecked" in tags) or ("tristate" in tags):
                    self.set_tag(iid, "checked")
                    self.check_parents(iid)
                    self.check_childrens(iid)
                else:                                           # if item "checked"
                    self.set_tag(iid, "unchecked")
                    self.uncheck_childrens(iid)
                    self.uncheck_parents(iid)


class DirBrowserTree(CheckboxTreeview):

    def __init__(self, parent=None, startpath='/', progressVar=None, **options):
        self.treeview = CheckboxTreeview(master=parent, **options)
        self.progressVar = progressVar
        
        self.treeview.column("Size", anchor=E, width=self.treeview.winfo_width()//4)
        self.treeview.column("size", anchor=E)
        self.treeview.heading('#0', text='Name')        
        self.treeview.heading('Size', text='Size')

        if startpath: self.new_root(self.treeview, startpath)

    def _readable_size(self, size=0):
        if type(size) == type(1):
            if size > 0:
                for x in ['b', 'KB', 'MB', 'GB', 'TB']:
                    if size < 1024:
                        return "%.2f %s" % (size, x)
                    size /= 1024
            else: return 0
        else: return 0
    
    def _sort(self, path, listdir):
        dirs, files = [], []
        for name in listdir:
            p = os.path.join(path, name)
            if os.path.isdir(p) and not os.path.islink(p):
                ptype = 'directory'
                dirs.append((name, ptype))
            else:
                ptype = 'file'
                files.append((name, ptype))                     # линки считаем файлами и по ним не переходим
        dirs.sort(key = lambda x: x[0])
        files.sort(key = lambda x: x[0])
        return dirs + files                                     # сначала папки потом файлы
 

    def fill_tree(self, treeview, node, progressVar=None):
        """ обход каждой директории вручную рекурсивно через os.listdir()
        через os.walk() можно, но не сказать, что будет проще
        """
        path = treeview.set(node, column="fullpath")            # get "fullpath" value from node

        try:
            listdir = os.listdir(path)
        except PermissionError:                                 # skip system dirs
            pass
        else:
            listdir = self._sort(path, listdir)                                                   
            for (i, (basename, ptype)) in enumerate(listdir):   # i для оценки прогресса сканирования больших объемов папок
                p = os.path.join(path, basename)
                if os.path.exists(p):                           # пропустить файлы, которые не существуют, а их овер9000
                    try:
                        size = os.path.getsize(p) if ptype == 'file' else '-'
                    except:
                        size = 0 
                        print(sys.exc_info()[1])
                    else:
                        if hasattr(progressVar, 'set'):         # i.e. progressVar != None
                            progressVar.set( ((i+1) / len(listdir)) * 100 )
                        rsize = self._readable_size(size) if size != '-' else '-' 
                        tags = ("dir", ) if ptype=="directory" else ("file",)
                        iid = treeview.insert(node, 'end', text=basename, values=(p, ptype, size, rsize), tags=tags)
                        if ptype == 'directory':
                            self.fill_tree(treeview, iid, None) # фьють

    def remove_node(self, iid):
        self.treeview.uncheck_parents(iid)
        self.treeview.delete(iid)
    
    def new_root(self, treeview, startpath):
        dfpath = os.path.abspath(startpath)
        dname = os.path.basename(dfpath)
        iid = treeview.insert('', 'end', text=dname,
                values=[dfpath, "directory", '-', '-'], tags=("dir", ), open=True)
        self.fill_tree(treeview, iid, progressVar=self.progressVar)

if __name__ == "__main__":
    # test
    def test_checked():
        for item in tv.treeview.checked():
            print(item)
        print()
    
    def test_tagged():
        for item in tv.treeview.tagged(in_tags=('checked',), ex_tags=('dir',)):   # включая "checked", исключая "dir"
            print(item)
        print()

    root = Tk()
    options= dict(columns=("fullpath", "type", "size", "Size"),
                  displaycolumns=("Size",),
                  selectmode="extended",
                  dirfont=("Sans", 9, "bold"))
    
    tv = DirBrowserTree(root, startpath=os.getcwd(), **options)
    tv.treeview.pack(fill='both', expand=True)
    btn1 = Button(root, text='checked', command=test_checked)
    btn2 = Button(root, text='tagged', command=test_tagged)
    btn1.pack()
    btn2.pack()
    root.mainloop()