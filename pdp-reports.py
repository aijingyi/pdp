#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 - 2019 Wind River Systems, Inc.
# File  : pdp-reports.py
# Author: Kai Liang <Kai.Liang@windriver.com>
# Date  : 2019.12.25

# update : 2020.12.03 
# add lab requests, set blocker defects as first

from __future__ import division
import commands
import json
import urllib
import getpass
import os
import sys
import re
import time
import urllib
import urllib2
from optparse import OptionParser

class Env_Setup():
    def __init__(self):


        #get your linux username
        username = getpass.getuser()
        #username="zzhao1, kliang, wgao, xdong, lyang0, jhu2, rqu1, zwang7, sjiao, pyan, jkang, lwang4, lliu2, xhou, flian, zliu2, cxu"
        # report year
        year = time.strftime("%Y", time.localtime())

        parser = OptionParser()
        parser.add_option("-u", "--username", default=username,dest= "username", help="The unix name, such as kliang")
        parser.add_option("-l", "--link", default='yes',dest= "link", help="With jira link: yes. Without link: no")
        parser.add_option("-y", "--year", default=year,dest= "year", help="Report year")
        parser.add_option("-c", "--commit", default="yes",dest= "commit", help="Git commit summary, yes or on")
        #parser.add_option("-a", "--attach", default='',dest= "attach", help="The attach picture")
        #parser.add_option("-l", "--list", default='',dest= "list", help="The mail list")
        opts, args = parser.parse_args(sys.argv[1:])


        self.username = opts.username
        self.link = opts.link
        self.report_year = opts.year
        self.commit = opts.commit

        name_dic = {"zzhao1":"Zhenfeng Zhao", "kliang":"Kai Liang\|Kai.Liang", "wgao":"Wei Gao", "xdong":"xdong\|Xiangyu Dong", "lyang0":"Lei Yang", "jhu2":"Jianwei Hu", "rqu1":"Renfei.Qu", "zwang7":"Zhe Wang", "sjiao":"sjiao|Shilong.Jiao|Shilong Jiao", "pyan":"Peng Yan", "jkang":"Jian Kang", "lwang4":"Li Wang", "lliu2":"Le Liu", "xhou":"Xinlong Hou", "flian":"Fangfang Lian", "zliu2":"Zeming Liu", "cxu":"Chi Xu"}

        self.fullname = name_dic[self.username]

        self.current_dir = os.getcwd()
        self.filename = "%s/pdp_reports_%s_%s.txt" %(self.current_dir, self.username, self.report_year )
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def write_txt(self,txt):
        with open(self.filename,"a+") as f:
            f.write(txt)

