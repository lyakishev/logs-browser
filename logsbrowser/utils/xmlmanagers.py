from xml.etree import ElementTree as ET
import fnmatch
import re

class QueriesManager(object):

    def __init__(self, source_xml):
        self.xml = source_xml

    @property
    def queries(self):
        xml = ET.parse(self.xml)
        q = {}
        for i in xml.getroot().find('queries'):
            q[i.attrib['name']] = i.text
        return q

    @property
    def filters(self):
        xml = ET.parse(self.xml)
        q = {}
        for i in xml.getroot().find('filters'):
            rows = []
            for r in i:
                rows.append((r.attrib['column'],
                             r.attrib['color'],
                             r.attrib['clause']))
            q[i.attrib['name']] = rows
        return q

    @property
    def default_query(self):
        xml = ET.parse(self.xml)
        for i in xml.getroot().find('queries'):
            if int(i.attrib['default']) == 1:
                return i.attrib['name']
        return i.attrib['name']

    @property
    def default_filter(self):
        xml = ET.parse(self.xml)
        for i in xml.getroot().find('filters'):
            if int(i.attrib['default']) == 1:
                return i.attrib['name']
        return i.attrib['name']

class SourceManager(object):

    def __init__(self, source_xml):
        self.xml = source_xml

    @property
    def stands(self):
        xml = ET.parse(self.xml)
        return [i.attrib['name'] for i in xml.getroot()]

    def get_filelog_sources(self, stand):
        xml = ET.parse(self.xml)
        return [f.text for f in xml.getroot().find('stand[@name="%s"]' % stand).find('filelogs')]

    def get_evlog_sources(self, stand):
        xml = ET.parse(self.xml)
        evlogs = {}
        for f in xml.getroot().find('stand[@name="%s"]' % stand).find('evlogs'):
            evlogs[f.attrib['server']] = [t.strip() for t in f.text.split(',')]
        return evlogs

    @property
    def default_stand(self):
        xml = ET.parse(self.xml)
        for i in xml.getroot():
            try:
                if int(i.attrib['default']) == 1:
                    return i.attrib['name']
            except KeyError:
                continue
        return i.attrib['name']


class SelectManager(object):

    operator_map = {"glob": fnmatch.fnmatch,
                    "regexp": lambda name, pat: re.search(pat, name),
                    "=": lambda name, pat: name == pat,
                    "contains": lambda name, pat: pat in name,
                    "iregexp": lambda name, pat: re.search(pat, name, re.I),
                    "icontains": lambda name, pat: pat.lower() in name.lower()}

    type_map = {"file": ("f,"),
                "dir": ("d, "),
                "all": ("d", "f"),
                "path": ()}
    
    operation_map = {'select': 'select',
                   'unselect': 'unselect'}

    def __init__(self, source_xml):
        self.xml = source_xml

    def get_attributes(self):
        return ["operation", "type", "operator", "rule"]
    
    def get_actions(self, actions_name):
        xml = ET.parse(self.xml)
        actions = []
        for action in xml.getroot().find('select[@name="%s"]/actions' % actions_name):
            attrib = action.attrib
            attrib_list = []
            for a in self.get_attributes():
                attrib_list.append(attrib[a])
            actions.append(attrib_list)
        return actions
    
    def empty_action(self):
        return None

    def new_select(self, new_name, new_actions):
        xml = ET.parse(self.xml)
        root = xml.getroot()
        select = ET.SubElement(root, "select", {"name": new_name})
        actions = ET.SubElement(select, "actions", {})
        for action in new_actions:
            ET.SubElement(actions, "action", action)
        tree = ET.ElementTree(root)
        tree.write(self.xml, encoding="utf-8")
                   
    def update_actions(self, old_name, new_name, new_actions):
        xml = ET.parse(self.xml)
        root = xml.getroot()
        select = root.find('select[@name="%s"]' % old_name)
        select.clear()
        select.attrib['name'] = new_name
        actions = ET.SubElement(select, "actions", {})
        for action in new_actions:
            ET.SubElement(actions, "action", action)
        tree = ET.ElementTree(root)
        tree.write(self.xml, encoding="utf-8")

    @property
    def selects(self):
        print 'call'
        xml = ET.parse(self.xml)
        return [i.attrib['name'] for i in xml.getroot()]

    def parse_action(self, attrib):
        def action(type_, path_, name_, select, unselect):
            operation = attrib['operation']
            if operation == self.operation_map["select"]:
                act = select
            elif operation == self.operation_map["unselect"]:
                act = unselect
            a_type = attrib['type']
            if a_type != 'path':
                if type_ in self.type_map[a_type]:
                    if bool(self.operator_map[attrib['operator']](name_, attrib["rule"])):
                        act()
            else:
                if bool(self.operator_map[attrib['operator']](path_, attrib["rule"])):
                    act()
        return action

    def save_pathes(self, name, pathes):
        xml = ET.parse(self.xml)
        root = xml.getroot()
        select = ET.SubElement(root, "select", {'name': name})
        actions = ET.SubElement(select, "actions")
        for path in pathes:
            try:
                path.encode('utf8')
            except UnicodeDecodeError:
                continue
            attrib = {"operation": "select", "type": "path", "operator": "=", "rule": path}
            ET.SubElement(actions, "action", attrib)
        tree = ET.ElementTree(root)
        tree.write(self.xml, encoding="utf-8")
        

    def get_select_actions(self, select):
        xml = ET.parse(self.xml)
        actions = []
        for action in xml.getroot().find('select[@name="%s"]/actions' % select):
            actions.append(self.parse_action(action.attrib))
        return actions
    
    def delete_select(self, select_name):
        xml = ET.parse(self.xml)
        root = xml.getroot()
        select = root.find('select[@name="%s"]' % select_name)
        root.remove(select)
        tree = ET.ElementTree(root)
        tree.write(self.xml, encoding="utf-8")
        


if __name__ == '__main__':
    pass

