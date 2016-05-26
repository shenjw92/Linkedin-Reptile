import requests
import re
import json
from bs4 import BeautifulSoup, Comment

def login(s):
    r = s.get('https://www.linkedin.com/uas/login')
    soup = BeautifulSoup(r.text, "lxml")
    soup = soup.find(id="login")
    loginCsrfParam = soup.find('input', id = 'loginCsrfParam-login')['value']
    csrfToken = soup.find('input', id = 'csrfToken-login')['value']
    sourceAlias = soup.find('input', id = 'sourceAlias-login')['value']
    isJsEnabled = soup.find('input',attrs={"name" :'isJsEnabled'})['value']
    source_app = soup.find('input', attrs={"name" :'source_app'})['value']
    tryCount = soup.find('input', id = 'tryCount')['value']
    clickedSuggestion = soup.find('input', id = 'clickedSuggestion')['value']
    signin = soup.find('input', attrs={"name" :'signin'})['value']
    session_redirect = soup.find('input', attrs={"name" :'session_redirect'})['value']
    trk = soup.find('input', attrs={"name" :'trk'})['value']
    fromEmail = soup.find('input', attrs={"name" :'fromEmail'})['value']

    payload = {
        'isJsEnabled':isJsEnabled,
        'source_app':source_app,
        'tryCount':tryCount,
        'clickedSuggestion':clickedSuggestion,
        'session_key':'*********',
        'session_password':'*********',
        'signin':signin,
        'session_redirect':session_redirect,
        'trk':trk,
        'loginCsrfParam':loginCsrfParam,
        'fromEmail':fromEmail,
        'csrfToken':csrfToken,
        'sourceAlias':sourceAlias
    }

    s.post('https://www.linkedin.com/uas/login-submit', data=payload)
    return s

def getCompanins(s, start_url):
    r= s.get(start_url)

    html = r.text.encode("utf-8")
    code = re.search(r'<code id="voltron_srp_main-content" style="display:none;"><!--.+--></code>', html).group()
    code = code.replace(r'<code id="voltron_srp_main-content" style="display:none;"><!--', '')
    code = code.replace(r'--></code>', '')

    code_json = json.loads(code)
    company_json = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["results"]
    company_list = []
    for company in company_json:
        company = company["company"]
        name = company["fmt_canonicalName"]
        fmt_industry = company["fmt_industry"]
        fmt_size= company["fmt_size"]
        fmt_location= company["fmt_location"]
        company_list.append("%s\t%s\t%s\t%s\n" % (name, fmt_industry, fmt_size, fmt_location))
    return company_list

def getCompanins(code_json):
    company_json = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["results"]

    company_list = []
    for company in company_json:
        company = company["company"]
        name = company["fmt_canonicalName"]
        fmt_industry = company["fmt_industry"]
        fmt_size= company["fmt_size"]
        fmt_location= company["fmt_location"]
        company_list.append("%s\t%s\t%s\t%s\n" % (name, fmt_industry, fmt_size, fmt_location))
    return company_list

def getNextPageURL(s ,start_url):
    r= s.get(start_url)

    html = r.text.encode("utf-8")
    code = re.search(r'<code id="voltron_srp_main-content" style="display:none;"><!--.+--></code>', html).group()
    code = code.replace(r'<code id="voltron_srp_main-content" style="display:none;"><!--', '')
    code = code.replace(r'--></code>', '')

    code_json = json.loads(code)
    resultPagination = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["baseData"]["resultPagination"]
    if "nextPage" in resultPagination:
        nextPageURL = "http://www.linkedin.com/" + resultPagination["nextPage"]["pageURL"]
    else:
        nextPageURL = "NULL"

    return nextPageURL

def getNextPageURL(code_json):
    resultPagination = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["baseData"]["resultPagination"]
    if "nextPage" in resultPagination:
        nextPageURL = "http://www.linkedin.com/" + resultPagination["nextPage"]["pageURL"]
    else:
        nextPageURL = "NULL"

    return nextPageURL

def search(s ,start_url):
    with open("result", "wb") as of:
        while True:
            if start_url == "NULL":
                break
            r= s.get(start_url)
            print r
            html = r.text.encode("utf-8")
            code = re.search(r'<code id="voltron_srp_main-content" style="display:none;"><!--.+--></code>', html).group()
            code = code.replace(r'<code id="voltron_srp_main-content" style="display:none;"><!--', '')
            code = code.replace(r'--></code>', '')
            code_json = json.loads(code)
            start_url = getNextPageURL(code_json)
            company_list = getCompanins(code_json)
            for line in company_list:
                of.write(line)

if __name__ == '__main__':
    s = requests.session()
    s = login(s)
    start_url = "http://bit.ly/27SYIKd"
    search(s ,start_url)