class Defects_Top():

    def __init__(self, username,year):

        self.url = "https://jira.wrs.com/rest/api/2/search?maxResults=500&jql=" 
        self.jira_browse = "https://jira.wrs.com/browse/"
        self.year = year
        self.username = username
        self.filename = env.filename

        self.project = '"LINCD","LIN1019","LIN1018", "LIN10", "LIN9","LIN8","LIN7",\
"LIN6", "LINPUL8", "LINPULLT17","OVP6", "OVP7","OVP8", "OVP9", "CGP5", "CGP6",\
 "CGP7", "CGP8", "CGP9", "SCP6","SCP7", "SCP8", "SCP9", "IDP3"'
	self.lab_project = "LABOPS"

        self.create_time = 'created  >= "%s/01/01" AND created <= "%s/12/31"' % (self.year, self.year)
        self.update_time = ' "Closed Date" >= "%s/01/01" AND  "Closed Date" <= "%s/12/31"' % (self.year, self.year)
        self.jql_all = 'project in (%s)  AND reporter in (%s)  AND %s' %(self.project,self.username,self.create_time)
        self.jql_lab = 'project in (%s)  AND reporter in (%s)  AND %s' %(self.lab_project,self.username,self.create_time)
        self.jql_test_blocking = 'project in (%s)  AND reporter in (%s)  AND %s AND labels = TEST_BLOCKING' %(self.project,self.username,self.create_time)

        self.jql_valid = '''project in (%s)  AND reporter in (%s)  AND %s AND status in (Resolved, Closed, "Checked In") AND resolution in (Fixed, "Won't Fix")''' %(self.project, self.username, self.create_time)
        self.jql_valid_all = 'project in (%s)  AND reporter in (%s)  AND %s AND status in (Resolved, Closed, "Checked In")' %(self.project, self.username,self.create_time)

        #self.jql_verified = 'project in (LIN8, CGP8, SCP8, OVP8, "Linux Pulsar 8", "IDP 3.x", "Linux 10.17", "Linux 10.18","LIN1019")  AND tester in (%s)  AND %s' % (self.username, self.create_time)
        self.jql_verified = 'project in (%s)  AND (tester in (%s) OR ( (reporter in (%s) AND labels not in (Verified, verified) ) )) AND status = Closed AND %s' % (self.project, self.username, self.username, self.create_time)
       
   
    def curl_to_jira(self,jql):
        jql_code = urllib.quote(jql)
        url_data = self.url + jql_code

        curl_data = 'curl -sb -H "Content-Type: application/json" -u apiuser:apiuser -X GET "%s"' % url_data
        out = commands.getoutput(curl_data)
        out = json.loads(out)
        defects_name = ""
        for issue in  out["issues"]:
            if env.link == "yes":
                defects_name = defects_name + "  " +  self.jira_browse + issue["key"] + "\n"
            else:
                defects_name = defects_name + "  " + issue["key"] + "\n"
        num = out["total"]
    
        return num, defects_name

    def write_txt(self,txt):
        with open(self.filename,"a+") as f:
            f.write(txt)
        
    def all_defects(self):

        # All defects
        num, defects_name = self.curl_to_jira(self.jql_all)
        self.write_txt("\n3. Submitted defects list.\n")
        all_nums = "\n  Numbers of all submitted defects: %s\n" % num
        self.write_txt(all_nums)
        #self.write_txt(defects_name)


    def defects_with_p(self):

        #Defects with P1, P2, P3, P4:
        for p in ["P1","P2","P3","P4"]:
            self.jql_p = 'project in (%s)  AND reporter in (%s)  AND Priority = %s AND %s' % (self.project,self.username, p, self.create_time)
            #print self.jql_p
            num, defects_name = self.curl_to_jira(self.jql_p)
            num_txt =  "\n  Numbers of defects with %s: %s\n" % (p,num)
            self.write_txt("%s" % num_txt)
            self.write_txt("%s" % defects_name)
        
    def defects_valid_ratio(self):

        #Defect Valid Ratio
        valid_num, defects_name_valid = self.curl_to_jira(self.jql_valid)
        valid_all_num, defects_name_invalid = self.curl_to_jira(self.jql_valid_all)
        self.write_txt(("\n  Numbers of valid defects: %s\n  Numbers of valid and invalid defects: %s\n") %(valid_num, valid_all_num))
        valid_ratio = valid_num / valid_all_num
        self.write_txt('  Valid Ratio of defects = {:.2%}\n'.format(valid_ratio))

    def lab_defects(self):

        # All defects
        num, defects_name = self.curl_to_jira(self.jql_lab)
        self.write_txt("\n4. Submitted lab request list.\n")
        lab_nums = "\n  Numbers of all submitted reqeusts: %s\n" % num
        self.write_txt(lab_nums)
        self.write_txt(defects_name)
    
    def defects_verified(self):

        #Defects Verified 
        verified_num, defects_verified = self.curl_to_jira(self.jql_verified)
        verified_txt = "\n5. Verified defects list.\n\n  Numbers: %s\n" % verified_num
        self.write_txt(verified_txt)
        self.write_txt("%s" % defects_verified)

    def defects_test_blocking(self):

        #Defects with test blocking
        blocking_num, blocking_defects = self.curl_to_jira(self.jql_test_blocking)
        blocking_txt = "\n  Numbers of TEST_BLOCKING defects: %s\n" % blocking_num
        self.write_txt(blocking_txt)
        self.write_txt("%s" % blocking_defects)


    def main(self):

        print("Your defects list are creating.")
        print("Please wait ..........")
        self.all_defects()
        self.defects_valid_ratio()
        self.defects_test_blocking()
        self.defects_with_p()
	self.lab_defects()
        self.defects_verified()        
        print("Your defects list are created successfully.")


