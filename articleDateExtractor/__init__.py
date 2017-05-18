# coding=utf-8
# last-updated = Zeon Trevor Fernando
# Added additional meta-tags to find out published dates/creation dates of web pages
# Added additional regular expressions to extract last updated text from both German and English web pages

__author__ = 'Ran Geva'
import sys
import urllib2,re, json
from dateparser import parse
try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

regexStrings = {
    'year': '(?:197[0-9]|198[0-9]|199[0-9]|200[0-9]|201[0-9]|202[0-9]|203[0-9]|[0-3][0-9])',
    'month': '(?:10|11|12|(?:0|)[1-9])',
    'month_string': '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)',
    'month_string_de': '(?:jan|feb|märz|apr|mai|juni|juli|aug|sept|okt|nov|dez|januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember)',
    'day': '(?:1[0-9]|2[0-9]|30|31|[0]{0,1}[1-9])',
    'hour': '(?:(?:0|)[0-9]|1[0-9]|2[0-3])',
    'minute': '(?:0[0-9]|[1-5][0-9])',
    'second': '(?:0[0-9]|[1-5][0-9])',
    'opt_slash': "\/?",
    'opt_slashes': "(?:\/|)+",
    'opt_sep': "(?:[\-\/\.]|)"
    }

def parseStrDate(dateString, rDate = None):
    try:
        if rDate is None:
            dateTimeObj = parse(dateString, date_formats=['%Y%m%d%H%M%S'])
            return dateTimeObj
        else:
            dateTimeObj = parse(dateString, date_formats=['%Y%m%d%H%M%S'], settings={'RELATIVE_BASE':rDate})#
            return dateTimeObj    
    except:
        return None

