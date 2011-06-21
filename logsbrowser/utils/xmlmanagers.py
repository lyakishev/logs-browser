from xml.etree import ElementTree as ET
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


if __name__ == '__main__':
    q = QueryManager('queries.xml')
    print q.queries