class Commit_Reports():

    def __init__(self, fullname,username, year):
        # test layer for master 
        self.link = "/lpg-build/cdc/WASSP_LINUX_MASTER_WR/testcases/wrlinux/"
        self.username = username
        self.fullname = fullname
        self.year = year


    def git_log(self):
        print("Your test cases commits are creating.")
        print("Please wait ..........")
        cd_git = os.chdir(self.link)
        git_cmd = 'git log --no-merges --before={%s-12-31} --after={%s-01-01} --author="%s" --pretty=format:"%%H"' % (self.year, self.year, self.fullname)
        get_commits = commands.getoutput(git_cmd).split() 

        add_cases = ""
        rca_add_cases = ""
        update_cases = ""
        rca_update_cases = ""
        other_cases = ""
        add_nums = 0
        rca_add_nums = 0
        update_nums = 0
        rca_update_nums = 0
        other_nums = 0
        for co in get_commits:
            commit_link = "http://lxgit.wrs.com/cgit/wrlinux-testing/testcases.git/commit/?id=%s" % co
            show_cmd = "git show %s -s --format=%%s" % co
            get_show = commands.getoutput(show_cmd)
            #print(get_show)
            if re.search("test results for|testresults for|test-plan|testplan|test plan|test report|testing report", get_show):
                other_nums += 1
                if env.commit == "no":
                    other_cases = other_cases  + "  " + commit_link + "\n"
                else:
                    other_cases = other_cases + "  " + get_show + "\n  " + commit_link + "\n"
            elif get_show.startswith("Add") or get_show.startswith("add") or get_show.startswith("Added"):
                if "RCA" in get_show:
                    rca_add_nums += 1
                    if env.commit == "no":
                        rca_add_cases = rca_add_cases + "  " + commit_link + "\n"
                    else:
                        rca_add_cases = rca_add_cases + "  " +  get_show + "\n  " + commit_link + "\n"
                else:
                    add_nums += 1
                    if env.commit == "no":
                        add_cases = add_cases + "  " + commit_link + "\n"
                    else:
                        add_cases = add_cases + "  " + get_show + "\n  " + commit_link + "\n"
                    #add_cases = add_cases + get_show + "\n" 
            elif get_show.startswith("Update") or get_show.startswith("update"):
                if "RCA" in get_show:
                    rca_update_nums += 1
                    if env.commit == "no":
                        rca_update_cases = rca_update_cases + "  "  + commit_link + "\n"
                    else:
                        rca_update_cases = rca_update_cases + "  " + get_show + "\n  " + commit_link + "\n"
                else:
                    update_nums += 1
                    if env.commit == "no":
                        update_cases = update_cases + "  "  + commit_link + "\n"
                    else:
                        update_cases = update_cases + "  " + get_show + "\n  " + commit_link + "\n"
                    #update_cases = update_cases + get_show + "\n" 
            else:
                other_nums += 1
                if env.commit == "no":
                    other_cases = other_cases + "  " + commit_link + "\n"
                else:
                    other_cases = other_cases + "  " + get_show + "\n  " + commit_link + "\n"
        env.write_txt("1. New test cases commits.\n\n  Numbers:%s\n" % add_nums)
        env.write_txt(add_cases)
        if rca_add_nums:
            env.write_txt("\n  RCA add test cases commits.\n\n  Numbers:%s\n" % rca_add_nums)
            env.write_txt(rca_add_cases)
        env.write_txt("\n2. Update test cases commits.\n\n  Numbers:%s\n" % update_nums)
        env.write_txt(update_cases)
        if rca_update_nums:
            env.write_txt("\n  RCA update test cases commits.\n\n  Numbers:%s\n" % rca_update_nums)
            env.write_txt(rca_update_cases)
        if other_nums:
            env.write_txt("\n  Other test commits.\n\n  Numbers:%s\n" % other_nums)
            env.write_txt(other_cases)
        print("Your test cases commits are created successfully.")
        #print(add_nums)
        #print(add_cases)
        #print(update_nums)
        #print(update_cases)
                
