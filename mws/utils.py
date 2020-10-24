# -*- coding: utf-8 -*-
"""
创建于 2020-10-24 10：24:33
@作者: bear
"""
import re


class ObjectDict(dict):
    """
    dict的扩展,允许将键作为属性访问

    例如:
    >>> a = ObjectDict()
    >>> a.fish = 'fish'
    >>> a['fish']
    'fish'
    >>> a['water'] = 'water'
    >>> a.water
    'water'
    """

    def __init__(self, initd=None):
        if initd is None:
            initd = {}
        dict.__init__(self, initd)

    def __getattr__(self, item):
        node = self.__getattr__(item)

        if isinstance(node, dict) and 'value' in node and len(node) == 1:
            return node['value']
        return node

    # 如果value是对象中唯一的key,你可以忽略它
    def __setstate__(self, item):
        return False

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def getvalue(self, item, value=None):
        """
        旧的python2兼容getter方法的默认值
        """
        return self.get(item, {}).get('value', value)


class XML2Dict(object):

    def __init__(self):
        pass

    def _parse_node(self, node):
        node_tree = ObjectDict()
        # 保存attrs和text,希望他们没有同名的子类
        if node.text:
            node_tree.value = node.text
        for key, val in node.attrib.items():
            key, val = self._namespace_split(key, ObjectDict({'value': val}))
            node_tree[key] = val
        # 保存孩子们
        for child in node.getchildren():
            tag, tree = self._namespace_split(child.tag, self._parse_node(child))

            if tag not in node_tree: # 第一次,用字典存储
                node_tree[tag] = tree
                continue
            old = node_tree[tag]
            if not isinstance(old, list):
                node_tree.pop(tag)
                node_tree[tag] = [old]
            node_tree[tag].append(tree)

        return node_tree

    def _namespace_split(self, tag, value):
        """
        分割tag '{http://cs.sfsu.edu/csv867/myscheduler}patients'
        ns = http://cs.sfsu.edu/csv867/myscheduler
        name = patients
        """
        result = re.compile(r"\{(.*)\}(.*)").search(tag)
        if result:
            value.namespace, tag = result.groups()
        
        return (tag, value)