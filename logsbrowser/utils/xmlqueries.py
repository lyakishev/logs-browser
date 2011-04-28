from xml.etree import ElementTree as ET
class QueriesManager(object):

    def __init__(self, source_xml):
        self.xml = source_xml

    @property
    def queries(self):
        xml = ET.parse(self.xml)
        q = {}
        for i in xml.getroot():
            q[i.attrib['name']] = i.text
        return q

    @property
    def default(self):
        xml = ET.parse(self.xml)
        q = {}
        for i in xml.getroot():
            if int(i.attrib['default']) == 1:
                return i.attrib['name']
        return i.attrib['name']

if __name__ == '__main__':
    q = QueryManager('queries.xml')
    print q.queries