class User_Story():
    def __init__(self,username, report_year):
        self.year = report_year
        self.username = username    
        self.release = ["WRLinux 10.17.41.x", "WRLinux 10.18","WRLinux 10.19", "WRLinux CD Standard", "WRLinux CD Next"]
        #self.release = ["WRLinux 10.19", "WRLinux CD Standard", "WRLinux CD Next"]
        #print self.ltaf_link

    def get_html(self, ltaf_link):    
        html = urllib2.urlopen(ltaf_link.replace(" ", "%20")).read()
        #print html
        return html
    def get_us(self, html):
        reg = r'req_ids=\'(.*)\' name='
        usre = re.compile(reg)
        us = re.findall(usre, html)
        return us

    def get_summary(self,html):
        reg = r'requirement_summary\'>(.*?)</td><td id='
        summaryre = re.compile(reg)
        summary = re.findall(summaryre, html)
        return summary

    def get_trs(self,html):
        reg = r'><b>(.*?) TRs'
        trsre = re.compile(reg)
        trs = re.findall(trsre, html)
        return trs

    def get_result_trs(self,html):
        #reg = r'><b>(.*?) TRs'
        #trsre = re.compile(reg)
        #trs = re.findall(trsre, html)
        if "There are no test runs for this selection" in html:
            total = 0
        else:
            total = html.split()[2]
        return total
    
    def get_all(self, release):
        
        ltaf_link = "http://pek-lpgtest3.wrs.com/ltaf/requirement.php?releasename=%s&clearfilter=true&tf_requirement_tester=%s&tf_requirement_show_tr=on&tf_per_page=50" % (release, self.username)
        html = self.get_html(ltaf_link)
        us = self.get_us(html)
        summary = self.get_summary(html)
        trs = self.get_trs(html)
        release_txt = ""
        trs_num = 0
        for n in range(len(us)):
            result_link = "http://pek-lpgtest3.wrs.com/ltaf/test_results.php?releasename=%s&clearfilter=true&tf_tr_show_latest=on&tf_tr_requirement=%s&extra_q_in=SKIP_WNR&tf_tr_start_date=%s-01-01&op_show_type=summary" % (release,us[n], self.year)
            result_link_all = "http://pek-lpgtest3.wrs.com/ltaf/test_results.php?releasename=%s&clearfilter=true&tf_tr_show_latest=on&tf_tr_requirement=%s&extra_q_in=SKIP_WNR&tf_tr_start_date=%s-01-01" % (release,us[n], self.year)
            re_html = self.get_html(result_link)
            trs_one = self.get_result_trs(re_html)
            if trs_one:
                #env.write_txt("  User Story: %s\n" % us[n])
                us_txt = "  User Story: %s\n" % us[n]
                sum_txt = "  Summary: %s\n" % summary[n]
                #env.write_txt("  LTAF result link: %s\n" % result_link_all)
                results_txt = "  LTAF result link: %s\n" % result_link_all.replace(" ", "%20")
                trs_txt = "  Test result runs: %s\n\n" % trs_one
                release_txt = release_txt + us_txt + sum_txt + results_txt + trs_txt
                trs_num = trs_num + int(trs_one)
        if trs_num:
            env.write_txt("\n  Release: %s\n\n" % release)
            env.write_txt(release_txt)
        return trs_num

    def ltaf_main(self):
        print("Your user story are creating.")
        print("Please wait ..........")
        env.write_txt("\n6. Test run list\n")
        trs_all = 0
        for r in self.release:
            trs_all = trs_all + int(self.get_all(r))
        env.write_txt("  All the test runs: %s\n" % trs_all)
        print("Your user story are created successfully.")


class Jira_Project():
    def __init__(self):
        self.url = "https://jira.wrs.com/rest/api/2/search?maxResults=500&jql=" 
        self.jira_browse = "https://jira.wrs.com/browse/"
        self.year = env.report_year
        self.username = env.username
        
        self.create_time = 'created  >= "%s/01/01" AND created <= "%s/12/31"' % (self.year, self.year)
        self.jql_all = 'assignee = %s  AND status in ("To Do", "In progress","Done") AND project = "Linux Execution Project" AND %s ORDER BY created DESC' %(self.username, self.create_time)
        
    def curl_to_jira(self,jql):
        jql_code = urllib.quote(jql)
        url_data = self.url + jql_code

        curl_data = 'curl -sb -H "Content-Type: application/json" -u apiuser:apiuser -X GET "%s"' % url_data
        out = commands.getoutput(curl_data)
        out = json.loads(out)
        defects_dic = {}
        defects_name = ""
        
        #print(out["issues"])
        for issue in  out["issues"]:
            #defects_name = defects_name + self.jira_browse + issue["key"] + "\n"
            #print(issue["fields"]["summary"])
            #if "parent" in issue["fields"]:
            #   print(issue["fields"]["summary"])
            #print(list(issue["fields"]["parent"].keys()))
            if "on xxx QEMU BSPs" in issue["fields"]["summary"]:
                continue
            issue_txt = issue["fields"]["summary"]
            if "in Week" in issue_txt or "on Week" in issue_txt:
                defects_dic[issue["fields"]["parent"]["key"]] = issue["fields"]["parent"]["fields"]["summary"]
            else:
                defects_dic[issue["key"]] = issue["fields"]["summary"]
        for key in defects_dic:
            defects_name = defects_name + "  " + key + "  " + defects_dic[key] + "\n"
        num = out["total"]
    
        return num, defects_name

    def jira_main(self):
        num, defects_name = self.curl_to_jira(self.jql_all)
        env.write_txt("\n7.Feature User Story lists:\n\n")
        env.write_txt("  %s User Story\n" % num)
        env.write_txt(defects_name)


if __name__ == "__main__":

    env = Env_Setup()

    mygit = Commit_Reports(env.fullname, env.username, env.report_year)
    mygit.git_log()

    mydefect = Defects_Top(env.username, env.report_year)
    mydefect.main()
    myus = User_Story(env.username, env.report_year)
    myus.ltaf_main()

    myjp = Jira_Project()
    myjp.jira_main()