# Try to extract from the article URL - simple but might work as a fallback
def _extractFromURL(url):

    #Regex by Newspaper3k  - https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
    m = re.search(r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    if m:
        return parseStrDate(m.group(0))


    return  None

def _extractFromLDJson(parsedHTML):
    jsonDate = None
    try:
        script = parsedHTML.find('script', type='application/ld+json')
        if script is None:
            return None

        data = json.loads(script.text)

        try:
            jsonDate = parseStrDate(data['datePublished'])
        except Exception, e:
            pass

        if jsonDate is None:
            try:
                jsonDate = parseStrDate(data['dateCreated'])
            except Exception, e:
                pass


    except Exception, e:
        return None



    return jsonDate


def _extractFromMeta(parsedHTML):
    print "extractMeta"
    metaDate = None
    for meta in parsedHTML.findAll("meta"):
        metaName = meta.get('name', '').lower()
        itemProp = meta.get('itemprop', '').lower()
        httpEquiv = meta.get('http-equiv', '').lower()
        metaProperty = meta.get('property', '').lower()

        #<meta name="pubdate" content="2015-11-26T07:11:02Z" >
        if 'pubdate' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name='publishdate' content='201511261006'/>
        if 'publishdate' == metaName:
            metaDate = meta['content'].strip()
            break

        if 'erstellungsdatum' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
        if 'timestamp' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DC.date.issued" content="2015-11-26">
        if 'dc.date.issued' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DC.DATE.MODIFIED" content="2012-01-13">
        if 'dc.date.modified' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta property="article:published_time"  content="2015-11-25" />
        if 'article:published_time' == metaProperty:
            metaDate = meta['content'].strip()
            break
            
        #<meta name="revison" content="Wed, 18 Sep 2013">
        if 'revision' == metaName:
            metaDate = meta['content'].strip()
            break
        
        #<meta name="update-date" content="2012-01-13">
        if 'update-date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
        if 'bt:pubdate' == metaProperty:
            metaDate = meta['content'].strip()
            break
        
        #<meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
        if 'sailthru.date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article.published" content="2015-11-26T11:53:00.000Z" />
        if 'article.published' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="published-date" content="2015-11-26T11:53:00.000Z" />
        if 'published-date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article.created" content="2015-11-26T11:53:00.000Z" />
        if 'article.created' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
        if 'article_date_original' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
        if 'cxenseparse:recs:publishtime' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
        if 'date_published' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        if 'datepublished' == itemProp:
            metaDate = meta['content'].strip()
            break

        #<meta property="og:image" content="http://www.dailytimes.com.pk/digital_images/400/2015-11-26/norway-return-number-of-asylum-seekers-to-pakistan-1448538771-7363.jpg"/>
        # if 'og:image' == metaProperty or "image" == itemProp:
        #     url = meta['content'].strip()
        #     possibleDate = _extractFromURL(url)
        #     if possibleDate is not None:
        #         return  possibleDate

        #<meta http-equiv="last-modified" content="10:27:15 AM Thursday, November 26, 2015">
        if 'last-modified' == httpEquiv:
            metaDate = meta['content'].strip()
            break
        
        #<meta content="2015-10-17T14:02:05Z" data-page-subject="true" property="og:article:published_time">
        if 'og:article:published_time' == metaProperty:
            metaDate = meta['content'].strip()
            break

        #<meta content="2016-01-14T21:58:23Z" data-page-subject="true" property="og:article:modified_time">
        if 'og:article:modified_time' == metaProperty:
            metaDate = meta['content'].strip()
            break

        #<meta name="Date" content="2015-11-26" />
        if 'date' == metaName:
            metaDate = meta['content'].strip()
            continue
        
        #<meta name="DC.DATE.CREATION" content="2008-12-29">
        if 'dc.date.creation' == metaName:
            metaDate = meta['content'].strip()
            continue

        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        if 'datecreated' == itemProp:
            metaDate = meta['content'].strip()
            continue

        #<meta http-equiv="date" content="10:27:15 AM Thursday, November 26, 2015">
        if 'date' == httpEquiv:
            metaDate = meta['content'].strip()
            continue

    if metaDate is not None:
        return parseStrDate(metaDate)

    return None

def _extractFromHTMLTag(parsedHTML, rDate = None):
    print "extractHTMLTag"

    date_re_str_1   = '('+regexStrings.get('year','')+')(?:[\-\/\.\s]\s?)('+regexStrings.get('month','')+'|'+regexStrings.get('month_string_de','')+'|'+regexStrings.get('month_string','')+')(?:[\-\/\.\s]\s?)('+regexStrings.get('day','')+')';
    date_re_str_2   = '('+regexStrings.get('day','')+')(?:[\-\/\.\s]\s?)('+regexStrings.get('month','')+'|'+regexStrings.get('month_string_de','')+'|'+regexStrings.get('month_string','')+')(?:[\-\/\.\s]\s?)('+regexStrings.get('year','')+')';
    date_re_str_3   = '('+regexStrings.get('day','')+')(?:[\-\/\.\s]\s?)('+regexStrings.get('month','')+'|'+regexStrings.get('month_string_de','')+'|'+regexStrings.get('month_string','')+')(?:[\-\/\.\s]\s?)('+regexStrings.get('hour','')+'):('+regexStrings.get('minute')+')';
    #<time>
    # for time in parsedHTML.findAll("time"):
    #     datetime = time.get('datetime', '')
    #     #print datetime
    #     if len(datetime) > 0:
    #         return parseStrDate(datetime)

    #     datetime = time.get('class', '')
    #     #print datetime
    #     if len(datetime) > 0 and datetime[0].lower() == "timestamp":
    #         return parseStrDate(time.string)


    tag = parsedHTML.find("span", {"itemprop": "datePublished"})
    if tag is not None:
        dateText = tag.get("content")

        if dateText is None:
            dateText = tag.text
        #print dateText
        if dateText is not None:
            return parseStrDate(dateText, rDate)

    #class=
    for tag in parsedHTML.find_all(['span', 'p','div'], class_=re.compile("date_published|pubdate|published_date|published-date|article_date|articledate|article-date",re.IGNORECASE)):
        dateText = tag.string
        if dateText is None:
            dateText = tag.text
        
        #Removing whitespace in the text
        dateText = re.sub("\s+"," ",dateText)
        dateText = dateText.lower()
        #print dateText
        m = re.search(date_re_str_2 + '|' + date_re_str_1, dateText)
        if m:
            #print m.group(0)
            return parseStrDate(m.group(0), rDate)
        
        possibleDate = parseStrDate(dateText, rDate)

        if possibleDate is not None:
            return  possibleDate

    
    #print date_re_str_2

    for tag in parsedHTML.find_all(['span','p','div'], class_=re.compile("footer",re.IGNORECASE)):
        footerText = tag.string
        if footerText is None:
            footerText = tag.text
        #print footerText
        m = re.search(date_re_str_2 + '|' + date_re_str_1, footerText)
        if m:
            #print m.group(0)
            return parseStrDate(m.group(0), rDate)
    
    for tag in parsedHTML.find_all(['footer']):
        footerText = tag.string
        if footerText is None:
            footerText = tag.text
        #print footerText
        m = re.search(date_re_str_2 + '|' + date_re_str_1, footerText)
        if m:
            #print m.group(0)
            return parseStrDate(m.group(0), rDate)
    
    #Removing script and style tag contents
    [s.extract() for s in parsedHTML(['style', 'script', '[document]', 'head', 'title'])]
    bodyText = parsedHTML.getText()
    
    #Removing whitespace in the text
    bodyText = re.sub("\s+"," ",bodyText)
    bodyText = bodyText.lower()
    #print "bodytext"
    #Extracting text following last update (in German)
    m = re.search(u'(?<=letzte änderung)\s*.*|(?<=geändert am)\s*.*|(?<=letzte aktualisierung)\s*.*|(?<=verändert am)\s*.*|(?<=zuletzt aktualisiert am)\s*.*', bodyText)
    if m:
        lastUpdateText = m.group(0)
        lastUpdateText = lastUpdateText.lower()
        print parseStrDate(lastUpdateText)
        date_match = re.search(date_re_str_3 + '|' + date_re_str_2 + '|' + date_re_str_1, lastUpdateText)
        if date_match:
            print date_match.group(0)
            return parseStrDate(date_match.group(0), rDate)

    #Extracting text following last update (in English)
    m = re.search(u'(?<=last change)\s*.*|(?<=updated on)\s*.*|(?<=last updated)\s*.*|(?<=modified on)\s*.*|(?<=last modified)\s*.*|(?<=updated)\s*.*|(?<=updated since)\s*.*|(?<=modified)\s*.*', bodyText)
    if m:
        lastUpdateText = m.group(0)
        lastUpdateText = lastUpdateText.lower()
        #print lastUpdateText
        date_match = re.search(date_re_str_2 + '|' + date_re_str_1, lastUpdateText)
        if date_match:
            #print date_match.group(0)
            return parseStrDate(date_match.group(0), rDate)

    #print parsedHTML.findAll('div',text=re.compile(r'(?<=Letzte Änderung:).*\s'))
    return None


def extractArticlePublishedDate(articleLink, html = None, rDate = None):

    #print "Extracting date from " + articleLink
    articleDate = None

    try:
        articleDate = _extractFromURL(articleLink)

        if html is None:
            request = urllib2.Request(articleLink)
            # Using a browser user agent, decreases the change of sites blocking this request - just a suggestion
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
            html = urllib2.build_opener().open(request).read()

        parsedHTML = BeautifulSoup(html,"html.parser")

        possibleDate = _extractFromLDJson(parsedHTML)
        if possibleDate is None:
            possibleDate = _extractFromMeta(parsedHTML)
        if possibleDate is None:
            possibleDate = _extractFromHTMLTag(parsedHTML, parseStrDate("20120803163259"))


        articleDate = possibleDate

    except Exception as e:
        #print "Exception in extractArticlePublishedDate for " + articleLink
        print e.message, e.args
        return None


    return articleDate




if __name__ == '__main__':
    #d = extractArticlePublishedDate("http://techcrunch.com/2015/11/30/atlassian-share-price/")
    #print d

    articleLink = sys.argv[1]
    articleHTML = None
    articleTimestamp = None

    if len(sys.argv) == 3:
        articleHTML = sys.argv[2]
        if articleHTML == "":
            articleHTML = None

    if len(sys.argv) == 4:
        articleHTML = sys.argv[2]
        articleTimestamp = parse(sys.argv[3])
        if articleHTML == "":
            articleHTML = None

    print extractArticlePublishedDate(articleLink, articleHTML)