import requests
import lxml.etree
import tempfile
import os

#Current local election notice of election PDF for Isle of Wight - looks to be same format-ish as before
#url='https://www.iwight.com/azservices/documents/1174-Notice-of-Poll-IOWC-2017.pdf'


def _get_url(url):
    #Read in the Notice of Poll PDF
    return requests.get(url).content

def pdftoxml(fn):
    """converts pdf file to xml file"""

    xmlin = tempfile.NamedTemporaryFile(mode='r', suffix='.xml')
    tmpxml = xmlin.name  # "temph.xml"

    cmd = 'pdftohtml -xml -nodrm -zoom 1.5 -enc UTF-8 -noframes %s "%s" "%s"' % (
        '', fn, os.path.splitext(tmpxml)[0])
    # can't turn off output, so throw away even stderr yeuch
    cmd = cmd + " >/dev/null 2>&1"
    os.system(cmd)
    
    root = lxml.etree.parse(tmpxml)#lxml.etree.fromstring(xmldata)
    #xmlfin = open(tmpxml)
    xmldata = xmlin.read()
    xmlin.close()

    pages = list(root.getroot())
    return pages

# this function has to work recursively because we might have "<b>Part1 <i>part 2</i></b>"
def gettext_with_bi_tags(el):
    res = [ ]
    if el.text:
        res.append(el.text)
    for lel in el:
        res.append("<%s>" % lel.tag)
        res.append(gettext_with_bi_tags(lel))
        res.append("</%s>" % lel.tag)
        if el.tail:
            res.append(el.tail)
    return "".join(res).strip()

def _parse_pages(pages):
    #Scrape the separate pages
    #print(pages)
    for page in pages:
        data={'stations':[]}
        phase=0
        for el in page:
            #print(el.attrib, gettext_with_bi_tags(el))
            if 'Election of' in gettext_with_bi_tags(el):
                phase=1
                continue
            tmp=gettext_with_bi_tags(el).strip()
            if phase==1:
                if tmp=='':pass
                else:
                    data['ward']=tmp
                    phase=phase+1
            elif phase==2:
                if 'Proposers' in tmp:
                    phase=3
                    record={'candidate':[],'address':[],'desc':[],'proposers':[],'seconders':[]}
                    data['list']=[]
                    continue
            elif phase==3:
                if tmp.strip()=='':
                    phase=4
                    #print('-------------------------------')
                    data['list'].append(record)
                    continue
                elif int(el.attrib['left'])<100:
                    if record['address']!=[]:
                        data['list'].append(record)
                        record={'candidate':[],'address':[],'desc':[],'proposers':[],'seconders':[]}
                    record['candidate'].append(tmp)
                elif int(el.attrib['left'])<300: record['address'].append(tmp)
                elif int(el.attrib['left'])<450: record['desc'].append(tmp)
                elif int(el.attrib['left'])<600:
                    if tmp.startswith('('): record['proposers'][-1]=record['proposers'][-1]+' '+tmp
                    elif len(record['proposers'])>0 and record['proposers'][-1].strip().endswith('-'): record['proposers'][-1]=record['proposers'][-1]+tmp
                    elif len(record['proposers'])>0 and record['proposers'][-1].strip().endswith('.'): record['proposers'][-1]=record['proposers'][-1]+' '+tmp
                    else: record['proposers'].append(tmp)
                elif int(el.attrib['left'])<750:
                    if tmp.startswith('('): record['seconders'][-1]=record['seconders'][-1]+' '+tmp
                    elif len(record['seconders'])>0 and record['seconders'][-1].strip().endswith('-'): record['seconders'][-1]=record['seconders'][-1]+tmp
                    elif len(record['seconders'])>0 and record['seconders'][-1].strip().endswith('.'): record['seconders'][-1]=record['seconders'][-1]+' '+tmp
                    else: record['seconders'].append(tmp)
            elif phase==4:
                if 'persons entitled to vote' in tmp:
                    phase=5
                    record={'station':[],'range':[]}
                    continue
            elif phase==5: #Not implemented... TO DO
                #print(el.attrib, gettext_with_bi_tags(el))
                if tmp.strip()=='':
                    data['stations'].append(record)
                    break #The following bits are broken...
                #need to add situation
                elif int(el.attrib['left'])<100:
                    if record['range']!=[]:
                        data['stations'].append(record)
                        record={'situation':[],'station':[],'range':[]}
                    record['station'].append(tmp)
                elif int(el.attrib['left'])>300:
                    record['range'].append(tmp)
        #print(data)
        tmpdata=[]
        for station in data['stations']:
            tmpdata.append({'ward':data['ward'],
                            #'situation':' '.join(station['situation']),
                            'station':' '.join(station['station']),
                            'range':' '.join(station['range'])})
        #scraperwiki.sqlite.save(unique_keys=[], table_name='stations', data=tmpdata)
        stations = tmpdata
        
        tmpdata=[]
        tmpdata2=[]
        for candidate in data['list']:
            tmpdata.append( {#'year':year,
                             'ward':data['ward'],
                             'candidate':' '.join(candidate['candidate']),#.encode('ascii','ignore'),
                             'address':' '.join(candidate['address']),
                             'desc':' '.join(candidate['desc']) } )
            party=' '.join(candidate['desc']).replace('Candidate','').strip()
            cand=' '.join(candidate['candidate'])#.encode('ascii','ignore')
            cs=cand.strip(' ').split(' ')
            if len(cs)>2:
                cand2=cs[:2]
                for ci in cs[2:]:
                    cand2.append(ci[0]+'.')
            else: cand2=cs
            ctmp=cand2[0]
            cand2.remove(ctmp)
            cand2.append(ctmp.title())
            candi=' '.join(cand2)#.encode('ascii','ignore')
            for proposer in candidate['proposers']:
                if proposer.find('(+)')>-1:
                    proposer=proposer.replace('(+)','').strip()
                    typ='proposer'
                else:typ='assentor'
                tmpdata2.append({ #'year':year,
                                 'ward':data['ward'],
                                 'candidate':cand, 
                                 'candinit':candi,
                                 'support':proposer,
                                 'role':'proposal',
                                 'typ':typ,
                                 'desc':party}.copy())
            for seconder in candidate['seconders']:
                if seconder.find('(++)')>-1:
                    seconder=seconder.replace('(++)','').strip()#.encode('ascii','ignore')
                    typ='seconder'
                else:typ='assentor'
                tmpdata2.append({ #'year':year,
                                 'ward':data['ward'],
                                 'candidate':cand, 
                                 'candinit':candi,
                                 'support':seconder,
                                 'role':'seconding',
                                 'typ':typ, 
                                 'desc':party }.copy())
    return stations, tmpdata, tmpdata2
    
def get_nop_data(fn,dbname):
    os.environ["SCRAPERWIKI_DATABASE_NAME"] ='sqlite:///{}'.format(dbname)
    #The scraperwiki package loads the dbname as global from the env var
    import scraperwiki
    
    pages = pdftoxml(fn)
    stations, tmpdata, tmpdata2 = _parse_pages(pages)
    scraperwiki.sqlite.save(unique_keys=[], table_name='stations', data=tmpdata)
    scraperwiki.sqlite.save(unique_keys=[], table_name='candidates', data=tmpdata)
    scraperwiki.sqlite.save(unique_keys=[], table_name='support', data=tmpdata2)