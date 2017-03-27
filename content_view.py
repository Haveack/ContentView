# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET
import sys
import os


class Node():
    def __init__(self, vtype, vid):
        self.vtype = vtype
        self.vid = vid
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def children(self):
        return self.children

    def __str__(self):
        if self.vid is None:
            return self.vtype + ': None'
        else:
            return self.vtype + ':' + self.vid
        # return self.vtype + ':'
        # + (self.vid if self.vid is not None else 'no id')

    def __repr(self):
        return self.__str__()


class Model():
    def __init__(self, root):
        self.root = root

    def __str__(self):
        return self.root.type + ":" + self.root.id


ns = {'android': 'http://schemas.android.com/apk/res/android'}


def process(source, sink):
    model = parse(source)
    write(model, sink)


def parse(path):
    tree = ET.parse(path)
    root = tree.getroot()
    model = parse_iter(root)
    return model


def parse_iter(xml_node):
    vid = get_id(xml_node)
    node = Node(xml_node.tag, vid)
    # print node
    for child in xml_node:
        node.add_child(parse_iter(child))
    return node


def get_id(xml_node):
    try:
        id = xml_node.attrib['{' + ns['android'] + '}id']
        return id[5:]
    except KeyError:
        return None


def get_content(model, layout):
    content = 'private static class ContentView {\n'
    content += '    static final int LAYOUT_ID = ' + convert_layoutid(layout) + ";\n"
    content += '\n'
    content += "    View root;\n"

    flatten = flatten_required_views(model)
    # content += traverse(model)
    for e in flatten:
        content += get_line(e)
    content += '\n'
    content += '    ContentView(View v) {\n'
    content += '        this.root = v;\n'
    content += '\n'
    for e in flatten:
        type_cast = '' if convert_type(e.vtype) == "View" else '(' + convert_type(e.vtype) + ')'
        content += '        this.' + convertName(e.vid) + ' = ' + type_cast + ' v.findViewById(R.id.' + e.vid + ');\n'
    content += '    }\n'

    content += """
    static ContentView attachTo(Window window) {
        View root =
            View.inflate(window.getContext(), LAYOUT_ID, ViewUtils.getAndroidContainer(window));
        return new ContentView(root);
    }
"""

    content += '}\n'
    return content


def flatten_required_views(root):
    result = []
    if root.vid is not None:
        result.append(root)
    for child in root.children:
        child_results = flatten_required_views(child)
        for child_result in child_results:
            result.append(child_result)
    return result


def traverse(root):
    result = ''
    if root.vid is not None:
        result += get_line(root)
    for child in root.children:
        result += traverse(child)
    return result


def get_line(node):
    return '    public ' + node.vtype + ' ' + convertName(node.vid) + ';\n'


def write(model, path):
    pass


def convertName(xml_name):
    s = list(xml_name)
    for i in range(len(s)):
        if s[i] == '_':
            s[i + 1] = s[i + 1].upper()
    name = "".join(s)
    name = name.replace('_', '')
    return name


def convert_type(xml_type):
    if xml_type == "include":
        return "ViewGroup"
    else:
        return xml_type


def convert_layoutid(path):
    return 'R.layout.' + os.path.basename(path)[:-4]


def main():
    if len(sys.argv) == 2:
        model = parse(sys.argv[1])
        print get_content(model, sys.argv[1])
    elif len(sys.argv) == 3:
        process(sys.argv[1], sys.argv[2])
    else:
        print 'Please specify layout file and target path'


if __name__ == "__main__":
    main()
