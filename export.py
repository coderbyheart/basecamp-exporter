#!/usr/bin/env python3

#
# Exportiert ein Base-Camp-Projekt
#
# @author Markus Tacker <m@coderbyheart.de>
#

import sys
import httplib2
import json
import shutil
import os

class BasecampExporter(object):
    def __init__(self, account_id, username, password, target_folder = None, pretty_json=False):
        self.account_id = int(account_id)
        self.username = username
        self.password = password
        self.base_url = "https://basecamp.com/%d/api/v1/" % self.account_id
        self.target_folder = target_folder if target_folder != None else "."
        self.pretty_json = pretty_json
        
    def fetch(self, url, is_json = True):
        client = httplib2.Http()
        client.add_credentials(self.username, self.password)
        print("Fetching %s …" % url)
        resp, content = client.request(url, headers={'User-Agent': 'Gründerhub (http://gründerhub.de/)'})
        if (int(resp['status']) > 400):
            print("GET request failed: " + url)
            print(data)
            return None
        return json.loads(content.decode('utf-8')) if is_json else content
        
    def exportProject(self, project_id):
        print("Fetching project ...")
        url = self.base_url + "projects/%d.json" % int(project_id)
        project = self.fetch(url)
        # Export stuff
        self.exportAttachments(project["attachments"]['url'])
        self.exportByUrl(project["documents"]['url'], "documents")
        self.exportByUrl(project["topics"]['url'], "topics", lambda topic: topic["topicable"]["url"])
        self.exportByUrl(project["todolists"]['url'], "todolists")
    
    def exportAttachments(self, url):
        attachment_dir = self.target_folder + os.sep + "attachments" + os.sep
        if not os.path.isdir(attachment_dir):
            os.mkdir(attachment_dir)
        for attachment in self.fetch(url):
            data = self.fetch(attachment["url"], False)
            afile = attachment_dir + attachment["key"] + ".json"
            with open(attachment_dir + attachment["name"], 'wb') as a:
                a.write(data)          
                print(attachment_dir + attachment["name"])
            with open(afile, 'w') as a:
                a.write(json.dumps(attachment) if self.pretty_json is False else json.dumps(attachment, sort_keys=True, indent=4, separators=(',', ': ')))
                print(afile)
        
    def exportByUrl(self, url, what, getkey = lambda thing: thing['url']):
        export_dir = self.target_folder + os.sep + what + os.sep
        if not os.path.isdir(export_dir):
            os.mkdir(export_dir)
        for thing in self.fetch(url):
            data = self.fetch(getkey(thing))
            tfile = export_dir + str(data["id"]) + ".json"
            with open(tfile, 'w') as t:
                t.write(json.dumps(data) if self.pretty_json is False else json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
                print(tfile)
        

if __name__ == "__main__":
    
    if len(sys.argv) < 5:
        print("Usage: %s <account id> <project id> <username> <password> [target_folder]" % sys.argv[0])
        sys.exit()
        
    exporter = BasecampExporter(sys.argv[1], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) == 6 else None, pretty_json=True)
    exporter.exportProject(sys.argv[2])
